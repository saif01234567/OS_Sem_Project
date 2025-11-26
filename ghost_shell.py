#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime

# ==============================
#   Explanation Dictionary
# ==============================
EXPLANATIONS = {
    "cd": "Used built-in command 'cd' to change directory — affects the current shell process (no child process created).",
    "pwd": "Displayed current working directory using os.getcwd() — simple system call, no new process spawned.",
    "echo": "Printed text directly inside the shell (built-in).",
    "history": "Displayed command history stored in shell memory.",
    "exit": "Exited shell by terminating the parent process using sys.exit()."
}

# ==============================
#   External Command Explanation
# ==============================
def explain_external_command(cmd):
    return (
        f"[SYSTEM] Spawned a child process for '{cmd}' using fork() + execvp(). "
        f"Parent waits using waitpid(). The OS scheduler decides when the child runs."
    )

# ==============================
#   Shell History
# ==============================
history = []

# ==============================
#   Logging (for OS project marks)
# ==============================
def log_command(cmd):
    with open("logs/ghost_log.txt", "a") as f:
        f.write(f"{datetime.now()} -> {cmd}\n")


# ==============================
#   Built-in Command Handler
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

    return None, None



# ==============================
#   External Command Execution
# ==============================
def execute_external(cmd_list):
    """
    Executes external programs using subprocess (which internally uses fork + execvp).
    """
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        output = result.stdout + result.stderr
        explanation = explain_external_command(cmd_list[0])
        return output, explanation

    except FileNotFoundError:
        return f"{cmd_list[0]}: command not found", ""

    except Exception as e:
        return str(e), ""


# ==============================
#   Main Shell (REPL)
# ==============================
def main():
    while True:
        try:
            user_input = input("Ghost$ ").strip()
        except EOFError:
            break

        if not user_input:
            continue

        # Save history + logs
        history.append(user_input)
        log_command(user_input)

        parts = user_input.split()
        cmd = parts[0]
        args = parts[1:]

        # First try built-ins
        output, explanation = handle_builtin(cmd, args)

        # If not built-in → external command
        if output is None and explanation is None:
            output, explanation = execute_external([cmd] + args)

        # Print command output
        if output:
            print(output)

        # Print OS explanation
        if explanation:
            print(f"\n[Explanation] {explanation}\n")


# ==============================
#   Run Shell
# ==============================
if __name__ == "__main__":
    # Ensure logs folder exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
    main()

