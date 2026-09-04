import os
from dotenv import load_dotenv

load_dotenv()

AUTH_KEY = os.getenv("GIGACHAT_AUTH_KEY")

print(f"Ключ: {AUTH_KEY}")
print(f"Длина: {len(AUTH_KEY)}")

# Проверяем каждый символ
bad_chars = []
for i, ch in enumerate(AUTH_KEY):
    try:
        ch.encode('latin-1')
    except UnicodeEncodeError:
        bad_chars.append((i, ch))

if bad_chars:
    print("⚠️ Найдены недопустимые символы:")
    for pos, ch in bad_chars:
        print(f"   Позиция {pos}: '{ch}' (код: {ord(ch)})")
else:
    print("✅ Все символы допустимы")