# Foodgram

Foodgram — сервис для публикации рецептов. Пользователи могут создавать рецепты, добавлять их в избранное и список покупок, подписываться на других авторов и скачивать список ингредиентов.

Проект реализован в виде REST API на Django Rest Framework.

---

Технологии

* Python
* Django REST Framework
* PostgreSQL
* Docker / Docker Compose
* Nginx
* GitHub Actions (CI/CD)

---

## Запуск проекта в Docker (рекомендуемый способ)

### 1. Клонировать репозиторий

```bash
git clone git@github.com:anastasiapuzaceva-source/foodgram-project-react.git
cd foodgram-project-react
```

### 2. Создать файл `.env`

В корне проекта создайте файл `.env` и заполните его:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost
DJANGO_CSRF_TRUSTED_ORIGINS=https://myfoodgram27.hopto.org
```

### 3. Запустить контейнеры

```bash
docker-compose up -d
```

### 4. Выполнить миграции и собрать статику

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
```

### 5. Создать суперпользователя (опционально)

```bash
docker-compose exec backend python manage.py createsuperuser
```

После этого проект будет доступен по адресу:

```text
http://localhost/
```

---

## CI/CD

В проекте настроен CI/CD с использованием **GitHub Actions**.

При каждом пуше в ветку `main` автоматически выполняются:

* проверка кода и тесты
* сборка Docker-образов
* публикация образов в Docker Hub
* деплой проекта на сервер

Файл workflow находится в директории:

```text
.github/workflows/
```

---

## Автор

**Anastasiia Puzacheva**
GitHub: [https://github.com/anastasiapuzaceva-source](https://github.com/anastasiapuzaceva-source)
