#!/usr/bin/env python3
"""
Auto-commit and push daemon for AgriData project.
Monitors git repository for any changes, generates realistic semantic commit messages,
and immediately pushes to GitHub.
"""

import os
import sys
import time
import subprocess
import signal
import re
from pathlib import Path
from datetime import datetime

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
PID_FILE = WORKSPACE_DIR / ".auto_commit.pid"
LOG_FILE = WORKSPACE_DIR / "auto_commit.log"
DEBOUNCE_SECONDS = 4
CHECK_INTERVAL_SECONDS = 3

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def run_cmd(cmd, cwd=WORKSPACE_DIR):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=isinstance(cmd, str)
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def get_git_status():
    code, out, _ = run_cmd(["git", "status", "--porcelain"])
    if code != 0 or not out:
        return []
    changes = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        status = line[:2].strip()
        filepath = line[2:].strip().strip('"')
        
        # Ignore our internal daemon files
        if filepath in [".auto_commit.pid", "auto_commit.log"] or filepath.startswith(".auto_commit"):
            continue
        changes.append((status, filepath))
    return changes

def determine_scope(filepath: str) -> str:
    path_lower = filepath.lower()
    parts = Path(filepath).parts
    
    if "dataset" in path_lower or "data" in path_lower or "telepati 8.0 datasets" in path_lower:
        return "dataset"
    if "model" in path_lower or "yolo" in path_lower or "train" in path_lower:
        return "model"
    if "notebook" in path_lower or filepath.endswith(".ipynb"):
        return "notebook"
    if "eval" in path_lower or "val" in path_lower or "metric" in path_lower:
        return "eval"
    if "preprocess" in path_lower or "augment" in path_lower or "transform" in path_lower:
        return "data-pipeline"
    if "infer" in path_lower or "detect" in path_lower or "predict" in path_lower:
        return "inference"
    if "util" in path_lower or "helper" in path_lower:
        return "utils"
    if "script" in path_lower:
        return "scripts"
    if "config" in path_lower or filepath.endswith((".yaml", ".yml", ".json", ".toml", ".ini")):
        return "config"
    if "doc" in path_lower or filepath.endswith((".md", ".txt", ".rst")):
        return "docs"
    if "test" in path_lower:
        return "test"
    
    if len(parts) > 1:
        clean_part = re.sub(r'[^a-zA-Z0-9_-]', '', parts[0]).lower()
        if clean_part:
            return clean_part
            
    stem = Path(filepath).stem.lower()
    clean_stem = re.sub(r'[^a-zA-Z0-9_-]', '', stem)
    return clean_stem if clean_stem else "core"

def analyze_diff_for_semantics(filepath: str, status: str) -> tuple:
    """Returns (type, scope, description) for realistic developer commit."""
    scope = determine_scope(filepath)
    ext = Path(filepath).suffix.lower()
    filename = Path(filepath).name
    stem = Path(filepath).stem.replace("_", " ").replace("-", " ")
    
    # 1. DELETED files
    if "D" in status:
        return ("refactor", scope, f"remove obsolete {stem} {ext[1:] if ext else 'file'}".strip())
    
    # 2. NEW files (?? or A)
    if "??" in status or "A" in status:
        if ext in [".md", ".rst", ".txt"]:
            if "readme" in filename.lower():
                return ("docs", "readme", "initialize project documentation and architecture overview")
            return ("docs", scope, f"add documentation for {stem}")
        if ext == ".ipynb":
            return ("feat", scope, f"add {stem} exploratory analysis and experimentation notebook")
        if ext in [".yaml", ".yml", ".json", ".toml"]:
            return ("chore", scope, f"configure {stem} specifications")
        if ext == ".py":
            if "train" in filename.lower():
                return ("feat", scope, "implement model training execution pipeline")
            if "detect" in filename.lower() or "predict" in filename.lower() or "infer" in filename.lower():
                return ("feat", scope, "implement object detection inference module")
            if "eval" in filename.lower() or "test" in filename.lower():
                return ("test", scope, f"implement evaluation benchmarks for {stem}")
            if "convert" in filename.lower() or "prepare" in filename.lower() or "dataset" in filename.lower():
                return ("feat", scope, f"add dataset preparation and format conversion utilities")
            return ("feat", scope, f"implement {stem} module")
        if ext in [".sh", ".bash"]:
            return ("chore", scope, f"add {stem} automation script")
        if ext in [".jpg", ".png", ".jpeg"]:
            return ("feat", scope, f"add sample image assets for {stem}")
        return ("feat", scope, f"add {filename}")

    # 3. MODIFIED files (M)
    code, diff_out, _ = run_cmd(["git", "diff", "--", filepath])
    diff_lower = diff_out.lower() if diff_out else ""
    
    # Inspect diff contents for clues
    if ext in [".md", ".rst", ".txt"]:
        return ("docs", scope, f"update {stem} documentation details")
    
    if ext == ".ipynb":
        return ("refactor", scope, f"update experiments and outputs in {filename}")
        
    if ext in [".yaml", ".yml", ".json"]:
        return ("chore", scope, f"update {filename} configuration settings")

    if ext == ".py":
        if "def " in diff_out:
            added_defs = re.findall(r'^\+\s*def\s+([a-zA-Z0-9_]+)', diff_out, re.MULTILINE)
            if added_defs:
                func_name = added_defs[0].replace("_", " ")
                return ("feat", scope, f"implement {func_name} in {filename}")
        if "fix" in diff_lower or "bug" in diff_lower or "error" in diff_lower or "except" in diff_lower:
            return ("fix", scope, f"resolve edge cases and handle exceptions in {filename}")
        if "import " in diff_out:
            return ("refactor", scope, f"update imports and dependencies in {filename}")
        if "batch" in diff_lower or "lr" in diff_lower or "epoch" in diff_lower or "param" in diff_lower:
            return ("refactor", scope, f"tune training hyperparameters in {filename}")
        return ("refactor", scope, f"enhance logic and modular structure in {filename}")

    return ("chore", scope, f"update {filename}")

