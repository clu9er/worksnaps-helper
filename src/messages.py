from models.worksnaps_user import WorksnapsUser

new_user_greeting_message = (
    "<b>Hello!</b> I am your <i>Worksnaps helper bot</i>. 🤖\n\n"
    "To get started, please provide your <b>Worksnaps API token</b>. I'll save it for you to use.\n\n"
    "To get your API token:\n"
    "1. Go to Profile & Settings >> Web Service API (Figure 1).\n"
    "2. Click the link Show my API Token. Then you will see the API token displayed in clear text (Figure 2).\n\n"
    "Thank you!"
)

existing_user_greeting_message = (
    "<b>Hello again!</b> I am your <i>Worksnaps helper bot</i>. 🤖\n\n"
    "Your <b>Worksnaps API token</b> is already set. \n"
    "You can now use the <code>/statistics</code> command to get your projects summary."
)

def create_existing_user_greeting_message(token_exists: bool) -> str:
    message = (
        "<b>Hello again!</b> I am your <i>Worksnaps helper bot</i>. 🤖\n\n"
    )

    if token_exists:
        message += "Your <b>Worksnaps API token</b> is already set. \n"
        message += "You can now use the <code>/statistics</code> command to get your projects summary."
    else:
        message += "To get started, please provide your <b>Worksnaps API token</b>. I'll save it for you to use.\n\n"
        message += "To get your API token:\n"
        message += "1. Go to Profile & Settings >> Web Service API (Figure 1).\n"
        message += "2. Click the link Show my API Token. Then you will see the API token displayed in clear text (Figure 2).\n\n"
        message += "Thank you!"

    return message

def create_user_summary_message(user: WorksnapsUser, token: str, rate: str, currency: str) -> str:
    message = (
        f"<b>👤 Account Summary</b>\n\n"
        f"<b>Name</b>: {user.first_name} {user.last_name}\n"
        f"<b>Email</b>: {user.email}\n"
        f"<b>API Token</b>: <tg-spoiler>{token}</tg-spoiler>\n"
    )

    if rate and currency:
        message += f"<b>Rate</b>: <tg-spoiler>{rate} {currency}</tg-spoiler>"

    return message
