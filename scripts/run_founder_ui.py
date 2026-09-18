"""
JESTER Founder Local Interface CLI Launcher (TASK-0011).

Starts the local-first HTTP/Web server hosting the Founder Command Interface.

Usage:
    python scripts/run_founder_ui.py
    python scripts/run_founder_ui.py --port 8765 --no-browser
"""
import argparse
from pathlib import Path
import sys
import threading
import time
import webbrowser

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

import uvicorn
from jester_bridge.server import create_bridge_app


def main():
    parser = argparse.ArgumentParser(description="JESTER Founder Local Interface Runner")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", default=False, help="Do not open browser automatically")

    args = parser.parse_args()
    url = f"http://{args.host}:{args.port}"

    print("==================================================")
    print("JESTER FOUNDER LOCAL INTERFACE (TASK-0011)")
    print("==================================================")
    print(f"Local Server URL: {url}")
    print("AI Bridge Status: Ready")
    print("Governance:       Mandatory Human Sign-off Enforced")
    print("--------------------------------------------------")
    print("Press Ctrl+C to stop the server.")

    app = create_bridge_app(repo_root=REPO_ROOT)

    if not args.no_browser:
        def _open_browser():
            time.sleep(1.0)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=_open_browser, daemon=True).start()

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
