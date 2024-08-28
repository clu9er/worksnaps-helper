import logging as logger

from db.repositories.token_repository import get_all_tokens
from helpers.summary_data_helper import get_summary_data

from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from utils.date_utils import get_today_date_range, get_month_date_range

async def send_day_summary(context: CallbackContext) -> None:
    try:
        bot = context.bot
        tokens = get_all_tokens()

        from_date, to_date = get_today_date_range()

        message = ""

        for token in tokens:
            message += await get_summary_data(token.worksnaps_user_id, token.api_token, token.token_id, token.rate, token.currency, from_date, to_date, False)
            message += "\n\n"

        await bot.send_message(chat_id=token.user_id, text=message, parse_mode=ParseMode.HTML, disable_notification=True)

    except Exception as e:
        logger.error(f"Error sending daily summary: {e}")

async def send_month_summary(context: CallbackContext) -> None:
    try:
        bot = context.bot
        tokens = get_all_tokens()

        from_date, to_date = get_month_date_range()

        message = ""

        for token in tokens:
            message += await get_summary_data(token.worksnaps_user_id, token.api_token, token.token_id, token.rate, token.currency, from_date, to_date, False)
            message += "\n\n"

        await bot.send_message(chat_id=token.user_id, text=message, parse_mode=ParseMode.HTML, disable_notification=True)

    except Exception as e:
        logger.error(f"Error sending monthly summary: {e}")
