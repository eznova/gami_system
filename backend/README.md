# Backend

API для работы с базой данных.

- PUT ​/login Точка входа для авторизации (put_login)
- GET ​/users​/get​/{user_id}​/details Получить информацию о пользователе, такую как количество монет (ncoins), рейтинг и другие данные
- GET ​/users​/get​/{user_id}​/job_info Получить информацию о должностях и отделах пользователя
- GET ​/users​/get​/{user_id}​/personal Получить личные данные пользователя
- GET ​/users​/get​/{user_id}​/photo Получить фото пользователя в формате base64
- POST ​/users​/upload​/{user_id}​/photo Загрузить фото пользователя в формате base64 и сохранить его в базе данных.

## Запуск

```bash
docker-compose up -d
```

## Документация

http://<url>:5000/apidocs
