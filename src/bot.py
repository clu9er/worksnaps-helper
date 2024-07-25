import logging

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from helpers.summary_data_helper import get_summary_data
from helpers.worksnaps_api_helper import get_worksnaps_user

from states.start_command_states import WAITING_FOR_TOKEN
from states.token_command_states import RATE, START, TOKEN

from db.repositories.user_repository import is_user_exists, insert_user
from db.repositories.token_repository import get_tokens, add_rate, delete_token, insert_token, is_token_exists

from messages import new_user_greeting_message, create_user_summary_message, create_existing_user_greeting_message

from datetime import datetime, timezone, timedelta

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_exists = is_user_exists(update.effective_user.id)
    token_exists = is_token_exists(update.effective_user.id)

    message = create_existing_user_greeting_message(token_exists) if user_exists else new_user_greeting_message

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

    return WAITING_FOR_TOKEN if not user_exists or not token_exists else ConversationHandler.END

async def receive_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text
    worksnaps_user = await get_worksnaps_user(token)

    user_id = update.effective_user.id
    user_exists = is_user_exists(update.effective_user.id)

    if worksnaps_user is None:
        await update.message.reply_text("❌ Invalid token. Please try again.")
        return WAITING_FOR_TOKEN

    worksnaps_user_id = worksnaps_user.user_id

    if user_exists:
        insert_token(user_id, token, worksnaps_user_id)
    else:
        insert_user(update.effective_user.id, update.effective_user.username, update.effective_user.first_name, update.effective_user.last_name, token, worksnaps_user_id)

    await update.message.reply_text("✅ Token received. You can now use the <code>/statistics</code> command to get your projects summary.", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def ignore_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please provide your Worksnaps API token.")

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
        summary_data = await get_summary_data(token.worksnaps_user_id, token.api_token, token.rate, token.currency, from_date, to_date)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=summary_data, parse_mode=ParseMode.HTML)

    await wait_message.delete()

async def tokens_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tokens = get_tokens(user_id)
    
    if len(tokens) == 0 or tokens is None:
        await update.message.reply_text("You don't have any tokens.")
    else:
        for token in tokens:
            user_data = await get_worksnaps_user(token.api_token)
            message = create_user_summary_message(user_data)

            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton('Add or edit rate 💰', callback_data=f'add_rate {token.token_id}'),
                    InlineKeyboardButton('Delete 🗑️', callback_data=f'delete_token {token.token_id}'),
                ],
                [InlineKeyboardButton('Add new token ➕', callback_data=f'add_token')]
            ])

            await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return START

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    query_data = query.data.split(' ')

    if query_data[0] == 'add_rate':
        context.user_data['token'] = query_data[1]

        await query.message.reply_text('💰 Please enter your rate along with the currency (e.g., 50 USD):')
        await query.answer()

        return RATE

    if query_data[0] == 'delete_token':
        token_id = query_data[1]
        delete_token(token_id)

        await query.message.reply_text('✅ Token deleted.', parse_mode=ParseMode.HTML)
        await query.answer()

        return ConversationHandler.END
    
    if query_data[0] == 'add_token':
        await query.message.reply_text('💡 Please enter your Worksnaps API token:')
        await query.answer()

        return TOKEN


async def rate_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rate = update.message.text.split(' ')[0]
    currency = update.message.text.split(' ')[1]

    token = context.user_data['token']
    add_rate(token, rate, currency)

    await update.message.reply_text("✅ Rate added. \n If you want to remove it later, just send 0 as your rate next time.", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def token_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text
    user_id = update.effective_user.id

    worksnaps_user = await get_worksnaps_user(token)

    if worksnaps_user is None:
        await update.message.reply_text("❌ Invalid token. Please try again.")
        return TOKEN

    insert_token(user_id, token, worksnaps_user.user_id)

    await update.message.reply_text("✅ Token added.", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} caused an error {context.error}')
    await update.message.reply_text('❌ Something went wrong. Please try again later.')
