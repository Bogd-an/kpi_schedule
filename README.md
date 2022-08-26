# kpi_schedule
Tg bot python

## Бот для зручного перегляду розкладу у Telegram

`main.py`  головний скрипта
`mongo.py` скрипт завантаження та оновлення бази данних 

### Всстановлення

Інсталяція [mongodb](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-debian/)

```bash
sudo apt install python3
pip3 install certbot aiohttp cchardet aiodns pyTelegramBotAPI pymongo
```

Встановлюємо ssl сертефікати
`sudo certbot`

Додаємо дозвіл на читання сертифікатів
```bash
groupadd letsencrypt
usermod -a -G letsencrypt КОРИСТУВАЧ_ЯКИЙ_ЗАПУСКАЄ_СКРИПТ
chgrp -R letsencrypt /etc/letsencrypt/
chown -R КОРИСТУВАЧ_ЯКИЙ_ЗАПУСКАЄ_СКРИПТ:letsencrypt /etc/letsencrypt/
```

Реєструємо свого бота https://t.me/botfather/ та надсилаємо про нього інформацію:
`https://api.telegram.org/botYOUR-TOKEN/setWebhook?url=https://YOUR_DOMAIN:8443/YOUR-TOKEN/`

Відкриваємо порт для боту `sudo ufw allow 8443`

Необхідні змінні оточення:
* DOMAIN_NAME
* TG_BOT_API_TOKEN
