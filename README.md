# praktikum_new_diplom
[![Django-app workflow](https://github.com/Postich-prog/foodgram-project-react/actions/workflows/main.yml/badge.svg)]

84.201.174.159

### Спринт 17 - Итоговый проект курса Foodgram
### Описание
«Продуктовый помощник»: приложение в котором можно публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Сервис «Список покупок» позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд, и получить его в формате PDF.
​
Команда разработки:
- :white_check_mark: [Матвей слуцких (backend)](https://github.com/Postich-prog)
- :white_check_mark: [Yandex Practicum (frontend)]
​
Полная документация к API находится по эндпоинту /redoc
​
### Стек технологий использованный в проекте:
- Python 3.7
- Django 2.2.26
- DRF
- Djoser
​
### Запуск проекта в dev-режиме
- Клонировать репозиторий git@github.com:Postich-prog/foodgram-project-react.git и перейти в него в командной строке.
- Установите и активируйте виртуальное окружение c учетом версии Python 3.7 (выбираем python не ниже 3.7):
​
```bash
py -3.7 -m venv venv
```
​
```bash
source venv/Scripts/activate
```
​
- Затем нужно установить все зависимости из файла requirements.txt
​
```bash
python -m pip install --upgrade pip
```
​
```bash
pip install -r requirements.txt
```
​
- Выполняем миграции:
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
​
Если есть необходимость, заполняем базу тестовыми данными командой:
​
```bash
python from_csv.py
```
​
- Создаем суперпользователя:
​
```bash
python manage.py createsuperuser
```
​
- Запускаем проект:
​
```bash
python manage.py runserver localhost:8000
```
​
### Примеры работы с API для всех пользователей
​
Подробная документация доступна по эндпоинту http://localhost:8000/redoc/
​
Для неавторизованных пользователей работа с API доступна в режиме чтения, что-либо изменить или создать не получится. 
​
```
Права доступа: Доступно без токена.
GET http://localhost:8000/api/recipes/ - Получение списка всех рецептов
GET http://localhost:8000/api/tags/ - Получение списка всех тегов
GET http://localhost:8000/api/users/ - Получение списка всех пользователей
```
​
### Пользовательские роли
​
- Аноним — может просматривать описания произведений, читать отзывы и комментарии.
- Аутентифицированный пользователь (user) — может, как и Аноним, читать всё, дополнительно он может публиковать рецепты, добавлять рецетпы в избранное, подписываться на пользователей, добавлять список покупок. Эта роль присваивается по умолчанию каждому новому пользователю.
- Модератор (moderator) — те же права, что и у Аутентифицированного пользователя плюс право удалять любые рецепты.
- Администратор (admin) — полные права на управление всем контентом проекта.
- Суперюзер Django — обладает правами администратора (admin)
​
### Регистрация нового пользователя
Получить код подтверждения на переданный email.
Права доступа: Доступно без токена.
спользовать имя 'me' в качестве username запрещено.
Поля email и username должны быть уникальными.
​
Регистрация нового пользователя:
​
```
POST http://localhost:8000/api/users/
```
​
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
​
```
​
Получение Auth-токена:
​
```
POST http://localhost:8000/api/auth/token/login/
```
​
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
​
### Примеры работы с API для авторизованных пользователей
​
Получение списка всех рецептов:
​
```
Права доступа: Доступно без токена
GET http://localhost:8000/api/recipes/
```
​
```json
[
  {
    "count": 0,
    "next": "string",
    "previous": "string",
    "results": [
      {
        "name": "string",
        "slug": "string"
      }
    ]
  }
]
```
​
Добавление тега:
​
```
Права доступа: Администратор.
POST http://localhost:8000/api/tags/
```
​
```json
{
  "name": "string",
  "color": "#Hex",
  "slug": "string"
}
```
​
Удаление тега:
​
```
Права доступа: Администратор.
DELETE http://localhost:8000/api/tags/<id>/
```
​
По ингредиентам аналогично, более подробно по эндпоинту /redoc/
​
​
Получение информации о произведении:
​
```
Права доступа: Доступно без токена
GET http://localhost:8000/api/v1/titles/{titles_id}/
```
​
```json
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {
      "name": "string",
      "slug": "string"
    }
  ],
  "category": {
    "name": "string",
    "slug": "string"
  }
}
```
​
Частичное обновление информации о произведении:
​
```
Права доступа: Администратор
PATCH http://localhost:8000/api/v1/titles/{titles_id}/
```
​
```json
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```
​
Удаление произведения:
```
Права доступа: Администратор
DEL http://localhost:8000/api/v1/titles/{titles_id}/
```
​
По TITLES, REVIEWS и COMMENTS аналогично, более подробно по эндпоинту /redoc/
​
### Работа с пользователями:
​
Для работы с пользователя есть некоторые ограничения для работы с ними.


Удаление пользователя по id:
​
```
Права доступа: Администратор
DELETE http://localhost:8000/api/users/{id}/ - Удаление пользователя по id
```
​
Получение данных своей учетной записи:
​
```
Права доступа: Любой авторизованный пользователь
GET http://localhost:8000/api/users/me/ - Получение данных своей учетной записи
```

​
​
Авторы:
- :white_check_mark: [Матвей Слуцких (backend)](https://github.com/Postich-prog)
- :white_check_mark: [Yandex Practicum (frontend)]