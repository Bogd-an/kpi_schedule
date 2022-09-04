[@K_P_I_schedule_bot](https://t.me/K_P_I_schedule_bot)

## Бот для зручного перегляду розкладу у Telegram

Можливості показу:
- розкладу на сьогодні
- розкладу на завтра
- розкладу на тиждень
- розкладу на наступнийТиждень
- дзвінків


TODO:
- [x] Перегляд розкладу групи
- [ ] Щоденні нагадування
- [ ] Зеркало у Matrix

* `telegram.py`  головний скрипта
* `mongo.py` скрипт завантаження та оновлення бази данних 

## Всстановлення

Інсталяція [mongodb](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-debian/)

```bash
sudo apt install python3
pip3 install certbot aiohttp cchardet aiodns pyTelegramBotAPI pymongo
```

Встановлюємо ssl сертефікати `sudo certbot`

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

Додаємо необхідні змінні оточення у кінець файлу `~/.bashrc`:
```
export DOMAIN_NAME='ВАШ_ДОМЕН'
export TG_BOT_API_TOKEN='ВАШ_ТОКЕН_БОТА'
```
Перезавантажуємо оболонку: `. ~/.bashrc`
