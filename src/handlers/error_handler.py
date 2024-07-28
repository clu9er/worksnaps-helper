import logging
from telegram import Update
from telegram.ext import ContextTypes

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} caused an error {context.error}')
    if update.message is not None:
        await update.message.reply_text('❌ Something went wrong. Please try again later.')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='❌ Something went wrong. Please try again later.')
