Сторонние модули нужно устанавливать через pip:
pip install redis jinja2 werkzeug mysql-connector-python

До запуска нужно создать БД в MySQL

Команда запуска веб сервиса
python anno.py

Тестовая страница
http://127.0.0.1:5555/

2 инструмента с https://palletsprojects.com/ :
1. jinja2 - шаблонизатор - https://jinja.palletsprojects.com/en/stable/
2. werkzeug - WSGI toolkit - https://werkzeug.palletsprojects.com/en/stable/

2 инструмента для сохранения данных в процессе работа с программой :
1. mysql.connector - соединенеие с локальным MySQL - https://dev.mysql.com/doc/connector-python/en/quick-installation-guide.html
2. redis соединенеие с локальным Redis - https://redis.readthedocs.io/en/stable/

Кеширование с использованием Redis нужно, т.к. генерация GIF файла занимает продолжительное время.

Генераторы (gen_* файлы) в тестовых целях могут запускаться сами по себе.
Аргумент для тестовой генерации гифки находится в самом низу .py файла.
Все промежуточные кадры создаются в полдпапке frames
Все результаты создаются в подпапке static