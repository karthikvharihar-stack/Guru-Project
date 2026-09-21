/**
 * jijnasa.js — Guru Jijnasa AI Chat Interface
 */
'use strict';

let conversationHistory = [];
let isProcessing = false;
let mediaRecorder = null;
let isRecording = false;
let audioChunks = [];

// ── Message sender ──────────────────────────────────────────────────────────
window.sendMessage = async function () {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text || isProcessing) return;

  appendUserMessage(text);
  input.value = '';
  input.style.height = 'auto';
  conversationHistory.push({ role: 'user', content: text });

  showLoading();
  isProcessing = true;

  try {
    const res = await fetch('/guru-jijnasa/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text, history: conversationHistory.slice(-10) })
    });

    if (!res.ok) throw new Error('Server error');
    const data = await res.json();

    hideLoading();
    if (data.error) {
      appendAIMessage('I encountered an error. Please try again.', []);
    } else {
      appendAIMessage(data.answer, data.sources || []);
      conversationHistory.push({ role: 'model', content: data.answer });
    }
  } catch (err) {
    hideLoading();
    appendAIMessage('Guru Jijnasa is temporarily unavailable. Please try again shortly.', []);
  }

  isProcessing = false;
};

// ── Ask from example ────────────────────────────────────────────────────────
window.askQuestion = function (text) {
  const input = document.getElementById('chat-input');
  if (input) {
    input.value = text;
    sendMessage();
  }
};

// ── Append messages ─────────────────────────────────────────────────────────
function appendUserMessage(text) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-message';
  div.style.cssText = 'display:flex; gap:12px; align-items:flex-start; flex-direction:row-reverse;';
  div.innerHTML = `
    <div style="width:36px;height:36px;background:var(--color-gold);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;color:white;">🙏</div>
    <div style="flex:1;display:flex;flex-direction:column;align-items:flex-end;">
      <div style="background:var(--color-primary);color:white;border-radius:16px 4px 16px 16px;padding:14px 18px;max-width:75%;">
        ${escHtml(text)}
      </div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

function appendAIMessage(text, sources) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-message';
  div.style.cssText = 'display:flex; gap:12px; align-items:flex-start;';

  // Format text: bold **text**, newlines
  const formatted = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');

  let sourcesHtml = '';
  if (sources && sources.length > 0) {
    const sourceList = sources.map(s =>
      `<span style="display:inline-block;padding:2px 8px;background:rgba(201,146,42,0.1);border-radius:6px;font-size:0.75rem;color:var(--color-gold);margin:2px;">📄 ${escHtml(s.title || s)}</span>`
    ).join(' ');
    sourcesHtml = `<div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--color-border);">
      <span style="font-size:0.72rem;color:var(--color-text-muted);letter-spacing:0.5px;">SOURCES: </span>${sourceList}
    </div>`;
  }

  // TTS button
  const ttsId = 'tts-' + Date.now();
  div.innerHTML = `
    <div style="width:36px;height:36px;background:var(--color-primary);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;color:white;">🪷</div>
    <div style="flex:1;">
      <div style="background:var(--color-background);border:1px solid var(--color-border);border-radius:4px 16px 16px 16px;padding:14px 18px;max-width:85%;">
        <div style="color:var(--color-text);line-height:1.8;">${formatted}</div>
        ${sourcesHtml}
        <div style="margin-top:10px;">
          <button id="${ttsId}" onclick="speakText(this, ${JSON.stringify(text)})" style="border:none;background:none;cursor:pointer;font-size:0.8rem;color:var(--color-text-muted);padding:0;">🔊 Listen</button>
        </div>
      </div>
      <div style="font-size:0.72rem;color:var(--color-text-muted);margin-top:5px;padding-left:4px;">Guru Jijnasa</div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
}

// ── Loading indicator ───────────────────────────────────────────────────────
let loadingEl = null;
function showLoading() {
  const container = document.getElementById('chat-messages');
  loadingEl = document.createElement('div');
  loadingEl.id = 'chat-loading';
  loadingEl.style.cssText = 'display:flex;gap:12px;align-items:flex-start;';
  loadingEl.innerHTML = `
    <div style="width:36px;height:36px;background:var(--color-primary);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;flex-shrink:0;">🪷</div>
    <div style="background:var(--color-background);border:1px solid var(--color-border);border-radius:4px 16px 16px 16px;padding:14px 18px;">
      <div style="display:flex;gap:5px;align-items:center;">
        <span style="width:8px;height:8px;background:var(--color-gold);border-radius:50%;animation:bounce 1.2s infinite 0s;display:inline-block;"></span>
        <span style="width:8px;height:8px;background:var(--color-gold);border-radius:50%;animation:bounce 1.2s infinite 0.2s;display:inline-block;"></span>
        <span style="width:8px;height:8px;background:var(--color-gold);border-radius:50%;animation:bounce 1.2s infinite 0.4s;display:inline-block;"></span>
      </div>
    </div>
  `;
  container.appendChild(loadingEl);
  scrollToBottom();
}

function hideLoading() {
  loadingEl?.remove();
  loadingEl = null;
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function scrollToBottom() {
  const container = document.getElementById('chat-messages');
  if (container) container.scrollTop = container.scrollHeight;
}

function escHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ── TTS ─────────────────────────────────────────────────────────────────────
window.speakText = function (btn, text) {
  if (!window.speechSynthesis) return;
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    btn.textContent = '🔊 Listen';
    return;
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'en-IN';
  utter.rate = 0.95;
  utter.onend = () => { btn.textContent = '🔊 Listen'; };
  btn.textContent = '⏹ Stop';
  window.speechSynthesis.speak(utter);
};

// ── Voice input ─────────────────────────────────────────────────────────────
window.toggleRecording = async function () {
  if (isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
};

async function startRecording() {
  if (!navigator.mediaDevices) {
    alert('Microphone access is not available in this browser.');
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = sendAudioForTranscription;
    mediaRecorder.start();
    isRecording = true;
    const btn = document.getElementById('mic-btn');
    if (btn) { btn.textContent = '⏹'; btn.classList.add('mic-active'); }
  } catch (err) {
    alert('Could not access microphone. Please allow microphone access.');
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(t => t.stop());
  }
  isRecording = false;
  const btn = document.getElementById('mic-btn');
  if (btn) { btn.textContent = '🎙️'; btn.classList.remove('mic-active'); }
}

async function sendAudioForTranscription() {
  const blob = new Blob(audioChunks, { type: 'audio/webm' });
  const formData = new FormData();
  formData.append('audio', blob, 'recording.webm');
  try {
    const res = await fetch('/guru-jijnasa/transcribe', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.transcription) {
      const input = document.getElementById('chat-input');
      if (input) input.value = data.transcription;
    } else {
      if (window.showToast) window.showToast('Could not transcribe audio.', 'warning');
    }
  } catch (err) {
    if (window.showToast) window.showToast('Transcription failed.', 'danger');
  }
}

// ── Keyboard shortcut: Enter to send ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chat-input');
  input?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
});
