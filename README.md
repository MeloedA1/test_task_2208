# test_task

Запуск приложения:

    sudo docker-compose up -d --force-recreate --build

Для отправки уведомлений в ТГ необходимо вставить значения tg_token и tg_chat_id в code/config.py

Описание:

    1. Приложение собирает данные с документа при помощи Google API
    2. Данные добавляются в БД, в том же виде, что и в файле –источнике, с добавлением колонки «стоимость в руб.»
    3. Приложение имеет функционал проверки соблюдения «срока поставки» из таблицы. В случае, если срок прошел, скрипт отправляет уведомление в Telegram.
       Приложение собирает данные о просроченных заказов и аггрегирует их в одно сообщение для телеграма.
