#!/bin/bash

# Скрипт для отправки запроса к GigaChat через curl
# Использование: ./chat_request.sh "Ваш запрос"

if [ -z "$1" ]; then
    echo "Использование: $0 \"Ваш запрос\""
    exit 1
fi

TOKEN="ВАШ_ACCESS_TOKEN_СЮДА"

echo "📤 Отправка запроса: $1"

curl -L -X POST 'https://api.giga.chat/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  --data-raw "{
    \"model\": \"GigaChat\",
    \"messages\": [
        {
            \"role\": \"user\",
            \"content\": \"$1\"
        }
    ]
}"