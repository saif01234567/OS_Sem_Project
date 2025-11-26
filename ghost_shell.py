#!/usr/bin/env python3
"""
Ghost Shell - enhanced educational mini shell
New features:
 - persistent history (~/.ghost_history)
 - builtins: cd, pwd, echo, history, exit, help, clear, whoami
 - logging to logs/ghost_log.txt
 - LLM integration placeholder (explain_with_llm)
 - clean structure for future piping/redirection
"""

import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROMPT = "Ghost$ "
HISTORY_FILE = Path.home() / ".ghost_history"
LOGS_DIR = Path("logs")
LOG_FILE = LOGS_DIR / "ghost_log.txt"
LLM_MODE = False   # Set True when you implement real API integration

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log_command(line):
    """Append timestamped command to log file."""
    ts = datetime.utcnow().isoformat(timespec='seconds') + "Z"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{line}\n")

def explain(cmd_name, kind, extra=""):
    """Return a short human-friendly explanation string."""
    if kind == 'builtin':
        return f"(👻) Built-in: shell handled `{cmd_name}` without creating a child process."
    if kind == 'external':
        return f"(👻) External: shell created a child process and used exec to run `{cmd_name}`."
    if kind == 'error':
        return f"(👻) Error: {extra}"
    return "(👻) Done."

def explain_with_llm(cmd_line, short_explanation):
    """
    Placeholder for LLM integration. When LLM_MODE = True, you'd call an LLM API here,
    sending cmd_line and short_explanation, and return the model's expanded explanation.
    For safety & privacy, this function currently returns the short_explanation.
    To integrate a real LLM:
      - implement an API call here (requests or openai library)
      - load API key from an env var or config file (never hardcode keys)
    """
    if not LLM_MODE:
        return short_explanation
    # Example pseudo-code:
    # response = call_llm_api(prompt=f"Explain: {cmd_line}\nShort: {short_explanation}")
    # return response_text
    return short_explanation

def run_external(parts):
    """Run an external command and print output (stdout/stderr)."""
    try:
        result = subprocess.run(parts, check=False, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        short = explain(parts[0], 'external')
        detailed = explain_with_llm(" ".join(parts), short)
        print(detailed)
    except FileNotFoundError:
        print(f"Ghost: command not found: {parts[0]}")
        print(explain(parts[0], 'error', "executable not found"))

def cmd_help():
    print("Ghost Shell built-in commands:")
    print("  cd [dir]     - change directory")
    print("  pwd          - print working directory")
    print("  echo [text]  - print text")
    print("  history      - show command history (session + persistent)")
    print("  whoami       - show current user")
    print("  clear        - clear the screen")
    print("  help         - this help message")
    print("  exit         - exit the shell")
    print("External commands (ls, cat, etc.) are supported as well.")
    print(explain('help', 'builtin'))

def handle_builtin(parts, history):
    cmd = parts[0]
    if cmd == "exit":
        print("Goodbye 👻")
        save_history(history)
        sys.exit(0)
    if cmd == "pwd":
        cwd = os.getcwd()
        print(cwd)
        print(explain('pwd', 'builtin'))
        return True
    if cmd == "cd":
        target = parts[1] if len(parts) > 1 else os.path.expanduser("~")
        try:
            os.chdir(os.path.expanduser(target))
            print(explain('cd', 'builtin', f"changed directory to {os.getcwd()}"))
        except Exception as e:
            print(f"cd: {e}")
            print(explain('cd', 'error', str(e)))
        return True
    if cmd == "echo":
        to_echo = " ".join(parts[1:]) if len(parts) > 1 else ""
        print(to_echo)
        print(explain('echo', 'builtin'))
        return True
    if cmd == "history":
        # show indexed history (session + persistent)
        combined = load_history()  # persistent lines first
        # show only last 200 lines to avoid huge output
        start = max(0, len(combined)-200)
        for i, h in enumerate(combined[start:], start=start+1):
            print(f"{i}\t{h}")
        print(explain('history', 'builtin'))
        return True
    if cmd == "help":
        cmd_help()
        return True
    if cmd == "clear":
        # clear terminal cross-platform
        os.system('clear' if os.name != 'nt' else 'cls')
        return True
    if cmd == "whoami":
        try:
            user = os.getlogin()
        except Exception:
            user = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
        print(user)
        print(explain('whoami', 'builtin'))
        return True
    return False

def parse_input(line):
    try:
        parts = shlex.split(line)
        return parts
    except ValueError as e:
        print(f"Parse error: {e}")
        return []

def load_history():
    """Load persistent history lines from HISTORY_FILE (if exists)."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                lines = [l.rstrip("\n") for l in f.readlines()]
            return lines
        except Exception:
            return []
    return []

def save_history(history):
    """Append new session history to persistent history file safely."""
    try:
        existing = load_history()
        # append only non-duplicates at the end
        to_append = [h for h in history if h.strip() and (not existing or h not in existing[-1000:])]
        if to_append:
            with open(HISTORY_FILE, "a", encoding="utf-8") as f:
                for line in to_append:
                    f.write(line + "\n")
    except Exception as e:
        print("Warning: could not save history:", e)

def main():
    # load persistent history into this session for display
    session_history = load_history()
    # start interactive session
    history = []
    print("Ghost Shell v1 — type 'help' for built-in commands. (LLM_MODE={})".format(LLM_MODE))
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            print()
            save_history(history)
            break
        if not line.strip():
            continue
        # log the command (always)
        log_command(line)
        history.append(line)
        parts = parse_input(line)
        if not parts:
            continue
        built = handle_builtin(parts, history)
        if built is False:
            run_external(parts)

if __name__ == "__main__":
    # ensure logs folder exists (again, for safety)
    LOGS_DIR.mkdir(exist_ok=True)
    main()
