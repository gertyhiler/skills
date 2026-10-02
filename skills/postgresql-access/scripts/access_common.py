"""Vendored per skill so copying one skill remains sufficient."""
import json
import os
import subprocess
from io import StringIO
from pathlib import Path
from dotenv import dotenv_values

class AccessError(Exception):
    """An intentionally safe diagnostic; never include server bodies or secrets."""

class PolicyError(AccessError):
    pass

def load_env(explicit=None, cwd=None):
    cwd = Path(cwd or Path.cwd()).resolve()
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=cwd,
                            capture_output=True, text=True, timeout=10)
    root = Path(result.stdout.strip()) if result.returncode == 0 else cwd
    target = (cwd / explicit).resolve() if explicit else root / ".agents/local/.env.agents"
    try:
        raw = target.read_text(encoding="utf-8")
    except OSError:
        raise AccessError("Cannot read agent env file; configure .agents/local/.env.agents or pass --env-file.") from None
    values = dotenv_values(stream=StringIO(raw), interpolate=False)
    return {k: v for k, v in values.items() if v is not None}

def positive(value):
    import argparse
    try:
        number = int(value)
        if number > 0:
            return number
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("must be a positive integer")

def write_private(target, text):
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
    except OSError:
        raise AccessError("Cannot create evidence file; check its parent and use a new filename.") from None

def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))

def run(main):
    import sys
    try:
        emit(main())
    except PolicyError as error:
        print(str(error), file=sys.stderr)
        return 2
    except AccessError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        print("Access helper failed; raw error suppressed. Check configuration, dependency and access contract.", file=sys.stderr)
        return 1
    return 0
