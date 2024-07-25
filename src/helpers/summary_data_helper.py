from helpers.worksnaps_api_helper import get_projects_summary_report

from datetime import datetime

async def get_summary_data(worksnaps_user_id: str, token: str, rate: float, currency: str, from_date: datetime, to_date: datetime, with_cache: bool = True) -> str:
    total_minutes = 0
    summaries = await get_projects_summary_report(worksnaps_user_id, token, from_date, to_date, with_cache)
    
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
