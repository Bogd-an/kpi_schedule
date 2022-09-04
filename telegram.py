import telebot, ssl
from aiohttp import web
from os import environ
from logic import (
    COMMAND,
    get_help,
    TIMETABLE,
    get_group,
    get_today,
    get_tomorrow,
    get_week,
    get_nextweek,
    get_info
)

bot = telebot.TeleBot(environ['TG_BOT_API_TOKEN'])

app = web.Application()

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

# - - -


@bot.message_handler(commands=['start'])
def func_start(message):
    bot.reply_to(message, 'Бот стартував. Щоб встановити групу: /група назва-групи')


@bot.message_handler(commands=COMMAND['help'])
def func_help(message):
    bot.reply_to(message, get_help(message.text), parse_mode = 'HTML', disable_web_page_preview=True)


@bot.message_handler(commands=COMMAND['group'])
def func_group(message):
    bot.reply_to(message, 'Пошук розкладу групи')
    bot.reply_to(message, get_group(message.chat.id, message.text), parse_mode='Markdown')


@bot.message_handler(commands=COMMAND['today'])
def func_today(message):
    bot.reply_to(message, get_today(message.chat.id), parse_mode='Markdown')


@bot.message_handler(commands=COMMAND['tomorrow'])
def func_tomorrow(message):
    bot.reply_to(message, get_tomorrow(message.chat.id), parse_mode='Markdown')


@bot.message_handler(commands=COMMAND['week'])
def func_week(message):
    bot.reply_to(message, get_week(message.chat.id), parse_mode='Markdown')


@bot.message_handler(commands=COMMAND['nextweek'])
def func_nextweek(message):
    bot.reply_to(message, get_nextweek(message.chat.id), parse_mode='Markdown')


@bot.message_handler(commands=COMMAND['timetable'])
def func_timetable(message):
    bot.reply_to(message, TIMETABLE, parse_mode='Markdown')

@bot.message_handler(commands=COMMAND['info'])
def func_timetable(message):
    bot.reply_to(message, get_info(message.chat.id))




# - - -

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(
    f'/etc/letsencrypt/live/{environ["DOMAIN_NAME"]}/fullchain.pem', 
    f'/etc/letsencrypt/live/{environ["DOMAIN_NAME"]}/privkey.pem'
)

# start aiohttp server (our bot)
web.run_app(
    app,
    host='0.0.0.0',
    port=8443,
    ssl_context=context,
)
