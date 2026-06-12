import shlex


FORBIDDEN_KEYWORDS = [
    "curl",
    "wget",
    "nc",
    "netcat",
    "ssh",
    "scp",
    "sudo",
    "su",
    "chmod",
    "chown",
    "rm",
    "mkfs",
    "mount",
    "umount",
    "dd",
    ":(){",
]


ALLOWED_COMMANDS = [
    "ls",
    "cat",
    "echo",
    "pwd",
    "python3",
]


def is_command_allowed(command: str) -> tuple[bool, str]:
    """
    Basic policy layer for agent-requested commands.

    This is intentionally simple for the first prototype:
    - block dangerous keywords
    - allow only a small set of commands
    """

    if not command.strip():
        return False, "Empty command is not allowed."

    lowered_command = command.lower()

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in lowered_command:
            return False, f"Forbidden keyword detected: {keyword}"

    try:
        parts = shlex.split(command)
    except ValueError:
        return False, "Invalid command syntax."

    executable = parts[0]

    if executable not in ALLOWED_COMMANDS:
        return False, f"Command not in allowlist: {executable}"

    return True, "Command allowed."
