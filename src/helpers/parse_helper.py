import xml.etree.ElementTree as ET
from typing import List
from models.summary import Summary
from models.project import Project
from models.worksnaps_user import WorksnapsUser

def parse_summary_xml(xml_data: bytes, projects: List[Project]) -> List[Summary]:
    root = ET.fromstring(xml_data)
    
    summary_items = []
    
    for entry in root.findall('time_entry'):
        user_id = entry.find('user_id').text
        project_id = entry.find('project_id').text
        duration_in_minutes = int(entry.find('duration_in_minutes').text)
        task_id = entry.find('task_id').text
        task_name = entry.find('task_name').text
        user_comment = entry.find('user_comment').text if entry.find('user_comment') is not None else ''
        time_entry_type = entry.find('time_entry_type').text
        project_name = next((project for project in projects if project.project_id == project_id), None).project_name
        
        item = Summary(
            user_id=user_id,
            project_id=project_id,
            project_name=project_name,
            duration_in_minutes=duration_in_minutes,
            task_id=task_id,
            task_name=task_name,
            user_comment=user_comment,
            time_entry_type=time_entry_type
        )
        summary_items.append(item)
    
    return summary_items

def parse_user_xml(xml_data: bytes) -> WorksnapsUser:
    user = ET.fromstring(xml_data)
    
    user_id = user.find('id').text
    first_name = user.find('first_name').text
    last_name = user.find('last_name').text
    email = user.find('email').text
    api_token = user.find('api_token').text
    
    result = WorksnapsUser(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        api_token=api_token
    )
    
    return result