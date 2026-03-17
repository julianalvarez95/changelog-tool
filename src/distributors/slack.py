"""
Send changelog to Slack using slack_sdk.
"""
import sys

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    print("[ERROR] slack_sdk not installed. Run: pip install slack_sdk", file=sys.stderr)
    raise


def send(token: str, channel: str, text: str) -> bool:
    """
    Post a text message to a Slack channel.
    Returns True on success, False on failure.
    """
    if not token:
        print("[ERROR] SLACK_BOT_TOKEN is required to send Slack messages.", file=sys.stderr)
        return False

    client = WebClient(token=token)
    try:
        resp = client.chat_postMessage(
            channel=channel,
            text=text,
            mrkdwn=True,
        )
        print(f"[slack] Message sent to {channel} (ts={resp['ts']})")
        return True
    except SlackApiError as e:
        print(f"[ERROR] Slack API error: {e.response['error']}", file=sys.stderr)
        return False
