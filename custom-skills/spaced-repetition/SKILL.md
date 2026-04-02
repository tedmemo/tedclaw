---
name: spaced-repetition
description: "Use this skill for flashcard quizzes, spaced repetition learning, and knowledge review. Handles 'quiz me', 'start a quiz', 'add flashcard', 'show my cards', 'how many cards due'. Uses SM-2 algorithm for optimal review intervals. Supports IT, Health, and Wealth learning tracks."
user_invocable: true
---

# Spaced Repetition (Flashcard Quizzes)

Quiz system using SM-2 algorithm for optimal memory retention. Cards are reviewed at increasing intervals based on recall quality.

## Usage

```bash
python3 spaced_repetition.py <action> --user <user_id> [options]
```

### Actions

**add** — Add a new flashcard
```bash
python3 spaced_repetition.py add --user ted --front "What is haversine?" --back "Formula to calculate distance between two GPS coordinates on a sphere" --track it
```

**quiz** — Start a quiz with due cards
```bash
python3 spaced_repetition.py quiz --user ted
```

**answer** — Record answer quality (1-5 scale)
```bash
python3 spaced_repetition.py answer --user ted --card-id abc123 --quality 4
```

**stats** — Show learning statistics
```bash
python3 spaced_repetition.py stats --user ted
```

**due** — Show how many cards are due for review
```bash
python3 spaced_repetition.py due --user ted
```

### Quality Scale (for answers)
- 1: Complete blackout, no recall
- 2: Wrong answer, but recognized correct one
- 3: Correct with significant difficulty
- 4: Correct with some hesitation
- 5: Perfect, instant recall

## Agent Behavior
When user says "quiz me" or "start a quiz":
1. Run `quiz` to get the next due card
2. Show only the front (question)
3. Wait for user's answer
4. Show the back (correct answer)
5. Ask user to rate recall (1-5)
6. Run `answer` with the rating
7. Continue with next card or end if none due
