from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from db.repositories.user_repository import is_user_exists, insert_user
from db.repositories.token_repository import insert_token, get_tokens, add_rate, delete_token, get_token
from helpers.worksnaps_api_helper import get_worksnaps_user, get_projects, get_projects_summary_report
from helpers.summary_data_helper import get_current_day_project_summary, create_daily_report_message
from messages import create_user_summary_message
from models.project import Project
from states.account_command_states import RATE, START, TOKEN
from utils.date_utils import get_today_date_range
from typing import List
from models.summary import Summary
from collections import defaultdict

async def accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE, replaced: bool = False):
    user_id = update.effective_user.id
    tokens = get_tokens(user_id)

    if len(tokens) == 0 or tokens is None:
        await update.message.reply_text("You don't have any accounts.")
    else:
        keyboard = []
        row = []
        for i, token in enumerate(tokens):
            user_data = await get_worksnaps_user(token.api_token, token.token_id)
            button_text = user_data.email
            callback_data = f"account {token.token_id}"
            row.append(InlineKeyboardButton(button_text, callback_data=callback_data))

            if len(row) == 2:
                keyboard.append(row)
                row = []
        
        if row: 
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton("➕ Add new account", callback_data="add_account")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        message = f"👤 Please select an account to view:\n\n"

        if replaced:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=update.effective_message.message_id, text=message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        return START


async def receive_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text
    worksnaps_user = await get_worksnaps_user(token, None)

    user_id = update.effective_user.id
    user_exists = is_user_exists(update.effective_user.id)

    if worksnaps_user is None:
        await update.message.reply_text("❌ Invalid token. Please try again.")
        return TOKEN

    worksnaps_user_id = worksnaps_user.user_id

    if user_exists:
        insert_token(user_id, token, worksnaps_user_id)
    else:
        insert_user(update.effective_user.id, update.effective_user.username, update.effective_user.first_name, update.effective_user.last_name, token, worksnaps_user_id)

    await update.message.reply_text("✅ Token received. You can now use the <code>/statistics</code> command to get your projects summary.", parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def rate_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    rate = str(update.message.text.split(' ')[0])
    currency = update.message.text.split(' ')[1]

    token = context.user_data['token_id']
    add_rate(token, rate, currency,user_id)

    await update.message.reply_text("✅ Rate added. \n If you want to remove it later, just send 0 as your rate next time.", parse_mode=ParseMode.HTML)
    return START

async def project_report_for_current_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    project = Project(
        project_id=query.data.split(' ')[1],
        project_name=query.data.split(' ')[2]
    )

    token_id = context.user_data['token_id']
    token = get_token(token_id)

    tasks = await get_current_day_project_summary(project, token.api_token, token_id, context)
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('📅 Create daily report template', callback_data='create_daily_report')],
        [InlineKeyboardButton('🔙 Back to projects', callback_data=f'tasks_report {token_id}')]
    ])

    await query.edit_message_text(tasks, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    await query.answer()

    return START

async def handle_add_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['token_id'] = query.data.split(' ')[1]

    await query.message.reply_text('💰 Please enter your rate along with the currency (e.g., 50 USD):')
    await query.answer()

    return RATE

async def handle_delete_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    token_id = query.data.split(' ')[1]

    delete_token(token_id)

    await query.edit_message_text('✅ Account deleted successfully from your list.', parse_mode=ParseMode.HTML)
    await query.answer()

    return ConversationHandler.END

async def handle_add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.message.reply_text('💡 Please enter your Worksnaps API token:')
    await query.answer()

    return TOKEN

async def handle_view_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    token_id = query.data.split(' ')[1]
    token = get_token(token_id)

    context.user_data['token_id'] = token_id

    user_data = await get_worksnaps_user(token.api_token, token_id)
    message = create_user_summary_message(user_data, token.api_token, token.rate, token.currency)

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('Add or edit rate 💰', callback_data=f'add_rate {token.token_id}'),
            InlineKeyboardButton('Delete 🗑️', callback_data=f'delete_token {token.token_id}'),
        ],
        [
            InlineKeyboardButton('View tasks report 📝', callback_data=f'tasks_report {token.token_id}'),
            InlineKeyboardButton("Today's Project Report 🗂️", callback_data='daily_reports')
        ],
        [
            InlineKeyboardButton('Back to accounts 🔙', callback_data='back')
        ]
    ])

    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    await query.answer()

async def handle_view_tasks_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    token_id = query.data.split(' ')[1]
    token = get_token(token_id)
    projects = await get_projects(token.api_token, token_id)

    message = '📝 Choose project to view tasks report: \n\n'

    context.user_data['token_id'] = token_id

    buttons = []
    for i in range(0, len(projects), 2):
        row = [InlineKeyboardButton(projects[i].project_name, callback_data=f'project {projects[i].project_id} {projects[i].project_name}')]
        if i + 1 < len(projects):
            row.append(InlineKeyboardButton(projects[i + 1].project_name, callback_data=f'project {projects[i + 1].project_id} {projects[i + 1].project_name}'))
        buttons.append(row)

    buttons.append([InlineKeyboardButton('Back to account 🔙', callback_data=f'account {token.token_id}')])
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    await query.answer()

    return START

async def handle_create_daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    username = query.from_user.username

    tasks = context.user_data['tasks']
    token_id = context.user_data['token_id']

    message = create_daily_report_message(tasks, username)

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('🔙 Back to projects', callback_data=f'tasks_report {token_id}')]
    ])

    await query.edit_message_text(message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    await query.answer()
    return START

async def handle_create_daily_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.callback_query.from_user.username
    token_id = context.user_data['token_id']
    token = get_token(token_id)

    projects = await get_projects(token.api_token, token.token_id)

    from_date, to_date = get_today_date_range()
    summaries = await get_projects_summary_report(token.worksnaps_user_id, token.api_token, from_date, to_date, projects, 'time_summary', False)

    grouped_summaries = group_summaries_by_project(summaries)

    if len(grouped_summaries) == 0:
        await update.callback_query.answer('No tasks found for the current day 😢')
        return START

    for summary in grouped_summaries:
        message = create_daily_report_message(summary, username)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)
        
    await update.callback_query.answer('✅ Daily reports created successfully')
    return START

def group_summaries_by_project(summaries: List[Summary]):
    grouped_summaries = defaultdict(list)
    
    for summary in summaries:
        project_name = summary.project_name
        grouped_summaries[project_name].append(summary)
    
    project_lists = list(grouped_summaries.values())
    
    return project_lists

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await accounts_command(update, context, True)

async def handle_project_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await project_report_for_current_day(update, context)