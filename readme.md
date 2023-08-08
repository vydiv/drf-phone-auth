# API авторизация через телефон

В проекте используется: Python 3.10, DRF, PostgreSQL.

Регистрация, авторизация реализована с помощью dj-rest-auth. https://dj-rest-auth.readthedocs.io/en/latest/

Функционал: 

- [Регистрация](#reg) 
- [Верификация](#code)
- [Авторизация](#login)
- [Профиль](#profile)
- [REDOC](#doc)


## <a name="reg">API запрос для регистрации </a>
http://127.0.0.1:8000/api/user/register/

Ожидаются данные: password1, password2, phone_number. 

После регистрации срабатывает отправка 4хзначного кода авторизации с реализованной задержкой в 2сек.

Срабатывает сигнал на создание 6-значного инвайт-код(цифры и символы).

## <a name="code">API запрос для верификации </a>
http://127.0.0.1:8000/api/user/verify-phone/

Ожидаются данные: phone_number, otp.

При правильно введённом коде, пользователь получает верификацию и может авторизоваться. 
Если пользователь потерял код, то есть возможность повторной отправки смс с помощью API http://127.0.0.1:8000/api/user/send-sms/


## <a name="login">API запрос для авторизации </a>
http://127.0.0.1:8000/api/user/login/

Ожидаются данные: phone_number, password.

Если пользователь получил верификацию телефона, он может авторизоваться. 
При успешной верификации получаем access token и refresh token. 

## <a name="profile">API запрос профиля </a>
http://127.0.0.1:8000/api/user/profile/

При успешной авторизации пользователь может получить доступ к своему профилю. 
При GET запросе можно увидеть:
phone_number, invite_code, activated_invite_code, invited_users (пользователи, которые ввели инвайт код текущего пользователя)

При PUT запросе в поле another_invite_code вводим чужой код, после первой активации второй раз переписать поле не получится. 
Код активируется только если он существует (был присвоен другому пользователю). 


## <a name="profile">API запрос для получения всех пользователей </a>
http://127.0.0.1:8000/api/user/list/

Данный API выводит всех зарегистрированных пользователей. 

## <a name="doc">REDOC</a>
http://127.0.0.1:8000/swagger/

Выводит API проекта в swagger. 

