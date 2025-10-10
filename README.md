# OTUS Highload Architect (1.2.0) – Social Network

## Домашняя работа

В рамках курса нужно проводить нагрузочное тестирование различных Highload-решений и описывать результаты тестов в отчете

Ссылки на отчеты
1. [Производительность индексов](https://github.com/Grin941/social-network/tree/main/tests/load/test_indexes)
2. [Репликация](https://github.com/Grin941/social-network/tree/main/tests/load/test_replication)
3. [Кэширование](https://github.com/Grin941/social-network/tree/main/tests/load/test_cache)
4. [Шардирование](https://github.com/Grin941/social-network/tree/main/tests/load/test_sharding)
5. [Очереди и отложенное выполнение](https://github.com/Grin941/social-network/tree/main/tests/load/test_queues)

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
$ set -a && source .env && set +a && docker compose -f devops/social_network/docker-compose.yaml up --build
```

### Документация API

- [FastAPI swagger](http://127.0.0.1:8080/docs)
- [Postman Collection](https://github.com/Grin941/social-network/blob/main/devops/social_network/postman_collection.json)

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

### Модульное тестирование

- запуск `pytest` тестов
```shell
make test
```
