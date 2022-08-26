from pymongo import MongoClient
import json
from requests import get as req_get
import logging as log
from datetime import datetime

dt_now = lambda: str(datetime.now())[:-7]
log.basicConfig(filename="log2.txt")

"""
{
    # SCHEME
    # pymongo.MongoClient('localhost', 27017).telegram_bot
    # API_LINK = https://schedule.kpi.ua/api/schedule/
    'telegram_bot': {

        'schedules': [
        #[ row['data'] for row in [( {API_LINK}lessons?groupId={id} ) for id in groups['id']] ]
            {
                'groupCode': "str == groups['id']",
                'scheduleFirstWeek':[
                    {
                        'day': 'str',
                        'pairs':[
                            {
                                'teacherName' : 'str',
                                'lecturerId': "str == lecturers['id']",
                                'type': 'str',
                                'time': 'str',
                                'name': 'str',
                                'place': 'str',
                                'tag': 'str'
                            },
                            '...'
                        ]
                    }
                ]
                'scheduleSecondWeek': { 
                    '...' 
                }
            },
            '...'
        ],

        'lecturers': [
        # [ for i in ( {API_LINK}lecturer/list )['data'] ]
            {
                'id': 'str',
                'name': 'str'
            },
            '...'
        ],

        'groups': [
        # [ for i in ( {API_LINK}groups )['data'] ]
            {
                'id': 'str',
                'name': 'str',
                'faculty': 'str'
            },
            '...'
        ],

        'chats':[
            {
                'chat_id': 'str',
                'groupCode': 'str'
            },
            '...'            
        ]
    }
}
"""


db = MongoClient('localhost', 27017).telegram_bot

schedules_db = db.schedules
lecturers_db = db.lecturers
groups_db = db.groups

def get_data_json(src:str) -> list:
    try:
        return req_get(f'https://schedule.kpi.ua/api/schedule/{src}').json()
    except json.JSONDecodeError:
        log.error(f'{dt_now()} get_data_json except with {src=}')
        return None


def groups_db_update() -> None:
    result = get_data_json('groups')
    if result != None:
        try: 
            result = result['data']
        except KeyError:
            log.error(f'{dt_now()} groups_db_update except with {result=}')
        else:
            if groups_db.find_one() == None:
                groups_db.insert_many(result)
            else:
                for row in result:
                    db_request = groups_db.find_one({'name': row['name']})
                    if db_request == None:
                        groups_db.insert_one(row)
                    elif db_request['id'] != row['id']:
                        log.info(f"{dt_now()} groups_db {row['name']}: {db_request['id']} -> {row['id']}")
                        groups_db.update_one({'name': row['name']}, {'$set': {'id': row['id']}})


def lecturers_db_update() -> None:
    result = get_data_json('lecturer/list')
    if result != None:
        try: 
            result = result['data']
        except KeyError:
            log.error(f'{dt_now()} lecturers_db_update except with {result=}')
        else:
            if lecturers_db.find_one() == None:
                # lecturers_db is empty
                lecturers_db.insert_many(result)
            else:
                for row in result:
                    db_request = lecturers_db.find_one({'name': row['name']})
                    if db_request == None:
                        lecturers_db.insert_one(row)
                    elif db_request['id'] != row['id']:
                        log.info(f"{dt_now()} lecturers_db {row['name']}: {db_request['id']} -> {row['id']}")
                        lecturers_db.update_one({'name': row['name']}, {'$set': {'id': row['id']}})


def schedules_db_update() -> None:
    for row in groups_db.find({}, {'id':1, '_id':0}):
        result = get_data_json(f'lessons?groupId={row["id"]}')
        if result != None:
            try: 
                result = result['data']
            except KeyError:
                log.error(f'{dt_now()} schedules_db_update except with {result=}')
            else:
                db_request = schedules_db.find_one({'groupCode': result["groupCode"]})
                if db_request == None:
                    schedules_db.insert_one(result)
                elif db_request != result:
                    log.info(f"{dt_now()} schedules_db {result['groupCode']}: {db_request} -> {result}")
                    schedules_db.update_one({'groupCode': result["groupCode"]},
                    {'$set': {'scheduleFirstWeek': result['scheduleFirstWeek'], 'scheduleSecondWeek': result['scheduleSecondWeek']}})



if __name__ == '__main__':
    print('Обновлення полів в базі данних')
    print('Якщо данні відрізняються, оновляться')
    print('Якщо данні відсутні, додадуться')
    groups_db_update()
    lecturers_db_update()
    schedules_db_update()
