import telebot
from aiohttp import web
import ssl
from pymongo import MongoClient
from datetime import datetime
import json
from requests import get as req_get
from os import environ

WEBHOOK_LISTEN = '0.0.0.0'
WEBHOOK_PORT = 8443

WEBHOOK_SSL_CERT = f'/etc/letsencrypt/live/{environ["DOMAIN_NAME"]}/fullchain.pem'
WEBHOOK_SSL_PRIV = f'/etc/letsencrypt/live/{environ["DOMAIN_NAME"]}/privkey.pem'

bot = telebot.TeleBot(environ['TG_BOT_API_TOKEN'])

app = web.Application()

db = MongoClient('localhost', 27017).telegram_bot

if False: # debug mode
    import logging
    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)


async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)




@bot.message_handler(commands=['start'])
def func_start(message):
    bot.reply_to(message, 'Бот стартував. Щоб встановити групу: /група назва-групи')



@bot.message_handler(commands=['help', 'h', 'допомога'])
def func_help(message):
    help_string = [
        '*Просто бот для КПІшного розкладу*\n',
        '/start',
        '/допомога або /help або /h',
        '/група або /group або /g',
        '/сьогодні або /today або /td',
        '/завтра /tomorrow або /tm',
        '/тиждень або /week або /w',
        '/насттижд або /nextweek або /nw',
        '/дзвінки /timetable або /tt'
    ]
    bot.reply_to(message, '\n'.join(help_string), parse_mode='Markdown')



@bot.message_handler(commands=['group', 'g', 'група'])
def func_group(message):
    text = message.text.split()
    if len(text) != 2:
        return bot.reply_to(message, 'Некоректна назва групи. Введіть згідно прикладу: /group АБ-01')

    bot.reply_to(message, 'Пошук розкладу групи')

    group_info = db.groups.find_one({'name': text[1].upper()})

    if group_info == None:
        return bot.reply_to(message, 'Групу не знайдено. Спробуйте ввести згідно прикладу: /group АБ-01')

    bot.reply_to(message, f'Ваш факультет {group_info["faculty"]}')
    if db.chats.find_one({'chat_id': message.chat.id}) == None:
        db.chats.insert_one({'chat_id': message.chat.id, 'groupCode': group_info['id']})
    else:
        db.chats.update_one({'chat_id':message.chat.id}, {'$set': {'groupCode': group_info['id']}})
    bot.reply_to(message, 'Групу встановлено. Можете скористатись командою /td')



@bot.message_handler(commands=['today', 'td', 'сьогодні'])
def func_today(message):
    bot.reply_to(message, '\n'.join(
        schedule_answer(message.chat.id, week_now(), day_now())
    ), parse_mode='Markdown')



@bot.message_handler(commands=['tomorrow', 'tm', 'завтра'])
def func_tomorrow(message):
    week, day = week_now(), day_now()
    day = day + 1 if day != 6 else 0
    if day == 0:
        week = 'scheduleFirstWeek' if week == 'scheduleSecondWeek' else 'scheduleSecondWeek'
    bot.reply_to(message, '\n'.join(
        schedule_answer(message.chat.id, week, day)
    ), parse_mode='Markdown')



@bot.message_handler(commands=['week', 'w', 'тиждень'])
def func_week(message):
    bot.reply_to(message, '\n'.join(
        schedule_answer(message.chat.id, week_now())
    ), parse_mode='Markdown')



@bot.message_handler(commands=['nextweek', 'nw', 'насттижд'])
def func_nextweek(message):
    week = 'scheduleFirstWeek' if week_now() == 'scheduleSecondWeek' else 'scheduleSecondWeek'
    bot.reply_to(message, '\n'.join(
        schedule_answer(message.chat.id, week)
    ), parse_mode='Markdown')



@bot.message_handler(commands=['timetable', 'tt', 'дзвінки'])
def func_timetable(message):
    bot.reply_to(message,
    '''
1 пара  08:30 - 10:05
2 пара  10:25 - 12:00
3 пара  12:20 - 13:55
4 пара  14:15 - 15:50
5 пара  16:10 - 17:45
    ''', 
    parse_mode='Markdown')


def schedule_answer(message_chat_id:str, week:str, day=None) -> list:
    groupCode = db.chats.find_one({'chat_id': message_chat_id})['groupCode']
    result = db.schedules.find_one({'groupCode': groupCode})[week]
    text = []
    if day != None: result = [result[day]]
    for res in result:
        text.append(f"     `{res['day']}`")
        for pair in res['pairs']:
            text.append(f"{pair['type']+': ' if pair['type'] != '' else ''}*{pair['time']}*")
            text.append(f"_{pair['name']}_")
            word_ending = 'ка' if pair['teacherName'].split()[1][-1] in 'ая' else ''
            text.append(f"Лектор{word_ending}: {pair['teacherName']}")
            text.append('')
        if day == None: text.append('')
    if text[-2] == '     `\u0421\u0431`' and len(text) > 3:
        del text[-2]
    return text



def week_now() -> str:
    return ('scheduleFirstWeek', 'scheduleSecondWeek'
            )[(datetime.utcnow().isocalendar()[1]+1) % 2]
#        [req_get('https://schedule.kpi.ua/api/time/current').json()['data']['currentWeek']]

def day_now() -> int:
    return datetime.weekday(datetime.now())
#    return req_get.('https://schedule.kpi.ua/api/time/current').json()['data']['currentDay']




# - - -

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

# start aiohttp server (our bot)
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
