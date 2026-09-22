/**
 * jijnasa.js — Guru Jijnasa Voice Assistant & AI Chat
 * 
 * Features:
 *  - Real-time Speech-to-Text via Web Speech API (with MediaRecorder fallback)
 *  - Natural Spoken Voice Text-to-Speech Output (window.speechSynthesis)
 *  - Auto Voice Response toggle (replies spoken automatically)
 *  - Visual listening & speaking waveform indicators
 */
'use strict';

let conversationHistory = [];
let isProcessing = false;
let speechRecognition = null;
let isListening = false;
let mediaRecorder = null;
let audioChunks = [];
let lastInputWasVoice = false;
let currentUtterance = null;
let activeSpeakerBtn = null;

// ── Initialize Speech Recognition on page load ──────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initSpeechRecognition();

  const input = document.getElementById('chat-input');
  input?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      lastInputWasVoice = false;
      sendMessage();
    }
  });

  // Pre-load synthesis voices
  if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = () => {
      // Voices loaded
    };
  }
});

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    try {
      speechRecognition = new SpeechRecognition();
      speechRecognition.continuous = false;
      speechRecognition.interimResults = true;
      speechRecognition.lang = 'en-IN'; // Indian English default, understands English/Sanskrit/Kannada terms

      speechRecognition.onstart = () => {
        isListening = true;
        showListeningUI(true);
      };

      speechRecognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        const input = document.getElementById('chat-input');
        if (input && transcript) {
          input.value = transcript;
          input.style.height = 'auto';
          input.style.height = input.scrollHeight + 'px';
        }
      };

      speechRecognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        stopRecording();
      };

      speechRecognition.onend = () => {
        isListening = false;
        showListeningUI(false);
        const input = document.getElementById('chat-input');
        if (input && input.value.trim().length > 0) {
          lastInputWasVoice = true;
          // Short delay so user sees transcribed text, then auto-send
          setTimeout(() => {
            if (!isProcessing && input.value.trim().length > 0) {
              sendMessage();
            }
          }, 400);
        }
      };
    } catch (e) {
      console.warn('SpeechRecognition init error:', e);
    }
  }
}

// ── Voice Input Toggle (Mic Button) ─────────────────────────────────────────
window.toggleRecording = async function () {
  if (isListening || isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
};

let isRecording = false;

async function startRecording() {
  // Stop any active speech output when user starts speaking
  stopAllSpeech();

  if (speechRecognition) {
    try {
      speechRecognition.start();
      return;
    } catch (err) {
      console.warn('Speech recognition start failed, using fallback:', err);
    }
  }

  // Fallback to MediaRecorder audio recording
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('Voice input is not supported in this browser. Please use Chrome, Edge, or Safari.');
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
    showListeningUI(true);
  } catch (err) {
    alert('Could not access microphone. Please enable microphone permissions in your browser.');
  }
}

function stopRecording() {
  if (speechRecognition && isListening) {
    try { speechRecognition.stop(); } catch (e) {}
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(t => t.stop());
  }
  isListening = false;
  isRecording = false;
  showListeningUI(false);
}

function showListeningUI(active) {
  const micBtn = document.getElementById('mic-btn');
  const banner = document.getElementById('voice-listening-banner');
  if (active) {
    if (micBtn) {
      micBtn.textContent = '⏹';
      micBtn.classList.add('mic-active');
    }
    if (banner) banner.style.display = 'flex';
  } else {
    if (micBtn) {
      micBtn.textContent = '🎙️';
      micBtn.classList.remove('mic-active');
    }
    if (banner) banner.style.display = 'none';
  }
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
      if (input) {
        input.value = data.transcription;
        lastInputWasVoice = true;
        sendMessage();
      }
    }
  } catch (err) {
    console.error('Transcription failed:', err);
  }
}

// ── Message Sender ──────────────────────────────────────────────────────────
window.sendMessage = async function () {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text || isProcessing) return;

  // Stop any ongoing TTS audio
  stopAllSpeech();

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
      const bubbleEl = appendAIMessage(data.answer, data.sources || []);
      conversationHistory.push({ role: 'model', content: data.answer });

      // Check if auto voice response is enabled or user used voice
      const autoSpeakToggle = document.getElementById('voice-auto-speak-toggle');
      const shouldSpeak = (autoSpeakToggle && autoSpeakToggle.checked) || lastInputWasVoice;
      if (shouldSpeak) {
        // Auto-speak response in voice
        const ttsBtn = bubbleEl?.querySelector('.tts-btn');
        speakText(ttsBtn, data.answer, bubbleEl);
      }
    }
  } catch (err) {
    hideLoading();
    appendAIMessage('Guru Jijnasa is temporarily unavailable. Please try again shortly.', []);
  }

  isProcessing = false;
  lastInputWasVoice = false;
};

// ── Quick Ask Example ───────────────────────────────────────────────────────
window.askQuestion = function (text) {
  const input = document.getElementById('chat-input');
  if (input) {
    input.value = text;
    lastInputWasVoice = false;
    sendMessage();
  }
};

