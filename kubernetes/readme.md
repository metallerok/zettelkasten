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

### Создаем namespace
```shell
kubectl apply -f kubernetes/zettelkasten-namespace.yaml 
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
````

### Включаем поддержку прокси-сервера ingress для minikube
```shell
minikube addons enable ingress
```

### Запускаем прокси
```shell
kubectl apply -f kubernetes/ingress.yaml
```

### Активируем сервис для доступа к приложению из вне
Смотрим по какому адресу доступно наше приложение
```shell
kubectl get ingress -n zettelkasten
```

### Проверяем работоспособность
```shell
curl http://{service-ip}/api/v1/api-info
```