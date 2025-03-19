import os
import re

import httpx
from slack_bolt import App

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
)


@app.event("url_verification")
def handle_url_verification(body, ack):
    """
    Handle the Slack URL verification challenge during app setup.

    This function responds to Slack's URL verification challenge by echoing back
    the challenge token, which is required for setting up the Slack app's event
    subscriptions.

    Args:
        body (dict): The request body containing the challenge token
        ack (function): Acknowledgement function to respond to Slack
    """
    ack(body["challenge"])


@app.event("app_mention")
def handle_app_mentions(event, say):
    """
    Process mentions of the bot in Slack and respond appropriately.

    When mentioned with the specific format requesting a Kestra execution review,
    this function extracts the execution ID and provides a button to resume the workflow.
    Otherwise, it responds with a generic message.

    Args:
        event (dict): The Slack event data containing the mention details
        say (function): Function to send messages back to the Slack channel
    """
    robot_reviewer = os.getenv("SLACK_BOT_USER_ID")

    if f"<@{robot_reviewer}>, will you review Kestra Execution ID: " in event["text"]:
        execution_id_pattern = r"Kestra Execution ID: ([^?]+)?"
        match = re.search(execution_id_pattern, event["text"])
        execution_id = match.group(1)

        say(
            blocks=[
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Resume Workflow",
                            },
                            "value": execution_id,
                            "action_id": "resume_kestra_workflow",
                        }
                    ],
                },
            ],
            thread_ts=event["ts"],
        )
    else:
        say("Hello, that message does not trigger anything.")


@app.action("resume_kestra_workflow")
def handle_resume_kestra_workflow(body, ack, say):
    """
    Resume a paused Kestra workflow execution via button click.

    This function is triggered when a user clicks the "Resume Workflow" button.
    It calls the Kestra API to resume the specified execution and provides
    feedback on the result in the Slack thread.

    Args:
        body (dict): The request body containing action details and execution ID
        ack (function): Acknowledgement function to respond to Slack's action request
        say (function): Function to send messages back to the Slack channel
    """
    ack()

    kestra_api_token = os.getenv("KESTRA_API_TOKEN")

    user = body["user"]["name"]
    thread_ts = (
        body["container"]["thread_ts"]
        if "thread_ts" in body["container"]
        else body["container"]["message_ts"]
    )
    execution_id = body["actions"][0]["value"]

    headers = {
        "Authorization": f"Bearer {kestra_api_token}",
    }

    url = (
        f"{os.getenv('KESTRA_SERVER_URL')}/api/v1/{os.getenv('KESTRA_TENANT_ID')}/"
        f"executions/{execution_id}/resume"
    )

    response = httpx.post(url, headers=headers)

    if response.status_code in [200, 204]:
        say(
            f"Kestra Execution {execution_id} resumed by {user}.",
            thread_ts=thread_ts,
        )
    elif response.status_code == 409:
        say(
            f"Kestra Execution {execution_id} is already in progress.",
            thread_ts=thread_ts,
        )
    else:
        say(
            f"Sorry, there was an error resuming Kestra "
            f"execution {execution_id} - {response.status_code}: "
            f"{response.text}.",
            thread_ts=thread_ts,
        )


if __name__ == "__main__":
    app.start(
        port=3000,
        http_server_logger_enabled=False,
    )
