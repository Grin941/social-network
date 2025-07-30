# OTUS Highload Architect (1.2.0) – Social Network

## Развертывание

1. Создать файл .env, хранящий sensitive data, согласно [12 factor app](https://12factor.net/config)
2. Запустить приложение

### Создание .env

В качестве примера воспользуйтесь файлом .env.local

```shell
cp .env.local .env
vim .env
```

### Запуск приложения

```shell
make serve
```

или при отсутствии cmake

```shell
$ docker compose -f devops/social_network/docker-compose.yaml --env-file .env up --build
```

## Локальная разработка

### Управление проектом

- установить необходимые зависимости для локальной разработки
```shell
make install
```

### Форматирование

- автоформатирование кода
```shell
make fix
```
- тестирование кода линтерами
```shell
make lint
```

### Тестирование

- запуск `pytest` тестов
```shell
make test
```
