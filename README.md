# Инструкция по развертке проекта EchoDel

Эта инструкция поможет вам развернуть проект `echo_delivery_web` с GitHub, создать виртуальное окружение, установить зависимости, настроить базу данных PostgreSQL вручную и запустить сервер разработки Django.

## Клонирование репозитория

Перед началом работы склонируйте репозиторий с проектом в нужную вам папку:

```bash
git clone https://github.com/abletoburntheweb/echo_delivery_web .
```
*(Обратите внимание на точку `.` в конце команды — она указывает, что нужно клонировать репозиторий в *текущую* директорию.)*

## Запуск проекта

Откройте терминал (например, CMD, PowerShell или VSCode Terminal) и перейдите в папку с проектом:

```bash
cd ...\EchoDel\
```
*(Замените `...\EchoDel\` на путь к папке, куда вы склонировали проект.)*

### Создание виртуального окружения

Виртуальное окружение — это изолированная среда, в которой хранятся зависимости Python-проекта. Это нужно, чтобы не засорять глобальную систему и избежать конфликтов между проектами. Для создания виртуального окружения с именем `echodel` выполните:

```bash
python -m venv echodel
```

### Активация виртуального пространства

Для активации виртуального окружения выполните:

```bash
.\echodel\Scripts\activate
```
После активации строка командной строки изменится — появится префикс `(echodel)`:

```bash
(echodel) C:\...\EchoDel\>
```

#### Ошибка: `cannot be loaded because running scripts is disabled on this system`

Если вы видите ошибку вроде:

```
File C:\...\echodel\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```
Это означает, что PowerShell запрещает выполнение скриптов. Чтобы разрешить выполнение скриптов для текущего пользователя, выполните:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Если нужно вернуть все обратно:

```bash
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser
```

### Установка зависимостей

Установите зависимости из файла `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```
*(Использование `python -m pip` гарантирует, что пакеты устанавливаются в активированное виртуальное окружение.)*

Это установит все необходимые библиотеки (например, Django, django-extensions, psycopg2-binary и другие).

### Подключение и настройка базы данных PostgreSQL

Проект настроен на работу с PostgreSQL. Если вы ещё не создали базу данных и таблицы, выполните следующие шаги:

#### 1. Настройка подключения к базе данных

Параметры подключения находятся в файле `echodel/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'echo_delivery', # Имя вашей базы данных
        'USER': 'postgres',      # Имя пользователя (измените при необходимости)
        'PASSWORD': '1221',      # Пароль пользователя (измените при необходимости)
        'HOST': 'localhost',     # Хост (обычно localhost)
        'PORT': '5432',          # Порт (обычно 5432)
    }
}
```
*Если вы будете использовать другого пользователя или пароль для БД, измените их в `settings.py`.*

#### 2. Создание базы данных и таблиц вручную

Так как в моделях проекта (`core/models.py`) установлено `managed = False`, Django **не будет** создавать таблицы через миграции. Их нужно создать вручную.

1.  **Запустите PostgreSQL.** Убедитесь, что служба работает.
2.  **Откройте pgAdmin (или psql).**
3.  **Создайте базу данных `echo_delivery`.**
    *   В pgAdmin: ПКМ по "Databases" -> "Create" -> "Database...". Введите `echo_delivery` в поле "Database", выберите владельца (например, `postgres`), нажмите "Save".
4.  **Подключитесь к созданной базе `echo_delivery`.**
    *   В pgAdmin: дважды щёлкните по `echo_delivery`.
5.  **Создайте таблицы с помощью SQL-скрипта.**
    *   В pgAdmin: откройте SQL-редактор (ПКМ по `echo_delivery` -> "Query Tool").
    *   Вставьте следующий SQL-скрипт и выполните его:

        ```sql
        -- Таблица Категория (Django модель Category)
        CREATE TABLE Категория (
            ID_CAT SERIAL PRIMARY KEY,
            Name VARCHAR(255) NOT NULL UNIQUE -- Уникальность имени категории
        );

        -- Таблица Блюдо (Django модель Dish)
        CREATE TABLE Блюдо (
            ID_BLU SERIAL PRIMARY KEY,
            FK_ID_CAT INTEGER NOT NULL,
            Name VARCHAR(255) NOT NULL,
            DESCRIPTION TEXT, -- Переименовано с DESC
            IMG VARCHAR(255) NOT NULL,
            Price DECIMAL(10,2) DEFAULT 0.00,
            FOREIGN KEY (FK_ID_CAT) REFERENCES Категория(ID_CAT) ON DELETE RESTRICT
        );

        -- Таблица Контора (Django модель Company или расширение User)
        CREATE TABLE Контора (
            ID_COMPANY SERIAL PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Phone VARCHAR(20),
            Email VARCHAR(255),
            PasswordHash VARCHAR(255) NOT NULL, -- Лучше не хранить хэш напрямую, Django сам шифрует пароли
            Address TEXT
        );

        -- Таблица Заказ (Django модель Order)
        CREATE TABLE Заказ (
            ID_ORDER SERIAL PRIMARY KEY,
            FK_ID_COMPANY INTEGER NOT NULL,
            DeliveryDate DATE NOT NULL,
            DeliveryTime TIME,
            DeliveryAddress TEXT NOT NULL,
            Status VARCHAR(20) DEFAULT 'новый',
            FOREIGN KEY (FK_ID_COMPANY) REFERENCES Контора(ID_COMPANY) ON DELETE RESTRICT
        );

        -- Таблица СоставЗаказа (Django модель OrderItem)
        CREATE TABLE СоставЗаказа (
            ID_ITEM SERIAL PRIMARY KEY,
            FK_ID_ORDER INTEGER NOT NULL,
            FK_ID_BLU INTEGER NOT NULL,
            Quantity INTEGER NOT NULL CHECK (Quantity > 0),
            FOREIGN KEY (FK_ID_ORDER) REFERENCES Заказ(ID_ORDER) ON DELETE CASCADE,
            FOREIGN KEY (FK_ID_BLU) REFERENCES Блюдо(ID_BLU) ON DELETE RESTRICT
        );
        ```
    *   **Порядок важен:** `Категория` и `Контора` создаются первыми, затем `Блюдо` (ссылающееся на `Категория`), `Заказ` (ссылающийся на `Контора`), и наконец `СоставЗаказа` (ссылающаяся на `Заказ` и `Блюдо`).

#### 3. Создание системных таблиц Django

Хотя таблицы для вашего приложения `core` создаются вручную, Django всё равно нужно создать свои *системные* таблицы (для аутентификации, сессий, админки и т.д.).

1.  Убедитесь, что виртуальное окружение активировано и вы находитесь в папке с `manage.py`.
2.  Выполните команду миграций:

    ```bash
    python manage.py migrate
    ```
    Эта команда создаст таблицы Django (`django_session`, `auth_user`, `django_content_type` и другие) в вашей базе данных `echo_delivery`.

### Создание суперпользователя

Создайте суперпользователя для доступа к административной панели Django:

```bash
python manage.py createsuperuser
```
Следуйте инструкциям в терминале, чтобы задать имя пользователя, почту и пароль.

### Запуск сервера разработки Django

Запустите сервер разработки:

```bash
python manage.py runserver
```
Вывод в терминале будет примерно такой:

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
November 05, 2025 - 16:00:00
Django version 5.2.7, using settings 'echodel.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
Откройте проект в браузере:

```
http://127.0.0.1:8000/
```
Административная панель будет доступна по адресу `http://127.0.0.1:8000/admin/`.

