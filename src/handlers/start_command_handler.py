from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from db.repositories.user_repository import is_user_exists
from db.repositories.token_repository import is_token_exists
from messages import new_user_greeting_message, create_existing_user_greeting_message
from states.account_command_states import TOKEN

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_exists = is_user_exists(update.effective_user.id)
    token_exists = is_token_exists(update.effective_user.id)

    message = create_existing_user_greeting_message(token_exists) if user_exists else new_user_greeting_message

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    return TOKEN if not user_exists or not token_exists else ConversationHandler.END

async def ignore_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide your Worksnaps API token.")