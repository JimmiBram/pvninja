import subprocess, signal, sys, os, time

PROCESSES = []

def spawn(name, *cmd):
    print(f"[orchestrator] starting {name} …")
    p = subprocess.Popen(cmd)
    PROCESSES.append((name, p))

def terminate_all(_sig=None, _frame=None):
    print("\n[orchestrator] stopping everything …")
    for name, p in PROCESSES:
        print(f"  └─ {name}")
        p.send_signal(signal.SIGINT)
    for _, p in PROCESSES:
        p.wait()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, terminate_all)
    signal.signal(signal.SIGTERM, terminate_all)

    spawn("server", "poetry", "run", "start-server")
    spawn("ui",     "poetry", "run", "start-ui")

    # Wait forever ‑ the signal handler does the shutdown work
    while True:
        time.sleep(1)
