# picservices
Picture processing service

**1. Установка Docker и Docker Compose**

* **macOS:**
    * Скачайте и установите Docker Desktop с официального сайта: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    * Docker Compose входит в состав Docker Desktop.
* **Linux (Debian/Ubuntu):**
    * Установите Docker:
        ```bash
        sudo apt-get update
        sudo apt-get install docker.io
        ```
    * Установите Docker Compose:
        ```bash
        sudo apt-get install docker-compose
        ```
    * У других Linux дистрибутивов инструкции могут отличаться.
* **Windows:**
    * Скачайте и установите Docker Desktop с официального сайта: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    * Docker Compose входит в состав Docker Desktop.

**2. Подготовка проекта**

* Убедитесь, что ваш `docker-compose.yml` файл находится в корне проекта.
* Убедитесь, что ваш Dockerfile, и папка src, находятся на один уровень выше папки с docker-compose файлом.
* Убедитесь, что в папке src есть файл .dev.env, если вы его используете.
* Убедитесь, что папка src содержит файл main.py, который запускает fastapi.
* Убедитесь, что в папке src есть файл tasks.py, который запускает celery.
* Убедитесь, что в файле requirements.txt или в файле pyproject.toml находятся все необходимые зависимости.

**3. Запуск контейнеров**

* Откройте терминал (или PowerShell в Windows).
* Перейдите в каталог, где находится ваш `docker-compose.yml` файл.
* Выполните команду:
    ```bash
    docker-compose up --build
    ```
    * `--build` - эта опция собирает образы Docker из вашего `Dockerfile`.
* Если необходимо пересобрать образы без кеша, выполните команду:
    ```bash
    docker-compose up --build --no-cache
    ```
* Если контейнеры уже были запущены, и вы хотите их пересоздать, выполните команду:
    ```bash
    docker-compose up --force-recreate
    ```

**4. Остановка контейнеров**

* Чтобы остановить контейнеры, нажмите `Ctrl + C` в терминале, где они запущены, или выполните команду в новом терминале:
    ```bash
    docker-compose down
    ```

**5. Проверка работы**

* После запуска контейнеров, вы можете проверить работу `image-service` в браузере, перейдя по адресу `http://localhost:8000`.
* Для проверки redis, можно использовать redis-cli.
* Для проверки celery, нужно смотреть логи контейнера celery-worker.
