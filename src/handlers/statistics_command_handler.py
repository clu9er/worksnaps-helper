from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime
from db.repositories.token_repository import get_tokens
from helpers.summary_data_helper import get_summary_data
from utils.date_utils import get_today_date_range, get_month_date_range

async def statistics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "📅 Choose period: "
    reply_markup = [
        [
            InlineKeyboardButton("Today", callback_data="today_summary"),
            InlineKeyboardButton("This month", callback_data="month_summary"),
        ],
    ]

    await update.message.reply_text(text=message, reply_markup=InlineKeyboardMarkup(reply_markup), parse_mode=ParseMode.HTML)

async def handle_month_summary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_range = get_month_date_range()

    await get_summary_report(update, context, date_range[0], date_range[1])
    await update.callback_query.answer()

async def handle_daily_summary_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_range = get_today_date_range()

    await get_summary_report(update, context, date_range[0], date_range[1], False)
    await update.callback_query.answer()

async def get_summary_report(update: Update, context: ContextTypes.DEFAULT_TYPE, from_date: datetime, to_date: datetime, with_cache: bool = True):
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)

    wait_message_text = "⏳ Please wait while we fetch your statistics..."
    wait_message = await context.bot.send_message(chat_id=update.effective_chat.id, text=wait_message_text, parse_mode=ParseMode.HTML)

    user_id = update.effective_user.id
    tokens = get_tokens(user_id)

    if len(tokens) == 0:
        await wait_message_text.edit_text("You don't have any tokens.")
        return

    summary_data = ""

    for token in tokens:
        summary_data += await get_summary_data(token.worksnaps_user_id, token.api_token, token.token_id, token.rate, token.currency, from_date, to_date, with_cache)
        summary_data += "\n\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=summary_data, parse_mode=ParseMode.HTML)

    await wait_message.delete()
