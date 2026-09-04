#!/bin/bash

# Скрипт для получения access_token GigaChat
# Использование: ./get_token.sh

# Генерация случайного UUID (для RqUID)
UUID=$(uuidgen 2>/dev/null || echo "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e")

echo "🔑 Запрос access_token..."

curl -L -X POST 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Accept: application/json' \
  -H "RqUID: $UUID" \
  -H 'Authorization: Basic ВАШ_BASE64_КЛЮЧ_СЮДА' \
  --data-urlencode 'scope=GIGACHAT_API_PERS'