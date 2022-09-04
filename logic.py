import json
from pymongo import MongoClient
from datetime import datetime
from requests import get as req_get

BOT_VERSION='0.5'

db = MongoClient('localhost', 27017).telegram_bot

COMMAND_LIST = {
    'today':    [['сьогодні', 'today', 'td'],
        ['Команда для виклику розкладу на сьогодні']],
    'tomorrow': [['завтра', 'tomorrow', 'tm'],
        ['Команда для виклику розкладу на завтра']],
    'week':     [['тиждень', 'week', 'w'],
        ['Команда для виклику розкладу на поточний тиждень']],
    'nextweek': [['насттижд', 'nextweek', 'nw'],
        ['Команда для виклику розкладу на наступний тиждень']],
    'timetable':[['дзвінки', 'timetable', 'tt'],
        ['Команда для виклику розкладу дзвінків']],
    'help':     [['допомога', 'help', 'h'],
        ['Команда для виклику допомоги, можна передавати аргументом іншу команду']],
    'group':    [['група', 'group', 'g'],
        ['Команда для встановлення групи, згідно якої надсилатиметься розклад.',
         'Щоб скористатись відправте команду: /група НАЗВА-ГРУПИ']],
    'personal': [['персональний', 'personal','p'],
        ['Зараз в розробці',
         'Команда для вибору власних предметів',
         'Можете допомогти написанням функції на <a href="github.com//Bogd-an//kpi_schedule">github</a>']],
    'info':     [['інформація', 'info', 'i'],
        ['Інформація для дебагу']],
}

COMMAND = dict(zip(tuple(COMMAND_LIST.keys()), [row[0] for row in COMMAND_LIST.values()]))

HELP_STRING = '\n'.join(
    ['*Просто бот для КПІшного розкладу*\n'] +
    [' або '.join([f'/{i}' for i in row]) for row in COMMAND.values()]
)

TIMETABLE = '''
1 пара  08:30 - 10:05
2 пара  10:25 - 12:00
3 пара  12:20 - 13:55
4 пара  14:15 - 15:50
5 пара  16:10 - 17:45
'''

def get_help(text: str) -> str:
    text = text.split()
    if len(text) == 1:
        return HELP_STRING[:-64]
    if len(text) != 2:
        return 'Помилковий запит'
    text = text[1]
    if text[0] == '/':
        text = text[1:]
    for x in COMMAND_LIST:
        if text in COMMAND_LIST[x][0]:
            return '\n'.join(COMMAND_LIST[x][1])
    return 'Команду не знайдено'

def get_group(chat_id, text):

    text = text.split()
    if len(text) != 2:
        return 'Некоректна назва групи. Введіть згідно прикладу: /група АБ-01'

    group_info = db.groups.find_one({'name': text[1].upper()})

    if group_info == None:
        return 'Групу не знайдено. Спробуйте ввести згідно прикладу: /група АБ-01'

    if db.chats.find_one({'chat_id': chat_id}) == None:
        db.chats.insert_one({'chat_id': chat_id, 'group':group_info['name'], 'groupCode': group_info['id']})
    else:
        db.chats.update_one({'chat_id':chat_id}, {'$set': {'groupCode': group_info['id']}})
    
    return f'Групу встановлено. Ваш факультет {group_info["faculty"]} Можете скористатись командою /td'


def get_today(chat_id:str, table='chats') -> str:
    return '\n'.join(
        schedule_answer(chat_id, week_now(), day_now(), table=table)
    )


def get_tomorrow(chat_id:str, table='chats') -> str:
    week, day = week_now(), day_now()
    day = day + 1 if day != 6 else 0
    if day == 0:
        week = 'scheduleFirstWeek' if week == 'scheduleSecondWeek' else 'scheduleSecondWeek'
    return '\n'.join(
        schedule_answer(chat_id, week, day, table=table)
    )


def get_week(chat_id:str, table='chats') -> str:
    return '\n'.join(
        schedule_answer(chat_id, week_now(), table=table)
    )


def get_nextweek(chat_id:str, table='chats') -> str:
    week = 'scheduleFirstWeek' if week_now() == 'scheduleSecondWeek' else 'scheduleSecondWeek'
    return '\n'.join(
        schedule_answer(chat_id, week, table=table)
    )

def get_info(message_chat_id:str) -> str:
    print(db.chats.find_one({'chat_id': message_chat_id}))
    return '\n'.join(
        [
            f'Зараз {day_now()+1} день тижня',
            f'Розклад згідно {week_now()}',
            f'Розклад групи '+db.chats.find_one({'chat_id': message_chat_id})['group'],
            f'BOT VERSION={BOT_VERSION}'
        ]
    )


def schedule_answer(message_chat_id:str, week:str, day=None, table='chats') -> list:
    groupCode = db[table].find_one({'chat_id': message_chat_id})['groupCode']
    result = db.schedules.find_one({'groupCode': groupCode})[week]
    text = []
    if day == 6: return ['Неділя, вихідний🥳']
    if day != None: result = [result[day]]
    for res in result:
        text.append(f"     `{res['day']}`")
        for pair in res['pairs']:
            text.append(f"{pair['type']+': ' if pair['type'] != '' else ''}*{pair['time']}*")
            text.append(f"_{pair['name']}_")
            if pair['teacherName'] != '':
                word_ending = 'ка' if pair['teacherName'].split()[1][-1] in 'ая' else ''
                text.append(f"Лектор{word_ending}: {pair['teacherName']}")
            text.append('')
        if day == None: text.append('')
    if text[-2] == '     `\u0421\u0431`' and len(text) > 3:
        del text[-2]
    return text


def week_now() -> str:
    return ('scheduleFirstWeek', 'scheduleSecondWeek'
            )[(datetime.utcnow().isocalendar()[1]) % 2]
#        [req_get('https://schedule.kpi.ua/api/time/current').json()['data']['currentWeek']]

def day_now() -> int:
    return datetime.weekday(datetime.now())
#    return req_get('https://schedule.kpi.ua/api/time/current').json()['data']['currentDay']


