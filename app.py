import logging
import json
import os
import re
from slack_bolt import App

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)


@app.middleware  # or app.use(log_request)
def log_request(logger, body, next):
    logger.debug(body)
    return next()


# messages https://slack.dev/bolt-python/concepts#message-listening

@app.message("knock knock")
def ask_who(say):
    say("_Who's there?_")


@app.message(re.compile("(elf|ELF|Elf)"))
def say_hello_regex(say, context, logger, body):
    logger.info(body)
    greeting = context['matches'][0]
    say(f"Hi! {greeting} is here, how may I help you?")


# webAPI https://slack.dev/bolt-python/concepts#web-api
@app.message("wake me up")
def say_hello(client, message):
    channel_id = message["channel"]
    client.chat_postMessage(
        channel=channel_id,
        text="Summer has come and passed"
    )


@app.action("button_click")
def action_button_click(body, ack, say):
    ack()
    say(f"<@{body['user']['id']}> clicked the button")


@app.command("/test")
def repeat_text(ack, say):
    ack()
    say(f"elf is working!")


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    try:
        with open('view/home.json') as f:
            data = json.load(f)

        # views.publish is the method that your app uses to push a view to the Home tab
        client.views_publish(
            user_id=event["user"],
            view=json.dumps(data)
        )

    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.command("/vm-provision")
def open_modal(body, ack, client, logger):
    ack()

    with open('view/vm_provision.json') as f:
        data = json.load(f)

    res = client.views_open(
        trigger_id=body["trigger_id"],
        view=json.dumps(data)
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
    app.start(port=int(os.environ.get("PORT", 3000)))
