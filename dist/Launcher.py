import subprocess
import time
import webview
import sys
import urllib.request


def start_streamlit():
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true"])


def get_active_url():
    for _ in range(15):
        time.sleep(1)
        for p in range(8501, 8520):
            url = f"http://localhost:{p}"
            try:
                req = urllib.request.urlopen(url, timeout=1)
                if req.status == 200:
                    return url
            except Exception:
                continue
    return "http://localhost:8501"


if __name__ == '__main__':
    print("Starting AuditFlow Web Server...")
    app_url = get_active_url()
    print(f"Server active at: {app_url}")

    # Create the window and start immediately
    window = webview.create_window(
        title="AuditFlow Enterprise | Public Accounting Suite",
        url=app_url,
        width=1400,
        height=900,
        resizable=True
    )

    webview.start()