### Диаграмма компонентов
![Диаграмма компонентов](components_diagram.png)

### Глобальные зависимости
* Python 3.8+
* virtualenv
* libpq-dev
* build-essential 
* python3-dev
* redis-server
* rabbitmq-server
* postgresql

### Документация по HTTP API
Для просмотра документации понадобится утилита [redoc](https://github.com/Redocly/redoc)
```shell
redoc-cli serve src/entrypoints/web/docs/specs.yaml --watch
```

### Коды HTTP исключений
[Ссылка](src/entrypoints/web/errors/errors_desc.md)

### Создание окружения
```bash
virtualenv -p python3.8 .venv
```
### Установка зависимостей
```bash
make install
```

### Тесты
Остановится после первой ошибки
```shell
make test
```

### Web сервер
```shell
make run_web
```

### Создание файла миграции
```shell
make migration name="001_init"
```

### Применение миграций
Предварительно нужно создать базу данных и указать ее uri
```shell
make migrate_up
```
```shell
make migrate_down
```

## Docker

### Сборка докер-образа веб сервера
```shell
make docker_build
```

### Запуск/остановка docker-compose dev окружения
```shell
make docker_up
```
```shell
make docker_down
```

### Применение миграций для докер контейнера
```shell
make docker_migrate_up
```
```shell
make docker_migrate_down
```

### Запуск тестов внутри докер контейнера
```shell
make docker_test
```
