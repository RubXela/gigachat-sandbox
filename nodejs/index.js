#!/usr/bin/env node
/**
 * Базовый скрипт для Node.js для работы с GigaChat API
 */

require('dotenv').config();
const readline = require('readline');
const { GigaChat } = require('gigachat');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const AUTH_KEY = process.env.GIGACHAT_AUTH_KEY;

if (!AUTH_KEY) {
  console.error('❌ Ошибка: ключ авторизации не найден.');
  console.error('   Создайте файл .env с переменной GIGACHAT_AUTH_KEY=ваш_ключ');
  process.exit(1);
}

async function main() {
  console.log('\n🤖 GigaChat клиент запущен. Напишите "exit" для выхода.\n');

  const client = new GigaChat({
    credentials: AUTH_KEY,
    scope: 'GIGACHAT_API_PERS',
    verify_ssl_certs: false,
    base_url: 'https://api.giga.chat/v1'
  });

  try {
    await client.authenticate();

    const askQuestion = () => {
      rl.question('🧑 Вы: ', async (userText) => {
        if (['exit', 'выход', 'quit'].includes(userText.toLowerCase())) {
          console.log('👋 До свидания!');
          rl.close();
          return;
        }

        if (!userText.trim()) {
          askQuestion();
          return;
        }

        try {
          const response = await client.chat.create(userText);
          const answer = response.messages[0].content[0].text;
          console.log(`🤖 GigaChat: ${answer}\n`);
        } catch (error) {
          console.error(`❌ Ошибка: ${error.message}\n`);
        }

        askQuestion();
      });
    };

    askQuestion();

  } catch (error) {
    console.error(`❌ Ошибка авторизации: ${error.message}`);
    process.exit(1);
  }
}

main();