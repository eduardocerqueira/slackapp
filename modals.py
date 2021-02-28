import logging
from slack_bolt import App

logging.basicConfig(level=logging.DEBUG)

app = App()


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.command("/vm-provision")
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
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Provision a virtual machine to Openstack. The name will be concatenated automatically as slack_userid-os_nvr-vm_name",
                    }
                },
                {
                    "type": "input",
                    "block_id": "vm",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "name",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "name of your virtual machine"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Name"
                    },
                    "hint": {
                        "type": "plain_text",
                        "text": "short name, no spaces and special characters"
                    }
                },
                {
                    "type": "section",
                    "block_id": "os",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Select OS NVR"
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
    user_id = body["user"]["id"]
    user_name = body["user"]["username"]
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

    osp_vm_name = f"{user_name}-{os_nvr}-{vm_name}".lower()

    # Message to send user
    msg = ""
    try:
        # Save to DB
        msg = f"Your request to provision `{osp_vm_name}` in Openstack was sent successfully \n" \
              f"it can take a few minutes :hourglass_flowing_sand: please wait and I will let you know when it is ready!"
    except Exception as e:
        msg = f":x: There was an error in sending your request to provision {osp_vm_name} to Openstack"
    finally:
        client.chat_postMessage(channel=user_id, text=msg)

    # Message to send user
    msg = ""
    try:
        # Save to DB
        # OpenstackSDK
        import time
        time.sleep(10)
        msg = f":white_check_mark: `{osp_vm_name}` was provisioned! \n" \
              f"you can access: \n" \
              f"```\n" \
              f"sshpass -p redhat ssh root@192.168.1.1 \n" \
              f"```"
    except Exception as e:
        # Handle error
        msg = f":x: There was an error while working in your request to provision {osp_vm_name} to Openstack \n" \
              f":pray: try it again later"
    finally:
        # Message the user
        client.chat_postMessage(channel=user_id, text=msg)


@app.action("nvr")
def rhel_selected(ack):
    ack()


@app.command("/vm-list")
def vm_list(body, ack, client):
    ack()

    user_id = body["user_id"]
    user_name = body["user_name"]

    # call OpenstackSDK and get a list of vm which contains user_id in vm name
    # format and return list or error

    # Message to send user
    msg = ""
    try:
        msg = f"{user_name}-vm1, {user_name}-vm2, {user_name}-vm3"
    except Exception as e:
        msg = f":x: There was an error in retrieving your vm(s) from Openstack \n" \
              f":pray: try it again later"
    finally:
        client.chat_postMessage(channel=user_id, text=msg)


@app.command("/vm-delete")
def vm_list(body, ack, client):
    ack()

    user_id = body["user_id"]
    user_name = body["user_name"]
    vm_name = body["text"]

    # call OpenstackSDK and get a list of vm which contains user_id in vm name
    # check vm_name is in the list
    # delete or error

    # Message to send user
    msg = ""
    try:
        msg = f"{user_name}-vm1, {user_name}-vm2, {user_name}-vm3"
    except Exception as e:
        msg = f":x: There was an error in retrieving your vm(s) from Openstack \n" \
              f":pray: try it again later"
    finally:
        client.chat_postMessage(channel=user_id, text=msg)


if __name__ == "__main__":
    app.start(3000)
