#!/usr/bin/env python3
"""
Launcher for Medical Triage System.
Starts the FastAPI backend in background, then runs Streamlit frontend.
For Hugging Face Spaces and local development.
"""
import os
import sys
import threading
import time

# Ensure we're in the correct directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def run_backend():
    import uvicorn
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    # Start backend in background thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    time.sleep(3)  # Allow backend to start

    # Run Streamlit frontend
    import subprocess
    port = os.environ.get("STREAMLIT_PORT", "7860")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false",
    ], check=True)
