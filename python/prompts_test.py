#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для массового тестирования промптов.
Читает запросы из файла, отправляет в GigaChat, сохраняет ответы.
"""

import os
import json
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

if not AUTH_KEY:
    print("❌ Ошибка: ключ авторизации не найден.")
    exit(1)

def load_requests(filename="synthetic_requests.txt"):
    """Загружает запросы из текстового файла"""
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def save_results(results, filename="results.json"):
    """Сохраняет результаты в JSON"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ Результаты сохранены в {filename}")

def main():
    print("📋 Загрузка синтетических запросов...")
    requests = load_requests()
    print(f"   Найдено {len(requests)} запросов\n")
    
    results = []
    
    with GigaChat(
        credentials=AUTH_KEY,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
        base_url="https://api.giga.chat/v1"
    ) as client:
        
        for idx, user_text in enumerate(requests, 1):
            print(f"📝 [{idx}/{len(requests)}] Запрос: {user_text}")
            
            try:
                response = client.chat.create(user_text)
                answer = response.messages[0].content[0].text
                
                results.append({
                    "request": user_text,
                    "response": answer,
                    "status": "ok"
                })
                print(f"   ✅ Ответ получен ({len(answer)} символов)\n")
                
            except Exception as e:
                results.append({
                    "request": user_text,
                    "response": None,
                    "status": f"error: {str(e)}"
                })
                print(f"   ❌ Ошибка: {e}\n")
    
    save_results(results)
    
    # Простая статистика
    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"\n📊 Статистика: {ok_count}/{len(results)} запросов успешно обработано")

if __name__ == "__main__":
    main()