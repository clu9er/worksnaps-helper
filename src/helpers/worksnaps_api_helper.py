import json
import logging
import grequests
import base64
import xml.etree.ElementTree as ET

from typing import List
from datetime import datetime

from helpers.parse_helper import parse_summary_xml, parse_user_xml

from models.summary import Summary
from models.worksnaps_user import WorksnapsUser
from models.project import Project

from db.redis.main import client as redis, ttl

from config_reader import config

from utils.date_utils import get_adjusted_timestamp
from utils.aes_cipher import AESCipher

def generate_authorization_header(token: str):
    auth_hash = base64.b64encode((token + ":ignored").encode()).decode()
    return auth_hash

async def get_projects_summary_report(worksnaps_user_id: int, token: str, from_date: datetime, to_date: datetime, projects: List[Project], report_type: str, with_cache: bool = True) -> List[Summary]:
    if with_cache:
        cached_value = redis.get(f"summary:{worksnaps_user_id}")
        if cached_value is not None:
            summaries = [Summary.from_json(summary) for summary in json.loads(cached_value)]
            return summaries

    from_timestamp = get_adjusted_timestamp(from_date)
    to_timestamp = get_adjusted_timestamp(to_date)

    urls = []

    for project in projects:
        url = f'{config.worksnaps.api_url}/projects/{project.project_id}/reports?name={report_type}&from_timestamp={from_timestamp}&to_timestamp={to_timestamp}&user_ids={worksnaps_user_id}'
        urls.append(grequests.get(url, headers={'Authorization': f'Basic {generate_authorization_header(token)}' }))

    responses = grequests.map(urls)

    result = []
    for response in responses:
        if response and response.content:
             summaries = parse_summary_xml(response.content, projects)
             result.extend(summaries)
    
    if with_cache:
        redis.set(f"summary:{worksnaps_user_id}", json.dumps([summary.to_json() for summary in result]), ex=ttl)

    return result

async def get_projects(token: str, token_id: int) -> List[Project]:

    cached_value = redis.get(f"projects:{token_id}")
    if cached_value is not None:
        return [Project.from_json(project) for project in json.loads(cached_value)]
    
    url = f'{config.worksnaps.api_url}/projects.xml'
    auth_hash = generate_authorization_header(token)

    headers = {
        'Authorization': f'Basic {auth_hash}',
    }

    req = grequests.get(url, headers=headers)
    response = grequests.map([req])[0]

    if response and response.status_code == 200:
        result = []
        root = ET.fromstring(response.content)
        for item in root.findall('project'):
            project = Project(item.find('id').text, item.find('name').text)
            result.append(project)

        redis.set(f"projects:{token_id}", json.dumps([project.to_json() for project in result]), ex=ttl)

        return result
    else:
        logging.error(f"Failed to fetch projects: {response.status_code} - {response.content if response else 'No response'}")
        return None

async def get_worksnaps_user(token: str, token_id: int) -> WorksnapsUser:
    try:
        url = f'{config.worksnaps.api_url}/me.xml'
        auth_hash = generate_authorization_header(token)

        cached_value = redis.get(f'user:{token_id}')
        if cached_value:
            return WorksnapsUser.from_json(json.loads(cached_value))

        headers = {
            'Authorization': f'Basic {auth_hash}',
        }

        req = grequests.get(url, headers=headers)

        response = grequests.map([req])[0]

        if response and response.content:
            user = parse_user_xml(response.content)

            cipher = AESCipher(config.encryption.key)
            user.api_token = cipher.encrypt(user.api_token)

            if token_id is not None:
                redis.set(f'user:{token_id}', json.dumps(user.to_json()), ex=ttl)

            return user

        return None

    except Exception as e:
        logging.error(f"Failed to fetch user: {e}")
        return None