def generate_commit_message(changes: list) -> str:
    if not changes:
        return "chore: update project assets"
    
    # If single file changed, specific message
    if len(changes) == 1:
        status, filepath = changes[0]
        ctype, scope, desc = analyze_diff_for_semantics(filepath, status)
        return f"{ctype}({scope}): {desc}"
    
    # Multiple files changed - analyze distribution
    scopes = set()
    types = []
    filenames = []
    
    for status, filepath in changes:
        ctype, scope, desc = analyze_diff_for_semantics(filepath, status)
        scopes.add(scope)
        types.append(ctype)
        filenames.append(Path(filepath).name)
        
    common_scope = scopes.pop() if len(scopes) == 1 else "core"
    
    # Determine dominant type
    if "feat" in types:
        primary_type = "feat"
    elif "fix" in types:
        primary_type = "fix"
    elif "refactor" in types:
        primary_type = "refactor"
    elif "docs" in types:
        primary_type = "docs"
    else:
        primary_type = "chore"
        
    if len(changes) <= 3:
        files_str = ", ".join(filenames)
        return f"{primary_type}({common_scope}): update {files_str}"
    else:
        return f"{primary_type}({common_scope}): update {len(changes)} components across {common_scope}"

def commit_and_push_cycle():
    changes = get_git_status()
    if not changes:
        return False
        
    log(f"Detected {len(changes)} pending change(s). Debouncing for {DEBOUNCE_SECONDS}s...")
    time.sleep(DEBOUNCE_SECONDS)
    
    # Re-check status after debounce
    changes = get_git_status()
    if not changes:
        log("No changes remaining after debounce.")
        return False
        
    msg = generate_commit_message(changes)
    log(f"Generated commit message: '{msg}'")
    
    # Stage changes
    code, _, err = run_cmd(["git", "add", "-A"])
    if code != 0:
        log(f"git add error: {err}")
        return False
        
    # Check if there are staged changes
    code, staged, _ = run_cmd(["git", "diff", "--cached", "--name-only"])
    if not staged:
        log("Nothing staged to commit.")
        return False
        
    # Commit
    code, out, err = run_cmd(["git", "commit", "-m", msg])
    if code != 0:
        log(f"git commit error: {err}")
        return False
    log(f"Committed successfully: {out.splitlines()[0] if out else ''}")
    
    # Push
    log("Pushing to origin main...")
    code, out, err = run_cmd(["git", "push", "origin", "main"])
    if code == 0:
        log("Push successful!")
        return True
    else:
        log(f"Push failed (will retry next cycle): {err or out}")
        return False

def run_loop():
    log("Starting auto-commit daemon loop...")
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
        
    def handle_exit(signum, frame):
        log(f"Received termination signal ({signum}). Stopping auto-commit daemon.")
        if PID_FILE.exists():
            PID_FILE.unlink(missing_ok=True)
        sys.exit(0)
        
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
    
    try:
        while True:
            try:
                commit_and_push_cycle()
            except Exception as e:
                log(f"Cycle exception: {e}")
            time.sleep(CHECK_INTERVAL_SECONDS)
    finally:
        if PID_FILE.exists():
            PID_FILE.unlink(missing_ok=True)

def start_daemon():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            print(f"Auto-commit daemon is already running (PID: {pid}).")
            return
        except (ProcessLookupError, ValueError):
            PID_FILE.unlink(missing_ok=True)
            
    # Launch background subprocess detached
    log("Launching auto-commit daemon in background...")
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--loop"],
        cwd=WORKSPACE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    time.sleep(1)
    if PID_FILE.exists():
        pid = PID_FILE.read_text().strip()
        print(f"Auto-commit daemon started successfully (PID: {pid}).")
        print(f"Logs: {LOG_FILE}")
    else:
        print(f"Auto-commit daemon started with PID: {proc.pid}")

def stop_daemon():
    if not PID_FILE.exists():
        print("Auto-commit daemon is not running (PID file not found).")
        return
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        print(f"Auto-commit daemon (PID {pid}) stopped.")
    except ProcessLookupError:
        print("Process not found. Cleaning up stale PID file.")
    except Exception as e:
        print(f"Failed to stop daemon: {e}")
    finally:
        PID_FILE.unlink(missing_ok=True)

def check_status():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            print(f"Status: RUNNING (PID: {pid})")
            print(f"Log file: {LOG_FILE}")
            # Print last 5 log entries
            if LOG_FILE.exists():
                lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
                print("\nRecent Activity:")
                for line in lines[-5:]:
                    print(f"  {line}")
            return
        except ProcessLookupError:
            PID_FILE.unlink(missing_ok=True)
    print("Status: STOPPED (Daemon is not running).")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["--start", "start"]:
            start_daemon()
        elif arg in ["--stop", "stop"]:
            stop_daemon()
        elif arg in ["--status", "status"]:
            check_status()
        elif arg in ["--run-once", "run-once"]:
            commit_and_push_cycle()
        elif arg in ["--loop", "loop"]:
            run_loop()
        else:
            print("Usage: python3 auto_commit_daemon.py [--start | --stop | --status | --run-once | --loop]")
    else:
        start_daemon()
