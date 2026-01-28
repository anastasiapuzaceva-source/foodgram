# Foodgram

Проект — реализация API для социальной сети Yatube.  
Позволяет работать с постами, комментариями, группами и системой подписок.

## Установка

Установка и запуск
1. Клонировать репозиторий
```
'git clone git@github.com:anastasiapuzaceva-source/api-final-yatube.git'
```

2. Создать и активировать виртуальное окружение
```
python3 -m venv venv

source venv/bin/activate
```
3. Установить зависимости
```
'python3 -m pip install --upgrade pip'

'pip install -r requirements.txt'
```

4. Выполнить миграции
```
'python3 manage.py migrate'
```

5. Запустить проект
```
'python3 manage.py runserver'
```

git@github.com:anastasiapuzaceva-source/api-final-yatube.git

## Где найти спецификацию API

После запуска локального сервера спецификация API доступна по адресу:
```
http://127.0.0.1:8000/redoc/
```

Автор проекта

[Anastasiia Puzacheva](https://github.com/anastasiapuzaceva-source)

