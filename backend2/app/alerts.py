import requests, os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def notify(node_id: str, event_type: str, severity: str):
    msg = f"[{severity.upper()}] {event_type} detected at {node_id}"

    if not SLACK_WEBHOOK_URL:
        print(f"[ALERT - no webhook configured] {msg}")
        return

    try:
        requests.post(SLACK_WEBHOOK_URL, json={"text": msg}, timeout=5)
    except requests.RequestException as e:
        print(f"[ALERT FAILED] {msg} — {e}")