# ACPX Integration Analysis — ACP Client (Provider) Mode

## Context

GoClaw hiện đã có mô hình provider linh hoạt cho LLM backends (Anthropic native, OpenAI-compat, ClaudeCLI subprocess, Codex OAuth). Yêu cầu là phân tích khả năng tích hợp **ACP (Agent Client Protocol)** — một JSON-RPC 2.0 protocol chuẩn cho AI coding agents — để GoClaw có thể sử dụng bất kỳ ACP-compatible agent nào (Claude Code, Codex CLI, Gemini CLI, Goose, etc.) làm provider.

Tham khảo:
- [ACPX CLI](https://github.com/openclaw/acpx) — headless ACP client
- [OpenClaw](https://github.com/openclaw/openclaw) — dự án tương tự GoClaw, có adapter cho ACPX
- [ACP Spec](https://agentclientprotocol.com/protocol/schema) — protocol specification

## Hiện trạng GoClaw — Các điểm mở rộng phù hợp

### 1. Provider Interface (`internal/providers/types.go`)
```go
type Provider interface {
    Chat(ctx context.Context, req ChatRequest) (*ChatResponse, error)
    ChatStream(ctx context.Context, req ChatRequest, onChunk func(StreamChunk)) (*ChatResponse, error)
    DefaultModel() string
    Name() string
}
```
- Đây là interface chính cần implement cho `ACPProvider`
- `ChatRequest` chứa Messages, Tools, Model, Options
- `ChatResponse` chứa Content, Thinking, ToolCalls, FinishReason, Usage

### 2. ClaudeCLI Provider — Precedent trực tiếp (`internal/providers/claude_cli*.go`)
Đây là mô hình gần nhất với ACP Provider:
- Spawn subprocess (`exec.CommandContext`)
- Communicate qua stdin/stdout
- Per-session mutex (`sessionMu sync.Map`)
- Session persistence qua session ID mapping (`deriveSessionUUID`)
- Stream parsing từ NDJSON output
- Workspace management (`ensureWorkDir`, `writeClaudeMD`)
- MCP config injection

### 3. Provider Registration (`cmd/gateway_providers.go`)
- Config-based: `registerProviders()` đọc từ `config.Config`
- DB-based: `registerProvidersFromDB()` đọc từ `llm_providers` table
- Cả hai đều gọi `registry.Register(provider)`

### 4. Agent Loop (`internal/agent/loop*.go`)
- `RunRequest` → provider.ChatStream() → parse response → tool execution → loop
- Provider chỉ cần implement `Chat/ChatStream` — agent loop handles tool execution
- Quan trọng: GoClaw agent loop **tự quản lý tools** — provider chỉ cần trả ToolCalls

## ACP Protocol — Tóm tắt kỹ thuật

### Transport
- JSON-RPC 2.0 over **stdin/stdout** (subprocess model)
- Bidirectional: cả agent và client có thể initiate requests

### Lifecycle
```
Client                          Agent (subprocess)
  |-- initialize ----------------->|  (capability negotiation)
  |<-- initialize response --------|
  |-- session/new ----------------->|  (create session)
  |<-- session/new response --------|  (returns sessionId)
  |-- session/prompt -------------->|  (send user message)
  |<-- session/update (notification)|  (streaming content/tools)
  |<-- session/update (notification)|  ...
  |<-- session/prompt response -----|  (done, stopReason)
```

### Key Methods
| Method | Direction | Purpose |
|--------|-----------|---------|
| `initialize` | Client→Agent | Capability negotiation, protocol version |
| `session/new` | Client→Agent | Create new session with workdir, MCP config |
| `session/load` | Client→Agent | Resume existing session by ID |
| `session/prompt` | Client→Agent | Send user message (text/image/audio) |
| `session/update` | Agent→Client (notification) | Stream content blocks, tool calls |
| `session/cancel` | Client→Agent | Cooperative cancellation |
| `session/request_permission` | Agent→Client | Ask for tool execution permission |

### Content Model (từ ACPX types)
```
Agent Content: Text | Thinking | RedactedThinking | ToolUse
User Content: Text | Image | Mention
Tool Result: { tool_use_id, tool_name, is_error, content }
```

## Thiết kế ACPProvider

### Architecture Overview

```
GoClaw Agent Loop
    ↓ ChatStream(req)
ACPProvider
    ↓ spawn ACP subprocess (if not running)
    ↓ initialize (once per process)
    ↓ session/new or session/load
    ↓ session/prompt (with translated messages)
    ↓ read session/update notifications → StreamChunk callbacks
    ↓ return ChatResponse
ACP Agent Process (claude, codex, gemini, goose, etc.)
```

### So sánh với ClaudeCLI Provider

| Aspect | ClaudeCLI | ACPProvider (proposed) |
|--------|-----------|----------------------|
| Process lifecycle | Per-request (spawn & wait) | **Persistent** (long-running subprocess) |
| Protocol | CLI flags + stream-json output | JSON-RPC 2.0 bidirectional |
| Session management | CLI `--session-id/--resume` | ACP `session/new` / `session/load` |
| Tool execution | CLI handles tools internally | **Two modes** (see below) |
| Streaming | NDJSON lines on stdout | JSON-RPC notifications (`session/update`) |
| System prompt | Write CLAUDE.md file | Pass in `session/new` or `session/prompt` |

### Tool Execution — Hai chế độ

**Mode A: Agent-managed tools (đơn giản hơn, khuyến nghị cho MVP)**
- ACP agent tự execute tools (file read/write, terminal, etc.)
- GoClaw chỉ forward text response — giống ClaudeCLI hiện tại
- Provider trả `ChatResponse{Content, Thinking}` — không có ToolCalls
- Agent loop không cần xử lý tool calls

**Mode B: GoClaw-managed tools (phức tạp hơn, tận dụng GoClaw tool ecosystem)**
- ACP agent trả `ToolUse` content blocks
- ACPProvider map sang `ChatResponse.ToolCalls`
- GoClaw agent loop execute tools → trả results qua `session/prompt` hoặc custom method
- Cho phép dùng GoClaw's MCP bridge, sandbox, memory, etc.

### Files cần tạo/sửa

#### Tạo mới:
1. **`internal/providers/acp.go`** — ACPProvider struct, NewACPProvider(), lifecycle management
2. **`internal/providers/acp_protocol.go`** — JSON-RPC message types, encode/decode
3. **`internal/providers/acp_session.go`** — Session management (initialize, new, load, prompt)
4. **`internal/providers/acp_stream.go`** — Stream parsing (session/update → StreamChunk)

#### Sửa đổi:
5. **`internal/config/config.go`** — Thêm `ACP` provider config section
6. **`cmd/gateway_providers.go`** — Register ACPProvider từ config + DB
7. **`internal/store/provider_types.go`** — Thêm `ProviderACP` constant
8. **`internal/store/pg/providers.go`** — Handle ACP provider type từ DB

### ACPProvider — Thiết kế chi tiết

```go
type ACPProvider struct {
    name         string
    command      string   // e.g. "claude", "codex", "gemini"
    args         []string // extra args for the ACP subprocess
    defaultModel string
    workDir      string   // base workspace directory

    // Process management
    mu       sync.Mutex
    proc     *acpProcess  // long-running subprocess
    procOnce sync.Once

    // Session management
    sessions sync.Map // sessionKey → acpSessionID

    // Permission policy
    permPolicy string // "approve-all", "approve-reads", "deny-all"
}

type acpProcess struct {
    cmd    *exec.Cmd
    stdin  io.WriteCloser
    stdout *bufio.Scanner

    // JSON-RPC state
    nextID   atomic.Int64
    pending  sync.Map // requestID → chan *jsonrpcResponse

    // Read loop runs in background goroutine
    done chan struct{}
}
```

### Luồng xử lý ChatStream

```
1. Ensure process running (spawn if needed)
2. Ensure session exists:
   - sessionKey → lookup in sessions map
   - If not found → session/new with workDir
   - If found → session/load (with fallback to session/new)
3. Build session/prompt request:
   - Convert ChatRequest.Messages → ACP content blocks
   - Include system prompt as context
4. Send session/prompt JSON-RPC request
5. Read loop dispatches:
   - session/update notifications → onChunk(StreamChunk{Content/Thinking})
   - session/prompt response → build ChatResponse, return
   - session/request_permission → auto-approve based on permPolicy
6. Return final ChatResponse
```

### Config Schema

```json5
{
  "providers": {
    "acp": {
      "command": "claude",           // ACP server binary
      "args": ["--acp"],             // extra args (some agents need --acp flag)
      "model": "sonnet",            // default model (passed to agent if supported)
      "workDir": "/home/user/work", // base workspace
      "permPolicy": "approve-all"   // auto-approve tool permissions
    }
  }
}
```

### DB Provider Type

```sql
-- In llm_providers table:
-- provider_type = 'acp'
-- api_base = command path (e.g. "/usr/local/bin/claude")
-- model = default model
-- other_config JSONB = { "args": ["--acp"], "permPolicy": "approve-all" }
```

## Thách thức kỹ thuật & Giải pháp

### 1. Persistent Process Management
- **Vấn đề:** ClaudeCLI spawn per-request; ACP cần long-running process
- **Giải pháp:** `acpProcess` struct với background read loop goroutine. Process respawn on crash (detect dead PID, restart, session/load fallback)

### 2. Bidirectional JSON-RPC
- **Vấn đề:** Agent có thể gửi requests TO client (session/request_permission)
- **Giải pháp:** Background read loop phân loại messages:
  - Responses (có `id` match pending request) → dispatch to waiting goroutine
  - Notifications (có `method`, không `id`) → route to handlers
  - Requests from agent (có `method` + `id`) → handle & respond

### 3. Session Mapping
- **Vấn đề:** GoClaw dùng composite session keys; ACP dùng session IDs
- **Giải pháp:** `sync.Map` mapping `sessionKey → acpSessionID`. Persist to disk/DB for crash recovery

### 4. Tool Execution Mode
- **Vấn đề:** ACP agents expect to execute tools themselves (file ops, terminal)
- **Giải pháp (MVP):** Mode A — let agent handle tools, GoClaw just receives final text. Đủ cho use case "dùng Claude Code/Codex qua ACP thay vì CLI-specific parsing"

### 5. Capability Negotiation
- **Vấn đề:** Mỗi agent support khác nhau (thinking, images, MCP)
- **Giải pháp:** Cache capabilities từ `initialize` response. Dùng để gate features (thinking support, image input, etc.)

## So sánh với OpenClaw

| Feature | OpenClaw | GoClaw (proposed) |
|---------|----------|-------------------|
| ACP usage | ACPX adapter trong agent registry | ACPProvider trong provider registry |
| Session model | Native session management | Map GoClaw session keys → ACP sessions |
| Tool handling | Agent-managed (Pi agent RPC) | Mode A: agent-managed (MVP) |
| Process model | Gateway manages agent processes | Provider manages subprocess |
| Protocol | Internal WS RPC + ACP bridge | Direct ACP JSON-RPC |

## Lợi ích

1. **Universal agent support:** Bất kỳ ACP-compatible agent → GoClaw provider
2. **Standardized protocol:** Không cần maintain CLI-specific parsers
3. **Future-proof:** ACP đang được adopt bởi Zed, Neovim, JetBrains, etc.
4. **Giảm coupling:** Không phụ thuộc vào output format cụ thể của từng CLI tool

## Rủi ro

1. **ACP still alpha:** Protocol có thể thay đổi
2. **Process management complexity:** Long-running subprocess cần crash recovery
3. **Tool mode confusion:** Agent-managed vs GoClaw-managed tools cần document rõ
4. **Testing:** Cần mock ACP server cho integration tests

## Kế hoạch triển khai (nếu proceed)

### Phase 1: MVP (Mode A — agent-managed tools)
1. Implement `acp_protocol.go` — JSON-RPC types
2. Implement `acp.go` — ACPProvider with subprocess management
3. Implement `acp_session.go` — initialize, session/new, session/prompt
4. Implement `acp_stream.go` — session/update parsing → StreamChunk
5. Wire up in config + gateway_providers.go
6. Test với Claude Code (`claude --acp` — nếu có ACP mode)

### Phase 2: Hardening
7. Crash recovery + process respawn
8. Session persistence (disk/DB)
9. Permission handling (session/request_permission)
10. Capability-based feature gating

### Phase 3: Advanced (Mode B — optional)
11. GoClaw-managed tool execution
12. MCP bridge integration
13. Sandbox support cho ACP agents

## Verification

Để test tích hợp:
```bash
# 1. Build
go build ./...

# 2. Chạy với ACP agent (ví dụ goose)
# Config:
# { "providers": { "acp": { "command": "goose", "args": ["--acp"] } } }

# 3. Test qua WS hoặc HTTP API
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "acp", "messages": [{"role": "user", "content": "hello"}]}'

# 4. Integration tests
go test -v ./tests/integration/ -run TestACP
```
