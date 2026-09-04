const chatWindow = document.getElementById('chatWindow');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const hint = document.getElementById('hint');
const ttsBtn = document.getElementById('ttsBtn');  // Новая кнопка

let isRecording = false;
let recognition = null;
let isTTSEnabled = true;  // Озвучка включена по умолчанию

// --- Отправка текста ---
async function sendMessage(text) {
    if (!text.trim()) return;

    addMessage('user', text);
    userInput.value = '';

    const typingId = showTyping();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        removeTyping(typingId);

        if (data.error) {
            addMessage('bot', '❌ ' + data.error);
        } else {
            addMessage('bot', data.reply);
            // Озвучиваем, если включено
            if (isTTSEnabled) {
                speakTextBrowser(data.reply);
            }
        }
    } catch (error) {
        removeTyping(typingId);
        addMessage('bot', '❌ Ошибка соединения');
        console.error(error);
    }
}

// --- Браузерный синтез речи ---
function speakTextBrowser(text) {
    if ('speechSynthesis' in window) {
        // Отменяем текущую речь, если есть
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ru-RU';
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        window.speechSynthesis.speak(utterance);
    }
}

// --- Добавление сообщения ---
function addMessage(type, text) {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.innerHTML = `
        <div class="avatar">${type === 'user' ? '👤' : '🤖'}</div>
        <div class="bubble">${text.replace(/\n/g, '<br>')}</div>
    `;
    chatWindow.appendChild(div);
    scrollToBottom();
}

// --- Индикатор печати ---
function showTyping() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message bot';
    div.id = id;
    div.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="bubble">
            <div class="typing"><span></span><span></span><span></span></div>
        </div>
    `;
    chatWindow.appendChild(div);
    scrollToBottom();
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// --- Отправка по Enter ---
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage(userInput.value);
});

sendBtn.addEventListener('click', () => sendMessage(userInput.value));

// --- Кнопка озвучки ---
ttsBtn.addEventListener('click', () => {
    isTTSEnabled = !isTTSEnabled;
    ttsBtn.textContent = isTTSEnabled ? '🔊' : '🔇';
    ttsBtn.title = isTTSEnabled ? 'Озвучка включена' : 'Озвучка выключена';
    
    // Если выключаем — останавливаем текущую речь
    if (!isTTSEnabled && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
});

// ============================================================
// 🎤 БРАУЗЕРНЫЙ МИКРОФОН (Speech Recognition API)
// ============================================================

function initSpeechRecognition() {
    // Проверяем поддержку
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.error('❌ Speech Recognition не поддерживается');
        hint.textContent = '❌ Ваш браузер не поддерживает голосовой ввод. Используйте Chrome.';
        micBtn.style.opacity = '0.3';
        return false;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'ru-RU';
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    // --- События ---
    recognition.onstart = () => {
        console.log('🔴 Распознавание началось');
        isRecording = true;
        micBtn.classList.add('recording');
        hint.textContent = '🔴 Слушаю... Говорите!';
    };

    recognition.onresult = (event) => {
        let transcript = '';
        let isFinal = false;
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                isFinal = true;
            }
        }
        
        console.log('📝 Распознано:', transcript, 'финал:', isFinal);
        
        if (isFinal && transcript.trim()) {
            userInput.value = transcript;
            hint.textContent = '🎙️ Отправляю...';
            stopRecording();
            sendMessage(transcript);
        } else if (transcript.trim()) {
            userInput.value = transcript;
        }
    };

    recognition.onerror = (event) => {
        console.error('❌ Ошибка распознавания:', event.error);
        
        // Исправляем ошибку "network" — пробуем перезапустить
        if (event.error === 'network') {
            hint.textContent = '🔄 Перезапуск микрофона...';
            setTimeout(() => {
                if (isRecording) {
                    try {
                        recognition.stop();
                    } catch (e) {}
                    setTimeout(() => {
                        try {
                            recognition.start();
                            hint.textContent = '🔴 Слушаю... Говорите!';
                        } catch (e) {
                            hint.textContent = '❌ Ошибка микрофона. Попробуйте перезагрузить страницу.';
                        }
                    }, 500);
                }
            }, 1000);
            return;
        }
        
        if (event.error === 'not-allowed') {
            hint.textContent = '❌ Разрешите доступ к микрофону в браузере';
        } else if (event.error === 'no-speech') {
            hint.textContent = '🎙️ Ничего не услышал. Попробуйте снова.';
        } else if (event.error === 'audio-capture') {
            hint.textContent = '❌ Микрофон не найден';
        } else {
            hint.textContent = '❌ Ошибка: ' + event.error;
        }
        
        micBtn.classList.remove('recording');
        isRecording = false;
    };

    recognition.onend = () => {
        console.log('⏹️ Распознавание завершено');
        micBtn.classList.remove('recording');
        isRecording = false;
        
        if (!userInput.value.trim()) {
            setTimeout(() => {
                hint.textContent = '🎙️ Нажмите и удерживайте для записи';
            }, 1000);
        }
    };

    return true;
}

function startRecording() {
    if (isRecording) return;
    
    if (!recognition) {
        const ok = initSpeechRecognition();
        if (!ok) return;
    }
    
    try {
        recognition.start();
    } catch (error) {
        console.error('Ошибка запуска:', error);
        if (error.message.includes('already started')) {
            try {
                recognition.stop();
            } catch (e) {}
            setTimeout(() => {
                try {
                    recognition.start();
                } catch (e) {
                    hint.textContent = '❌ Ошибка микрофона. Перезагрузите страницу.';
                }
            }, 500);
        } else {
            hint.textContent = '❌ Ошибка: ' + error.message;
        }
    }
}

function stopRecording() {
    if (recognition && isRecording) {
        try {
            recognition.stop();
        } catch (e) {
            console.warn('Ошибка остановки:', e);
        }
    }
}

// --- События микрофона (нажал → говоришь → отпустил) ---
micBtn.addEventListener('mousedown', (e) => {
    e.preventDefault();
    console.log('🖱️ mousedown');
    startRecording();
});

micBtn.addEventListener('mouseup', (e) => {
    e.preventDefault();
    console.log('🖱️ mouseup');
    stopRecording();
});

micBtn.addEventListener('mouseleave', () => {
    if (isRecording) {
        console.log('🖱️ mouseleave — останавливаем');
        stopRecording();
    }
});

// Поддержка touch (мобильные)
micBtn.addEventListener('touchstart', (e) => {
    e.preventDefault();
    console.log('📱 touchstart');
    startRecording();
});

micBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    console.log('📱 touchend');
    stopRecording();
});

// --- Инициализация при загрузке ---
initSpeechRecognition();

console.log('✅ Голосовой помощник готов');
console.log('   Нажмите и удерживайте 🎤 для записи');
console.log('   🔊 — включить/выключить озвучку');