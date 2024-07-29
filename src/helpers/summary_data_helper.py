from helpers.worksnaps_api_helper import get_projects_summary_report, get_projects, get_worksnaps_user

from telegram.ext import ContextTypes

from datetime import datetime, time
from models.project import Project
from models.summary import Summary
from typing import List

async def get_current_month_summary_data(worksnaps_user_id: str, token: str, token_id: int, rate: float, currency: str, from_date: datetime, to_date: datetime, with_cache: bool = True) -> str:
    total_minutes = 0

    projects = await get_projects(token, token_id)
    summaries = await get_projects_summary_report(worksnaps_user_id, token, from_date, to_date, projects, 'time_summary', with_cache)
    
    project_details = {}
    
    for summary in summaries:
        project_name = summary.project_name
        duration_in_minutes = summary.duration_in_minutes
        
        if project_name not in project_details:
            project_details[project_name] = 0
        
        project_details[project_name] += duration_in_minutes
        total_minutes += duration_in_minutes
    
    total_hours = total_minutes // 60
    total_minutes_remainder = total_minutes % 60

    is_monthly = from_date.day != to_date.day
    period = "Month" if is_monthly else "Day"

    message_lines = [
        f"📊 <b>Project Summary for the Current {period}</b> 📅",
        f"----------------------------------------"
    ]
    
    for project, minutes in project_details.items():
        hours = minutes // 60
        minutes_remainder = minutes % 60
        message_lines.append(f"🔹 <b>{project}</b>: {hours} hours and {minutes_remainder} minutes")
    
    message_lines.append(f"----------------------------------------")
    message_lines.append(f"⏰ <b>Total Time Spent</b>: {total_hours} hours and {total_minutes_remainder} minutes")
    
    if rate and rate > 0 and currency: 
        message_lines.append(f"💰 <b>Total Salary</b>: {total_hours * rate} {currency}")
    
    message = "\n".join(message_lines)
    
    return message

async def get_current_day_project_summary(project: Project, token: str, context: ContextTypes.DEFAULT_TYPE) -> str:
    now = datetime.now()

    from_date = datetime.combine(datetime(now.year, now.month, now.day), time.min)
    to_date = datetime.combine(datetime(now.year, now.month, now.day), time.max)
    
    worksnaps_user = await get_worksnaps_user(token)
    
    summaries = await get_projects_summary_report(worksnaps_user.user_id, token, from_date, to_date, [project], 'time_summary', False)
    message = generate_task_report_message(project.project_name, summaries)

    context.user_data['tasks'] = summaries
    
    return message

def generate_task_report_message(project_name: str, summaries: List[Summary]) -> str:
    message = f"📋 <b>Project:</b> {project_name}\n\n"
    message += "📝 <b>Tasks:</b>\n"

    if not summaries:
        message += "No tasks found for today. 🤷‍♂️"
    else:
        for summary in summaries:
            message += f"--------------------\n"
            message += f"🕒 <b>{summary.task_name}</b>\n"
            message += f"⏳ Duration: {summary.duration_in_minutes} minutes\n"
            message += f"--------------------\n"
        message += "Keep up the good work! 💪"

    return message

def create_daily_report_message(summaries: List[Summary], userame: str) -> str:
    message = ""

    if not summaries:
        message += "No tasks found for today. 🤷‍♂️"
        return message

    current_day = datetime.now().strftime('%d%m%Y')
    message = f"#dailyreport #day{current_day} #{userame}\n\n"

    for summary in summaries:
        message += f"{summary.duration_in_minutes} mins\n"
        message += f"<b>{summary.task_name}</b> - \n\n"
    
    return message