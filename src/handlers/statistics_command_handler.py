from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime, timedelta
from db.repositories.token_repository import get_tokens
from helpers.summary_data_helper import get_current_month_summary_data

async def statistics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wait_message = await update.message.reply_text("⏳ Please wait while we fetch your statistics...")

    user_id = update.effective_user.id
    tokens = get_tokens(user_id)

    if len(tokens) == 0:
        await wait_message.edit_text("You don't have any tokens.")
        return
    
    now = datetime.now()
    from_date = datetime(now.year, now.month, 1)
    to_date = from_date + timedelta(days=30)

    for token in tokens:
        summary_data = await get_current_month_summary_data(token.worksnaps_user_id, token.api_token, token.token_id, token.rate, token.currency, from_date, to_date)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=summary_data, parse_mode=ParseMode.HTML)

    await wait_message.delete()
