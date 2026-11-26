import os
import sys
import uvicorn
import signal

# --------------------------------------------------------------------
# Ensure the proper directory is on PYTHONPATH both when running as a
# script (development) and when packaged with PyInstaller (frozen).
# --------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    # When bundled, PyInstaller extracts files to a temporary folder.
    # Add the extracted path and also the original working directory (where
    # the exe is launched) to sys.path so that the bundled "src" package can be found.
    base_path = sys._MEIPASS  # type: ignore
    cwd_path = os.getcwd()
    for p in (base_path, cwd_path):
        if p not in sys.path:
            sys.path.insert(0, p)
else:
    # Running from source – add the project root (contains the src folder).
    base_path = os.path.abspath(os.path.dirname(__file__))
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

def _handle_shutdown(signum, frame):
    print(f"[{signum}] Signal received, shutting down gracefully...")
    sys.exit(0)

# Register handlers for common termination signals
signal.signal(signal.SIGINT, _handle_shutdown)   # Ctrl+C
signal.signal(signal.SIGTERM, _handle_shutdown)  # termination from OS

import webbrowser

if __name__ == "__main__":
    print("Starting Pior server on http://127.0.0.1:8000 ...")
    try:
        webbrowser.open("http://127.0.0.1:8000")
    except Exception as e:
        print(f"Failed to open browser: {e}")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_config=None,
        access_log=False,
    )
