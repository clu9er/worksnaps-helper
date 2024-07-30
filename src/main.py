import logging
import datetime

import handlers.error_handler
import handlers.start_command_handler
import handlers.statistics_command_handler
import handlers.account_command_handler

from config_reader import config
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from states.account_command_states import RATE, START, TOKEN, PROJECT

from db.main import migrate_database

from scheduler import send_day_summary, send_month_summary

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info('Starting bot...')
    app = Application.builder().token(config.telegram.token).build()

    migrate_database()

    start_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start_command_handler.start_command)],
        states={
            TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.account_command_handler.receive_token)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, handlers.start_command_handler.ignore_commands)],
    )

    tokens_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('accounts', handlers.account_command_handler.accounts_command)],
        states={
            START: [
                CommandHandler('accounts', handlers.account_command_handler.accounts_command),
                CallbackQueryHandler(handlers.account_command_handler.handle_add_rate, pattern='^add_rate '),
                CallbackQueryHandler(handlers.account_command_handler.handle_delete_token, pattern='^delete_token '),
                CallbackQueryHandler(handlers.account_command_handler.handle_add_account, pattern='^add_account$'),
                CallbackQueryHandler(handlers.account_command_handler.handle_view_account, pattern='^account '),
                CallbackQueryHandler(handlers.account_command_handler.handle_view_tasks_report, pattern='^tasks_report '),
                CallbackQueryHandler(handlers.account_command_handler.handle_back, pattern='^back$'),
                CallbackQueryHandler(handlers.account_command_handler.handle_project_report, pattern='^project '),
                CallbackQueryHandler(handlers.account_command_handler.handle_create_daily_report, pattern='^create_daily_report')
            ],
            RATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.account_command_handler.rate_received)
            ],
            TOKEN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.account_command_handler.receive_token)
            ]
        },
        fallbacks=[]
    )

    app.add_handler(start_conversation_handler)
    app.add_handler(tokens_conversation_handler)

    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_add_rate, pattern='^add_rate '))
    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_delete_token, pattern='^delete_token '))
    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_add_account, pattern='^add_account$'))
    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_view_account, pattern='^account '))
    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_view_tasks_report, pattern='^tasks_report '))
    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_back, pattern='^back$'))
    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_project_report, pattern='^project '))
    app.add_handler(CallbackQueryHandler(handlers.account_command_handler.handle_create_daily_report, pattern='^create_daily_report'))

    app.add_handler(CommandHandler('statistics', handlers.statistics_command_handler.statistics_command))

    app.add_error_handler(handlers.error_handler.error)
    
    job_queue = app.job_queue

    weekdays = (0, 1, 2, 3, 4)
    job_queue.run_daily(send_day_summary, datetime.time(hour=19, minute=10), days=weekdays)
    job_queue.run_daily(send_month_summary, datetime.time(hour=19, minute=10, second=30), days=weekdays)

    app.run_polling(poll_interval=3)
