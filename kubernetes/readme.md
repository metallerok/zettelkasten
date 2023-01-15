## Запуск кластера на локальном хосте


Для запуска вам для начала нужно установить:
- minikube
- kubectl
- Драйвер для minikube, например virtualbox

### Запускаем minikube
```shell
minikube start --vm-driver=virtualbox
```

### Собираем docker-образ web приложения
```shell
make docker build
```

### Делаем доступным образ внутри munikube кластера
```shell
minikube image load zettelkasten-web
```

### Устанавливаем секретные переменные
Значение параметров должны быть закодированы в base64: `echo -n 'password' | base64`
```shell
kubectl apply -f kubernetes/postgres-secrets.yaml
```

### Запускаем postgres pod'ы
```shell
kubectl apply -f kubernetes/postgres-deployment.yaml
```

### Запускаем web приложение
```shell
kubectl apply -f kubernetes/web-app-deployment.yaml
```
### Активируем сервис для доступа к приложению из вне
Откроет окно с адресом запущенного сервиса
```shell
minikube service zettelkasten-service
```

### Проверяем работоспособность
```shell
curl http://{service-ip}/api/v1/api-info
```