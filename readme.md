### Глобальные зависимости
* Python 3.8+
* virtualenv
* libpq-dev
* build-essential 
* python3-dev
* redis-server
* rabbitmq-server
* postgresql

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
```bash
make test
```

### Web сервер
```bash
make run_web
```

### Создание файла миграции
```bash
make migration name="001_init"
```

### Применение миграций
```bash
make migrate_up
make migrate_down
```
