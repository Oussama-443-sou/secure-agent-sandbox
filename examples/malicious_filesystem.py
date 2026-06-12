from pathlib import Path

sensitive_paths = [
    "/etc/passwd",
    "/root/.ssh/id_rsa",
    "/host/etc/passwd",
]

for path in sensitive_paths:
    target = Path(path)

    print(f"Trying to read {path}...")

    try:
        content = target.read_text(errors="ignore")
        print(f"Unexpectedly readable: {path}")
        print(content[:200])
    except Exception as error:
        print(f"Blocked or unavailable: {path} ({error})")
