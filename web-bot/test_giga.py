import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

if not AUTH_KEY:
    print("❌ Ключ не найден в .env")
    exit(1)

print(f"🔑 Длина ключа: {len(AUTH_KEY)}")

# Вариант 1: Пробуем передать ключ как bytes
try:
    # Кодируем ключ в bytes для безопасной передачи
    auth_bytes = AUTH_KEY.encode('ascii')
    auth_header = f"Basic {auth_bytes.decode('ascii')}"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e",
        "Authorization": auth_header
    }
    
    data = {"scope": "GIGACHAT_API_PERS"}
    
    print("🔄 Запрос токена для GigaChat...")
    
    response = requests.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers=headers,
        data=data,
        verify=False,
        timeout=10
    )
    
    print(f"📊 Статус: {response.status_code}")
    print(f"📄 Ответ: {response.text[:200]}")
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✅ Токен получен: {token[:30]}...")
    else:
        print("❌ Ошибка. Проверьте ключ или scope.")
        
except UnicodeEncodeError as e:
    print(f"❌ Ошибка кодировки: {e}")
    print("   Попробуйте другой способ...")
    
    # Вариант 2: Используем requests.auth
    try:
        from requests.auth import HTTPBasicAuth
        
        # Парсим ключ (он уже в формате Base64)
        # Нужно проверить, что это действительно Base64
        try:
            # Пробуем декодировать как Base64
            decoded = base64.b64decode(AUTH_KEY)
            print(f"   Ключ успешно декодирован как Base64")
        except:
            print("   Ключ НЕ является Base64, пробуем как есть...")
        
        response = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            auth=HTTPBasicAuth('', AUTH_KEY),  # Пустой логин, ключ как пароль
            data={"scope": "GIGACHAT_API_PERS"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": "6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e"
            },
            verify=False,
            timeout=10
        )
        
        print(f"📊 Статус (вариант 2): {response.status_code}")
        print(f"📄 Ответ: {response.text[:200]}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Токен получен: {token[:30]}...")
        else:
            print("❌ Ошибка. Проверьте ключ.")
            
    except Exception as e2:
        print(f"❌ Ошибка во втором способе: {e2}")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()