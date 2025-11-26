#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime

# ==============================
#   Explanation Dictionary
# ==============================
EXPLANATIONS = {
    "cd": "Used built-in command 'cd' to change directory — affects shell process, not child process.",
    "pwd": "Displayed current working directory using 'os.getcwd()' — no new process created.",
    "echo": "Printed text directly using shell built-in — no process spawned.",
    "history": "Showing command history stored inside Ghost Shell memory.",
    "exit": "Terminating the Ghost Shell process using sys.exit().",
}

# ==============================
#   Shell History
# ==============================
history = []

# ==============================
#   Logging (for project marks)
# ==============================
def log_command(cmd):
    with open("logs/ghost_log.txt", "a") as f:
        f.write(f"{datetime.now()}  ->  {cmd}\n")

# ==============================
#   Execute Built-in Commands
# ==============================
def handle_builtin(cmd, args):
    if cmd == "cd":
        try:
            os.chdir(args[0] if args else "/")
            return "", EXPLANATIONS["cd"]
        except Exception as e:
            return f"cd: {e}", ""

    elif cmd == "pwd":
        return os.getcwd(), EXPLANATIONS["pwd"]

    elif cmd == "echo":
        return " ".join(args), EXPLANATIONS["echo"]

    elif cmd == "history":
        return "\n".join(history), EXPLANATIONS["history"]

    elif cmd == "exit":
        print(EXPLANATIONS["exit"])
        sys.exit(0)

    return None, None  # not built-in

# ==============================
#   Execute External Commands
# ==============================
def execute_external(cmd_list):
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        output = result.stdout + result.stderr
        
        explanation = (
            "Executed external command by spawning a child process using "
            "subprocess module → internally uses fork() + execvp()."
        )
        return output, explanation
    except FileNotFoundError:
        return f"{cmd_list[0]}: command not found", ""
    except Exception as e:
        return str(e), ""

# ==============================
#   Main Shell Loop (REPL)
# ==============================
def main():
    while True:
        try:
            user_input = input("Ghost$ ").strip()
        except EOFError:
            break

        if not user_input:
            continue

        # Save to history + log
        history.append(user_input)
        log_command(user_input)

        parts = user_input.split()
        cmd = parts[0]
        args = parts[1:]

        # 1. Try built-in commands
        output, explanation = handle_builtin(cmd, args)

        if output is None and explanation is None:
            # 2. Execute external commands
            output, explanation = execute_external([cmd] + args)

        # Display output
        if output:
            print(output)

        # Display explanation
        if explanation:
            print(f"\n[Explanation] {explanation}\n")


if __name__ == "__main__":
    main()
