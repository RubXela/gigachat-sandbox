#python/basic_request.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Базовый скрипт для отправки запроса к GigaChat.
Принимает текст от пользователя и выводит ответ модели.
"""

import os
from gigachat import GigaChat
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

if not AUTH_KEY:
    print("❌ Ошибка: ключ авторизации не найден.")
    print("   Создайте файл .env с переменной GIGACHAT_AUTH_KEY=ваш_ключ")
    exit(1)

print("\n🤖 GigaChat клиент запущен. Напишите 'exit' для выхода.\n")

with GigaChat(
    credentials=AUTH_KEY,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,
    base_url="https://api.giga.chat/v1"
) as client:
    
    while True:
        user_text = input("🧑 Вы: ")
        
        if user_text.lower() in ["exit", "выход", "quit"]:
            print("👋 До свидания!")
            break
        
        if not user_text.strip():
            continue
        
        try:
            response = client.chat.create(user_text)
            answer = response.messages[0].content[0].text
            print(f"🤖 GigaChat: {answer}\n")
        except Exception as e:
            print(f"❌ Ошибка: {e}\n")