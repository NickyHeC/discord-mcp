#!/usr/bin/env python3
"""
Simulates Dedalus deployment validation: start server, hit /mcp, then stop.
Run from project root: python scripts/test_deploy.py

Captures server stdout/stderr so we can see why it might exit before responding.
"""
import os
import sys
import time
import signal
import subprocess
import urllib.request
import urllib.error

# Default matches src.main PORT
PORT = int(os.getenv("TEST_PORT", "8080"))
MCP_URL = f"http://127.0.0.1:{PORT}/mcp"
WELL_KNOWN_URL = f"http://127.0.0.1:{PORT}/.well-known/mcp-server.json"
WAIT_TIMEOUT = 15
POLL_INTERVAL = 0.3


def main() -> int:
    env = os.environ.copy()
    env["PORT"] = str(PORT)
    env["HOST"] = "127.0.0.1"

    # Start server the way Dedalus might: as module from project root
    cmd = [sys.executable, "-m", "src.main"]
    print(f"[test_deploy] Starting server: {' '.join(cmd)} (PORT={PORT})")
    proc = subprocess.Popen(
        cmd,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        # Wait for server to respond on /mcp or .well-known
        start = time.monotonic()
        last_output = []
        while (time.monotonic() - start) < WAIT_TIMEOUT:
            # Check if process died
            ret = proc.poll()
            if ret is not None:
                out = proc.stdout.read() if proc.stdout else ""
                print("[test_deploy] Server exited before responding!")
                print("--- Server output ---")
                print(out)
                print("--- End ---")
                return 1

            # Try to reach the server
            try:
                req = urllib.request.Request(WELL_KNOWN_URL, method="GET")
                with urllib.request.urlopen(req, timeout=2) as r:
                    if r.status == 200:
                        print(f"[test_deploy] Server responded at {WELL_KNOWN_URL}")
                        break
            except (OSError, urllib.error.URLError) as e:
                pass  # not ready yet

            # Accumulate any server output for debugging
            if proc.stdout:
                line = proc.stdout.readline()
                if line:
                    last_output.append(line)
                    print(f"[server] {line.rstrip()}")

            time.sleep(POLL_INTERVAL)
        else:
            # Timeout
            out = (proc.stdout.read() if proc.stdout else "") + "\n".join(last_output)
            print("[test_deploy] Timeout waiting for server to respond.")
            print("--- Server output ---")
            print(out)
            print("--- End ---")
            proc.terminate()
            proc.wait(timeout=5)
            return 1

        # Run client (list tools)
        print("[test_deploy] Running client...")
        client_env = os.environ.copy()
        client_env["MCP_URL"] = MCP_URL
        r = subprocess.run(
            [sys.executable, "-m", "src.client"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env=client_env,
            timeout=10,
        )
        if r.returncode != 0:
            print(f"[test_deploy] Client failed with exit code {r.returncode}")
            proc.terminate()
            proc.wait(timeout=5)
            return 1

        print("[test_deploy] OK: server stayed up and responded on /mcp.")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        # Dump any remaining server output
        if proc.stdout:
            rest = proc.stdout.read()
            if rest:
                print("--- Server output (final) ---")
                print(rest)


if __name__ == "__main__":
    sys.exit(main())
