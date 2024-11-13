# WhatsApp бот для создания и отправки напоминаний
***

## Структура проекта

### Реализовано

- Создание напоминания.
- Получение списка напоминаний.
- Удаления напоминания по его id.
- Создание повторяющихся напоминаний (ежедневных, еженедельных).

### Файлы и дерриктории
- src - директория с серверной частью приложения. Здесь находятся все API-эндпоинты, модели данных и логика обработки запросов.
- .env.template - шаблон переменных окружения.
- docker-compose.yaml - настройки docker-compose.
- requirements.txt - зависимости Python.

***

### Стек технологий:

- Python
- FastAPI
- Uvicorn
- Celery
- Docker
- Postgres
- SQLAlchemy
- Ngrok
- Twilio

***

## Установка и запуск проекта


### Предварительно 

1. Получить `Twilio Auth Token` и `Twilio SID`. Для этого необходимо зарегистрироваться на 
[twilio.com](https://www.twilio.com) и перейти на страницу 
[console](https://www.twilio.com/console).

2. Получить `Ngrok Auth Token`. Для этого нужно зарегистрироваться на [ngrok.com](https://ngrok.com/).
И на странице [dashboard](https://dashboard.ngrok.com/get-started/your-authtoken) будет код. 

3. Установить ngrok.
Команда для Ubuntu:
```
sudo apt install ngrok
```

4. Привязать токен
```
ngrok config add-authtoken <TOKEN>
```

### Установка проекта 
1. Склонировать проект:

```
https://github.com/ezemskov24/whatsapp_reminder.git
```

2. В репозитории хранится файл .env.template. Надо на его основе создать и заполнить файл .env 


3. Перед запуском проекта необходимо собрать контейнер командой:
```
docker compose build
```

4. Запуск проекта: 
```
docker compose up -d
```
***
5. После запуска необходимо зайти в контейнер

```
docker exec -it <ID КОНТЕЙНЕРА> /bin/sh
```
5. Ввести команду
```
psql -U admin
```

6. И создать базу данных командой
```
create database reminder_db;
```
7. Выполнить в терминале команду для получения временного http
```
ngrok http 8000
```
8. Скопировать временный http и добавить его на странице [twilio](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
в разделе `Sandbox Settings` в поле `When a message comes in` приписав `/reminder` в конце к http.

### Запуск
1. Отправить на номер, указанный на странице [twilio-whatsapp-learn](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
сообщение с текстом  `join aid-angry`.

2. Отправить напоминание в формате 
```
dd:mm:year HH:mm text
```

3. Если необходимо получать повторяющиеся напоминания, то к сообщению добавить `daily` - для ежедневных напоминаний 
или `weekly` - для еженедельных.

4. Получить список предстоящих напоминаний командой
```
reminders list
```
5. Удалить напоминание
```
delete <id>
```
