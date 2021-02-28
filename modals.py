import logging
from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)

app = App()


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.command("/vm")
def open_modal(body, ack, client, logger):
    ack()
    res = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "modal_vm",
            "title": {
                "type": "plain_text",
                "text": "Openstack VM launcher",
            },
            "submit": {
                "type": "plain_text",
                "text": "Provision",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "vm",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "name",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "kerberos_username-vm_name"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "vm name"
                    },
                    "hint": {
                        "type": "plain_text",
                        "text": "no spaces and special chars (.,*) suggestion: kerberos_username-vm_name"
                    }
                },
                {
                    "type": "section",
                    "block_id": "os",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Select RHEL version"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item"
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "RHEL-6.10"
                                },
                                "value": "RHEL-6.10"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "RHEL-7.9"
                                },
                                "value": "RHEL-7.9"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "RHEL-8.0"
                                },
                                "value": "RHEL-8.0"
                            }
                        ],
                        "action_id": "nvr"
                    }
                }
            ],
        },
    )
    logger.info(res)


@app.view("modal_vm")
def handle_submission(ack, body, client, view, logger):
    ack()
    logger.info(body["view"]["state"]["values"])
    vm_name = view["state"]["values"]["vm"]["name"]["value"]
    os_nvr = view["state"]["values"]["os"]["nvr"]["selected_option"]["value"]
    user = body["user"]["id"]
    # Validate the inputs
    errors = {}
    if vm_name is None:
        errors["vm_name"] = "The value can not be empty"
    if len(errors) > 0:
        ack(response_action="errors", errors=errors)
        return
    # Acknowledge the view_submission event and close the modal
    ack()
    # Do whatever you want with the input data - here we're saving it to a DB
    # then sending the user a verification of their submission

    # Message to send user
    msg = ""
    try:
        # Save to DB
        msg = f"Your submission of provisioning {vm_name} for {os_nvr} was successful"
    except Exception as e:
        # Handle error
        msg = "There was an error with your submission"
    finally:
        # Message the user
        client.chat_postMessage(channel=user, text=msg)

    # Message to send user
    msg = ""
    try:
        # Save to DB
        import time
        time.sleep(30)
        msg = f":white_check_mark: {vm_name} running {os_nvr} provisioned!"
    except Exception as e:
        # Handle error
        msg = "There was an error with your submission"
    finally:
        # Message the user
        client.chat_postMessage(channel=user, text=msg)


@app.action("nvr")
def rhel_selected(ack):
    ack()


if __name__ == "__main__":
    app.start(3000)
