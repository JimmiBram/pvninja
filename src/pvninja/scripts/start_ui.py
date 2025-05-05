import subprocess, sys, os, signal

def main():
    cmd = [
        "gunicorn",
        "-k", "uvicorn.workers.UvicornWorker",
        "ui.app:app",
        "--bind", "0.0.0.0:8000",
        "--workers", "1",          # exactly one instance
    ]
    # Forward CTRL‑C to gunicorn nicely
    try:
        proc = subprocess.Popen(cmd)
        proc.wait()
    except KeyboardInterrupt:
        print("\n[ui] stopping …", file=sys.stderr)
        proc.send_signal(signal.SIGINT)
        proc.wait()
