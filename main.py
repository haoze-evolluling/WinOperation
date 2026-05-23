import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from main import run_server, is_admin, elevate_and_run

if __name__ == "__main__":
    if not is_admin():
        elevate_and_run()
    run_server()