// ── Append Messages ─────────────────────────────────────────────────────────
function appendUserMessage(text) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'chat-message';
  div.style.cssText = 'display:flex; gap:12px; align-items:flex-start; flex-direction:row-reverse;';
  div.innerHTML = `
    <div style="width:38px;height:38px;background:linear-gradient(135deg, #BF953F, #AA771C);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;color:white;box-shadow:0 2px 8px rgba(0,0,0,0.15);">🙏</div>
    <div style="flex:1;display:flex;flex-direction:column;align-items:flex-end;">
      <div style="background:linear-gradient(135deg, #8B1A1A 0%, #591010 100%);color:white;border-radius:18px 4px 18px 18px;padding:14px 20px;max-width:80%;box-shadow:0 3px 12px rgba(139,26,26,0.25);font-size:0.96rem;line-height:1.6;">
        ${escHtml(text)}
      </div>
      <div style="font-size:0.72rem;color:var(--color-text-muted);margin-top:4px;padding-right:4px;">You (Devotee)</div>
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

  // Format Markdown to HTML
  const formatted = formatMarkdownText(text);

  let sourcesHtml = '';
  if (sources && sources.length > 0) {
    const sourceList = sources.map(s =>
      `<span style="display:inline-block;padding:3px 10px;background:rgba(201,146,42,0.12);border:1px solid rgba(201,146,42,0.3);border-radius:12px;font-size:0.75rem;color:#784b00;font-weight:600;margin:2px;">📜 ${escHtml(s.title || s)}</span>`
    ).join(' ');
    sourcesHtml = `<div style="margin-top:14px;padding-top:10px;border-top:1px solid #EFE8DC;">
      <span style="font-size:0.72rem;color:#8B1A1A;letter-spacing:0.5px;font-weight:bold;">VERIFIED SOURCES: </span>${sourceList}
    </div>`;
  }

  const rawJsonText = JSON.stringify(text);

  div.innerHTML = `
    <div style="width:40px;height:40px;background:linear-gradient(135deg, #8B1A1A, #4A1A1A);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;color:white;box-shadow:0 2px 8px rgba(0,0,0,0.2);">🪷</div>
    <div style="flex:1;">
      <div class="chat-bubble" style="background:#FFFFFF;border:1px solid rgba(201,146,42,0.3);border-radius:4px 18px 18px 18px;padding:18px 22px;max-width:88%;box-shadow:0 3px 14px rgba(0,0,0,0.04);transition:box-shadow 0.3s ease, border-color 0.3s ease;">
        <div style="color:#2C1810;line-height:1.8;font-size:0.96rem;">${formatted}</div>
        ${sourcesHtml}
        <div style="margin-top:14px;padding-top:10px;border-top:1px solid #EFE8DC;display:flex;align-items:center;gap:10px;">
          <button class="tts-btn" onclick="toggleSpeech(this, ${rawJsonText})" style="border:1px solid #BF953F;background:#FFFDF9;border-radius:16px;padding:4px 12px;cursor:pointer;font-size:0.8rem;color:#8B1A1A;font-weight:600;display:inline-flex;align-items:center;gap:4px;transition:all 0.2s;">
            🔊 Speak in Voice
          </button>
        </div>
      </div>
      <div style="font-size:0.75rem;color:#8B1A1A;margin-top:5px;padding-left:4px;font-weight:600;">Guru Jijnasa AI</div>
    </div>
  `;
  container.appendChild(div);
  scrollToBottom();
  return div.querySelector('.chat-bubble');
}

// ── Markdown Formatter ──────────────────────────────────────────────────────
function formatMarkdownText(md) {
  let html = escHtml(md);
  // Headers
  html = html.replace(/### (.*?)(?:\n|$)/g, '<h4 style="color:#8B1A1A;font-family:Playfair Display,serif;margin:12px 0 6px;font-size:1.15rem;">$1</h4>');
  html = html.replace(/## (.*?)(?:\n|$)/g, '<h3 style="color:#8B1A1A;font-family:Playfair Display,serif;margin:14px 0 8px;font-size:1.25rem;">$1</h3>');
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Italic
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // Blockquotes
  html = html.replace(/^&gt; (.*?)(?:\n|$)/gm, '<blockquote style="border-left:3px solid #BF953F;margin:8px 0;padding:6px 12px;background:rgba(201,146,42,0.06);font-style:italic;color:#4A1A1A;">$1</blockquote>');
  // Bullet lists
  html = html.replace(/^\s*[-•]\s+(.*?)(?:\n|$)/gm, '<li style="margin-left:18px;line-height:1.7;">$1</li>');
  // Numbered lists
  html = html.replace(/^\s*(\d+)\.\s+(.*?)(?:\n|$)/gm, '<li style="margin-left:18px;line-height:1.7;"><strong>$1.</strong> $2</li>');
  // Newlines
  html = html.replace(/\n\n/g, '<div style="height:10px;"></div>');
  html = html.replace(/\n/g, '<br>');
  return html;
}

// ── Text-to-Speech (Spoken Voice Response) ──────────────────────────────────
window.toggleSpeech = function (btn, text) {
  if (window.speechSynthesis && window.speechSynthesis.speaking && activeSpeakerBtn === btn) {
    stopAllSpeech();
    return;
  }
  const bubble = btn.closest('.chat-bubble');
  speakText(btn, text, bubble);
};

window.speakWelcomeMessage = function (btn) {
  const text = "Namaskara! I am Guru Jijnasa, your voice and AI guide for the sacred Guru Parampara. Ask me about the 42 Gurus, Dvaita Vedanta, or Lekhana Seva.";
  const bubble = btn.closest('.chat-bubble');
  speakText(btn, text, bubble);
};

function speakText(btn, rawText, bubbleEl) {
  if (!window.speechSynthesis) {
    alert('Voice synthesis is not supported in this browser.');
    return;
  }

  stopAllSpeech();

  // Clean raw markdown to smooth spoken speech
  const cleanSpokenText = cleanForSpeech(rawText);

  const utter = new SpeechSynthesisUtterance(cleanSpokenText);
  utter.rate = 0.95; // Slightly measured, serene tempo for devotional clarity
  utter.pitch = 1.0;

  // Pick best available voice (prefer Indian English or natural voice)
  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find(v => v.lang === 'en-IN' || v.name.includes('India')) 
                      || voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Neural') || v.name.includes('Google')))
                      || voices.find(v => v.lang.startsWith('en'));
  if (preferredVoice) utter.voice = preferredVoice;

  activeSpeakerBtn = btn;
  currentUtterance = utter;

  if (btn) {
    btn.innerHTML = '⏹ Stop Voice';
    btn.style.background = '#8B1A1A';
    btn.style.color = 'white';
    btn.style.borderColor = '#8B1A1A';
  }

  if (bubbleEl) {
    bubbleEl.classList.add('speaking-glow');
  }

  const globalStopBtn = document.getElementById('global-stop-speech-btn');
  if (globalStopBtn) globalStopBtn.style.display = 'inline-flex';

  utter.onend = () => resetSpeechUI(btn, bubbleEl);
  utter.onerror = () => resetSpeechUI(btn, bubbleEl);

  window.speechSynthesis.speak(utter);
}

window.stopAllSpeech = function () {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  resetSpeechUI(activeSpeakerBtn, document.querySelector('.speaking-glow'));
  const globalStopBtn = document.getElementById('global-stop-speech-btn');
  if (globalStopBtn) globalStopBtn.style.display = 'none';
};

function resetSpeechUI(btn, bubbleEl) {
  if (btn) {
    btn.innerHTML = '🔊 Speak in Voice';
    btn.style.background = '#FFFDF9';
    btn.style.color = '#8B1A1A';
    btn.style.borderColor = '#BF953F';
  }
  if (bubbleEl) {
    bubbleEl.classList.remove('speaking-glow');
  }
  activeSpeakerBtn = null;
  currentUtterance = null;
  const globalStopBtn = document.getElementById('global-stop-speech-btn');
  if (globalStopBtn) globalStopBtn.style.display = 'none';
}

function cleanForSpeech(text) {
  return text
    .replace(/[#*`_~>]/g, ' ')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/https?:\/\/\S+/g, '')
    .replace(/\|\s*Sri\s*Uttaradi\s*Math/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
}

