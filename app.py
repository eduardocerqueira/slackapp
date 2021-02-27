import os
# Use the package we installed
from slack_bolt import App
import json

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


# This will match any message that contains 👋
@app.message(":wave:")
def say_hello(message, say):
    user = message['user']
    say(f"Hi there, <@{user}>!")


@app.message("hello")
def say_hello1(message, say):
    user = message['user']
    say(f"Hi there, <@{user}>!")


# Listens for messages containing "knock knock" and responds with an italicized "who's there?"
@app.message("knock knock")
def ask_who(message, say):
    say("_Who's there?_")


@app.message("test")
def ask_who1(message, say):
    say("_working_")


# Listens to incoming messages that contain "hello"
@app.message("hi")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            # the user that opened your app's app home
            user_id=event["user"],
            # the view object that appears in the app home
            view={
                "type": "home",
                "callback_id": "home_view",

                # body of the view
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Welcome to your _App's Home_* :tada:"
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Click me!"
                                }
                            }
                        ]
                    }
                ]
            }
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.command("/test")
def test_command(body, client, ack, logger):
    logger.info(body)
    ack("I got it!")
    res = client.dialog_open(
        trigger_id=body["trigger_id"],
        dialog={
            "callback_id": "dialog-callback-id",
            "title": "Request a Ride",
            "submit_label": "Request",
            "notify_on_cancel": True,
            "state": "Limo",
            "elements": [
                {"type": "text", "label": "Pickup Location", "name": "loc_origin"},
                {
                    "type": "text",
                    "label": "Dropoff Location",
                    "name": "loc_destination",
                },
                {
                    "label": "Type",
                    "name": "types",
                    "type": "select",
                    "data_source": "external",
                },
            ],
        },
    )
    logger.info(res)


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