---

## FAQ

### Как создать обычного пользователя?

Чтобы создать обычного пользователя (не суперпользователя), воспользуйтесь командной оболочкой Django:

```bash
python manage.py shell
```
Затем выполните следующий код:

```python
from django.contrib.auth.models import User

user = User.objects.create_user(
    username='ваше_имя_пользователя',
    password='ваш_пароль',
    email='почта@пример.ком'  # Можно оставить пустым
)
```
Чтобы проверить, что пользователь создан, выполните:

```python
User.objects.all()
```

---

## Решение проблем

Если проект не запускается, проверьте:

1.  **Установлена ли правильная версия Python (3.8 или выше):**

    ```bash
    python --version
    ```
2.  **Активировано ли виртуальное окружение (должен быть префикс `(echodel)` в консоли).**
3.  **Установлены ли зависимости:**

    ```bash
    python -m pip install -r requirements.txt
    ```
4.  **Верно ли указаны параметры подключения в `echodel/settings.py` → `DATABASES`.**
5.  **Запущена ли служба PostgreSQL.**
6.  **Существует ли база данных `echo_delivery` в PostgreSQL.**
7.  **Выполнены ли миграции (`python manage.py migrate`) для создания системных таблиц Django.**
8.  **Если ошибка: `can't open file "C:\...\manage.py": [Errno 2] No such file or directory`, убедитесь, что вы перешли в директорию проекта:**

    ```bash
    cd ...\EchoDel\
    ```
9. **Если ошибка `ОШИБКА: отношение "django_session" не существует` или `django.db.utils.ProgrammingError` при обращении к таблицам Django — не выполнены миграции (`python manage.py migrate`).**

---