// ── Loading Indicator ───────────────────────────────────────────────────────
let loadingEl = null;
function showLoading() {
  const container = document.getElementById('chat-messages');
  loadingEl = document.createElement('div');
  loadingEl.id = 'chat-loading';
  loadingEl.style.cssText = 'display:flex;gap:12px;align-items:flex-start;';
  loadingEl.innerHTML = `
    <div style="width:40px;height:40px;background:linear-gradient(135deg, #8B1A1A, #4A1A1A);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;flex-shrink:0;">🪷</div>
    <div style="background:#FFFFFF;border:1px solid rgba(201,146,42,0.3);border-radius:4px 18px 18px 18px;padding:16px 22px;">
      <div style="display:flex;gap:6px;align-items:center;">
        <span style="font-size:0.85rem;color:#8B1A1A;font-weight:600;margin-right:6px;">Guru Jijnasa is contemplating...</span>
        <span style="width:8px;height:8px;background:#BF953F;border-radius:50%;animation:bounce 1.2s infinite 0s;display:inline-block;"></span>
        <span style="width:8px;height:8px;background:#BF953F;border-radius:50%;animation:bounce 1.2s infinite 0.2s;display:inline-block;"></span>
        <span style="width:8px;height:8px;background:#BF953F;border-radius:50%;animation:bounce 1.2s infinite 0.4s;display:inline-block;"></span>
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

function scrollToBottom() {
  const container = document.getElementById('chat-messages');
  if (container) container.scrollTop = container.scrollHeight;
}

function escHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
