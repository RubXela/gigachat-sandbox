import os
import requests
import urllib3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)
CORS(app)

GIGACHAT_KEY = os.getenv("GIGACHAT_AUTH_KEY")

if not GIGACHAT_KEY:
    print("❌ Ошибка: GIGACHAT_AUTH_KEY не найден в .env")
    exit(1)

print("✅ Ключ GigaChat загружен")

# --- Получение токена для GigaChat ---
def get_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "9995ee0a-981c-41e1-8a99-efd7cad58cdd",
        "Authorization": f"Basic {GIGACHAT_KEY}"
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"❌ Ошибка получения токена: {e}")
        return None

# --- GigaChat ---
def ask_gigachat(message):
    token = get_token()
    if not token:
        return "❌ Не удалось получить токен для GigaChat"
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "model": "GigaChat:latest",
        "messages": [
            {"role": "system", "content": "Ты — голосовой помощник для пожилых людей. Отвечай кратко, понятно и доброжелательно."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Ошибка GigaChat: {e}")
        return f"❌ Ошибка: {str(e)}"

# --- Маршруты ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    if not message.strip():
        return jsonify({'error': 'Сообщение не указано'}), 400
    reply = ask_gigachat(message)
    return jsonify({'reply': reply})

if __name__ == '__main__':
    print("🚀 Запуск на http://localhost:5000")
    
    # Проверяем GigaChat
    token = get_token()
    if token:
        print("✅ GigaChat готов к работе")
    else:
        print("⚠️ GigaChat не доступен")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    
    # app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
    