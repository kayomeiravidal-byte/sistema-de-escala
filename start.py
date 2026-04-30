import webbrowser
import threading
import subprocess

def start_server():
    subprocess.run(["python", "run_server.py"])

def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Timer(2, open_browser).start()
    start_server()