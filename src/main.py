import logging
import datetime

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from config_reader import config
from bot import start_command, error, statistics_command, receive_token, ignore_commands, tokens_command, button_click, rate_received, token_received

from states.start_command_states import WAITING_FOR_TOKEN
from states.token_command_states import RATE, START, TOKEN

from db.main import migrate_database

from scheduler import send_day_summary, send_month_summary

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info('Starting bot...')
    app = Application.builder().token(config.telegram.token).build()

    migrate_database()

    start_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            WAITING_FOR_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_token)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, ignore_commands)],
    )

    tokens_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('tokens', tokens_command)],
        states={
            START: [
                CommandHandler('tokens', tokens_command),
                CallbackQueryHandler(button_click)
            ],
            RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, rate_received)],
            TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, token_received)],
        },
        fallbacks=[]
    )

    app.add_handler(start_conversation_handler)
    app.add_handler(tokens_conversation_handler)
    app.add_handler(CommandHandler('statistics', statistics_command))

    app.add_handler(CallbackQueryHandler(button_click))

    app.add_error_handler(error)
    
    job_queue = app.job_queue

    job_queue.run_daily(send_day_summary, datetime.time(hour=19, minute=10))
    job_queue.run_daily(send_month_summary, datetime.time(hour=19, minute=10, second=30))

    app.run_polling(poll_interval=3)
