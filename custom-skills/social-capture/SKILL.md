---
name: social-capture
description: "Use this skill when the user shares ANY URL or link in chat — from YouTube, TikTok, X/Twitter, Facebook, LinkedIn, Instagram, Pinterest, or any website. Auto-detects platform, extracts content metadata (title, description, tags), and saves to knowledge warehouse. Also handles 'save this link', 'bookmark this', 'save for later'. No command needed — just paste a URL."
user_invocable: true
---

# Universal Social Capture

Zero-friction knowledge capture from any URL. Share a link → auto-save with AI tagging.

## Usage

```bash
python3 social_capture.py save --user <user_id> --url <url>
python3 social_capture.py recent --user <user_id>
python3 social_capture.py stats --user <user_id>
python3 social_capture.py search --user <user_id> --query <search_term>
```

### Actions

**save** — Save a URL with auto-detected metadata
```bash
python3 social_capture.py save --user ted --url "https://www.youtube.com/watch?v=abc123" --note "great cooking tip"
```

**recent** — Show recently saved items
```bash
python3 social_capture.py recent --user ted --count 10
```

**stats** — Show knowledge warehouse stats by topic
```bash
python3 social_capture.py stats --user ted
```

**search** — Search saved items
```bash
python3 social_capture.py search --user ted --query "cooking recipe"
```

### Platform Detection
- YouTube → extracts video title, channel, description
- TikTok → extracts caption, creator, hashtags
- X/Twitter → extracts tweet text, author
- Facebook → extracts post title, description
- LinkedIn → extracts article title, summary
- Instagram → extracts caption, hashtags
- Pinterest → extracts pin description
- Reddit → extracts post title, subreddit
- Any website → extracts page title, meta description

## Agent Behavior
When user sends a message containing a URL (no command needed):
1. Detect the URL in the message
2. Run `save` with the URL and any user note
3. Reply: "Saved! [Platform] — [Title]. Tagged: #tag1 #tag2. You now have X items about [topic]."

When user says "what did I save recently" or "show my bookmarks":
1. Run `recent` to show last 10 items
