import logging as logger

from db.repositories.token_repository import get_all_tokens
from helpers.summary_data_helper import get_current_month_summary_data

from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from datetime import datetime, time, timedelta

async def send_day_summary(context: CallbackContext) -> None:
    try:
        bot = context.bot
        tokens = get_all_tokens()

        now = datetime.now()
        from_date = datetime.combine(now.date(), time.min)
        to_date = datetime.combine(now.date(), time.max)

        for token in tokens:
            message = await get_current_month_summary_data(token.worksnaps_user_id, token.api_token, token.token_id, token.rate, token.currency, from_date, to_date, False)
            await bot.send_message(chat_id=token.user_id, text=message, parse_mode=ParseMode.HTML, disable_notification=True)

    except Exception as e:
        logger.error(f"Error sending daily summary: {e}")

async def send_month_summary(context: CallbackContext) -> None:
    try:
        bot = context.bot
        tokens = get_all_tokens()

        now = datetime.now()
        from_date = datetime(now.year, now.month, 1)
        to_date = from_date + timedelta(days=30)

        for token in tokens:
            message = await get_current_month_summary_data(token.worksnaps_user_id, token.api_token, token.token_id, token.rate, token.currency, from_date, to_date, False)
            await bot.send_message(chat_id=token.user_id, text=message, parse_mode=ParseMode.HTML, disable_notification=True)

    except Exception as e:
        logger.error(f"Error sending monthly summary: {e}")
