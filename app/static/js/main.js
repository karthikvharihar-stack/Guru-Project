/**
 * Uttaradi Math — Guru Lekhana Seva
 * Main JavaScript file
 */

'use strict';

// ============================================================
// UTILITY FUNCTIONS
// ============================================================
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function debounce(fn, delay = 300) {
  let timeout;
  return (...args) => { 
    clearTimeout(timeout); 
    timeout = setTimeout(() => fn(...args), delay); 
  };
}

// ============================================================
// NAVBAR: scroll shadow + hamburger
// ============================================================
function initNavbar() {
  const navbar = $('#main-navbar');
  const hamburger = $('#hamburger-btn');
  const mobileMenu = $('#mobile-menu');
  
  if (!navbar) return;
  
  // Scroll shadow
  window.addEventListener('scroll', debounce(() => {
    if (window.scrollY > 10) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }, 50));
  
  // Hamburger toggle
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      hamburger.classList.toggle('active', isOpen);
      hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    
    // Close menu on outside click
    document.addEventListener('click', (e) => {
      if (!navbar.contains(e.target) && mobileMenu.classList.contains('open')) {
        mobileMenu.classList.remove('open');
        hamburger.classList.remove('active');
        hamburger.setAttribute('aria-expanded', 'false');
      }
    });
  }
  
  // Active link highlight
  const currentPath = window.location.pathname;
  $$('.navbar-nav a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
}

// ============================================================
// FLASH MESSAGES: auto-dismiss
// ============================================================
function initFlashMessages() {
  $$('.flash').forEach(flash => {
    // Auto-dismiss after 5 seconds
    setTimeout(() => dismissFlash(flash), 5000);
    
    const closeBtn = flash.querySelector('.flash-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => dismissFlash(flash));
    }
  });
}

function dismissFlash(flash) {
  flash.style.opacity = '0';
  flash.style.transform = 'translateX(20px)';
  setTimeout(() => flash.remove(), 300);
}

// Show a toast notification programmatically
window.showToast = function(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:10px;';
    document.body.appendChild(container);
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span><button onclick="this.parentElement.remove()" style="background:none;border:none;margin-left:15px;font-size:1.2rem;cursor:pointer;">&times;</button>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, duration);
};

// ============================================================
// SMOOTH SCROLL
// ============================================================
function initSmoothScroll() {
  $$('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const targetId = anchor.getAttribute('href');
      if (targetId === '#') return;
      
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Update URL hash without jumping
        history.pushState(null, null, targetId);
      }
    });
  });
}

// ============================================================
// INTERSECTION OBSERVER: fade-in animations
// ============================================================
function initFadeAnimations() {
  if (!('IntersectionObserver' in window)) return;
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
  
  $$('.fade-in, .fade-in-up, .guru-card, .book-card, .media-card, .timeline-item').forEach(el => {
    observer.observe(el);
  });
}

// ============================================================
// DIYA ANIMATION
// ============================================================
function initDiyas() {
  // Randomize diya flicker timing to make it look natural
  $$('.diya-flame, .deepa-diya').forEach((el, i) => {
    el.style.animationDelay = `${(i * 0.3) % 2}s`;
    el.style.animationDuration = `${1.5 + Math.random()}s`;
  });
}

// ============================================================
// DIGITAL DEEPA FEATURE (LIVE REFRESH & COUNTER)
// ============================================================
function initDigitalDeepa() {
  const deepaCanvas = $('#deepa-canvas');
  const countEl = $('#deepa-live-count');
  
  if (!deepaCanvas) return;
  
  let currentDeepaCount = 0;

  window.fetchDeepaData = async function () {
    try {
      const res = await fetch('/api/deepa');
      if (res.ok) {
        const data = await res.json();
        renderDeepaState(data);
      }
    } catch (e) {
      console.warn('Could not fetch deepa data:', e);
      renderDeepaState({ count: 0, diyas: [] });
    }
  };

  function renderDeepaState(data) {
    currentDeepaCount = data.count || 0;
    if (countEl) {
      countEl.innerHTML = `${currentDeepaCount} <span style="font-size: 0.85rem; color: #E5C158; font-weight: normal;">Deepas Lit</span>`;
    }
    
    if (deepaCanvas) {
      if (data.diyas && data.diyas.length > 0) {
        deepaCanvas.innerHTML = data.diyas.map((d, i) => {
          const tooltip = `${d.name || 'A Devotee'} — ${d.prayer || 'Guru Smarana'}`;
          const delay = (i * 0.2) % 2;
          const duration = 1.8 + ((i * 0.3) % 1.2);
          return `<span class="deepa-diya" style="animation-delay:${delay}s;animation-duration:${duration}s" data-tooltip="${escHtml(tooltip)}" tabindex="0">🪔</span>`;
        }).join('');
      } else {
        deepaCanvas.innerHTML = `<div id="deepa-empty-altar" style="color:rgba(253,246,227,0.55);font-size:0.9rem;font-style:italic;padding:12px 0;">🪔 No Deepas offered yet in this session. Tap "Light a Deepa" below to offer the first lamp of devotion!</div>`;
      }
    }
  }

  window.openDeepaModal = function () {
    const modal = document.getElementById('deepaOfferingModal');
    if (modal) {
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      setTimeout(() => document.getElementById('deepa-devotee-name')?.focus(), 100);
    }
    // Pre-prime audio player on user click to unlock browser media policies
    try {
      const player = document.getElementById('deepaAudioPlayer');
      if (player) {
        player.load();
      }
    } catch (e) {}
  };

  window.closeDeepaModal = function (e) {
    if (!e || e.target.id === 'deepaOfferingModal' || e.target.tagName === 'BUTTON') {
      const modal = document.getElementById('deepaOfferingModal');
      if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
      }
    }
  };

  window.submitDeepaOffering = async function () {
    const nameInput = document.getElementById('deepa-devotee-name');
    const prayerInput = document.getElementById('deepa-devotee-prayer');
    const name = nameInput ? nameInput.value.trim() : '';
    const prayer = prayerInput ? prayerInput.value.trim() : '';

    // 1. Immediately dismiss modal dialog and reset inputs
    window.closeDeepaModal();
    if (nameInput) nameInput.value = '';
    if (prayerInput) prayerInput.value = '';

    // 2. Immediately scroll smoothly to the Diya Altar section on the homepage
    const deepaSection = document.getElementById('deepa-section') || deepaCanvas;
    if (deepaSection) {
      deepaSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                      document.querySelector('input[name="csrf_token"]')?.value || '';

    let newCount = currentDeepaCount + 1;
    let newDiyaObj = {
      name: name || 'A Devotee',
      prayer: prayer || 'Guru Smarana & Lokakshema'
    };

    // 3. Immediately increment count and animate
    currentDeepaCount = newCount;
    if (countEl) {
      countEl.innerHTML = `${currentDeepaCount} <span style="font-size: 0.85rem; color: #E5C158; font-weight: normal;">Deepas Lit</span>`;
      countEl.style.transform = 'scale(1.2)';
      countEl.style.color = '#FCF6BA';
      setTimeout(() => {
        countEl.style.transform = 'scale(1)';
        countEl.style.color = '#FFFDF9';
      }, 350);
    }

    // 4. Remove empty altar message and prepend sparkling Diya
    const emptyMsg = document.getElementById('deepa-empty-altar');
    if (emptyMsg) emptyMsg.remove();

    if (deepaCanvas) {
      const tooltip = `${newDiyaObj.name} — ${newDiyaObj.prayer}`;
      const newDiyaHtml = `<span class="deepa-diya deepa-diya-new" data-tooltip="${escHtml(tooltip)}" tabindex="0" style="background: radial-gradient(circle, rgba(252, 246, 186, 0.7) 0%, rgba(201, 146, 42, 0.3) 60%, transparent 90%);">🪔</span>`;
      deepaCanvas.insertAdjacentHTML('afterbegin', newDiyaHtml);
    }

    // 5. Play sacred temple chime and "Jai Sri Ram" voice chant
    playDevotionalDeepaVoice();

    if (window.showToast) {
      window.showToast('॥ जय श्री राम ॥ Deepa offered with devotion!', 'success');
    }

    // 6. Background sync with backend API
    try {
      const res = await fetch('/api/deepa/light', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ name: name, prayer: prayer })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.count && data.count > currentDeepaCount) {
          currentDeepaCount = data.count;
          if (countEl) {
            countEl.innerHTML = `${currentDeepaCount} <span style="font-size: 0.85rem; color: #E5C158; font-weight: normal;">Deepas Lit</span>`;
          }
        }
      }
    } catch (err) {
      console.warn('Deepa server sync warning:', err);
    }
  };

  window.playDevotionalDeepaVoice = function () {
    // 1. Play Resonant Temple Bell Chime (Web Audio API)
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        const ctx = new AudioCtx();
        if (ctx.state === 'suspended') {
          ctx.resume();
        }
        const now = ctx.currentTime;
        
        // Harmonic frequencies for authentic Indian temple bell (Ghanta)
        const freqs = [587.33, 880.00, 1174.66, 1760.00];
        freqs.forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          
          osc.type = idx === 0 ? 'sine' : 'triangle';
          osc.frequency.setValueAtTime(freq, now);
          
          gain.gain.setValueAtTime(0.25 / (idx + 1), now);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + 2.8 + idx * 0.3);
          
          osc.connect(gain);
          gain.connect(ctx.destination);
          
          osc.start(now);
          osc.stop(now + 3.2);
        });
      }
    } catch (e) {
      console.warn('AudioContext temple chime:', e);
    }

    // 2. Play Pure "Jai Shri Ram" Voice Audio
    try {
      const player = document.getElementById('deepaAudioPlayer');
      if (player) {
        player.currentTime = 0;
        player.volume = 1.0;
        const playPromise = player.play();
        if (playPromise !== undefined) {
          playPromise.catch(err => {
            console.warn('HTML5 audio element error, trying secondary fallback:', err);
            tryFallbackAudio();
          });
        }
      } else {
        tryFallbackAudio();
      }
    } catch (err) {
      console.warn('Audio playback exception:', err);
      tryFallbackAudio();
    }

    function tryFallbackAudio() {
      try {
        const fallbackAudio = new Audio('/static/audio/jai_shri_ram.wav');
        fallbackAudio.volume = 1.0;
        fallbackAudio.play().catch(() => {
          fallbackSpeechSynthesis();
        });
      } catch (e) {
        fallbackSpeechSynthesis();
      }
    }

    function fallbackSpeechSynthesis() {
      try {
        if (window.speechSynthesis) {
          window.speechSynthesis.cancel();
          const chantUtter = new SpeechSynthesisUtterance("Jai Shri Ram");
          chantUtter.rate = 0.95;
          chantUtter.pitch = 1.0;
          chantUtter.volume = 1.0;
          
          const voices = window.speechSynthesis.getVoices();
          const devotionalVoice = voices.find(v => v.lang === 'hi-IN' || v.lang === 'sa' || v.lang === 'mr-IN')
                               || voices.find(v => v.lang === 'en-IN' || v.name.includes('India'))
                               || voices.find(v => v.lang.startsWith('en'));
          if (devotionalVoice) {
            chantUtter.voice = devotionalVoice;
          }
          window.speechSynthesis.speak(chantUtter);
        }
      } catch (e) {
        console.warn('SpeechSynthesis fallback error:', e);
      }
    }
  }

  // Initial fetch on page load
  window.fetchDeepaData();
}

// ============================================================
// TAB SWITCHING (generic)
// ============================================================
function initTabs() {
  $$('.tabs').forEach(tabGroup => {
    const buttons = $$('.tab-btn', tabGroup);
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.dataset.tab;
        if (!targetId) return;
        
        // Find the container for these panels
        // Assume panels are siblings of the tabs container or in a specific wrapper
        let panelContainer = tabGroup.nextElementSibling;
        if (!panelContainer || !panelContainer.classList.contains('tab-content')) {
          panelContainer = btn.closest('.tabs-wrapper') || document;
        }
        
        // Deactivate all in group
        buttons.forEach(b => b.classList.remove('active'));
        
        // We only want to deactivate panels related to this tab group
        // If panels are grouped in a container, query within it. Otherwise, query all panels.
        const panels = panelContainer === document ? $$('.tab-panel') : $$('.tab-panel', panelContainer);
        panels.forEach(p => p.classList.remove('active'));
        
        // Activate selected
        btn.classList.add('active');
        const panel = document.getElementById(targetId);
        if (panel) {
          panel.classList.add('active');
        }
      });
    });
  });
}

// ============================================================
// CURRENT YEAR IN FOOTER
// ============================================================
function initFooterYear() {
  const yearEl = document.getElementById('current-year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
}

// ============================================================
// LAZY IMAGE LOADING
// ============================================================
function initLazyImages() {
  if (!('IntersectionObserver' in window)) {
    // Fallback for older browsers
    $$('img[data-src]').forEach(img => {
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
    });
    return;
  }
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
          // Add fade in effect
          img.style.opacity = 0;
          img.onload = () => {
            img.style.transition = 'opacity 0.5s ease';
            img.style.opacity = 1;
          };
        }
        observer.unobserve(img);
      }
    });
  }, { rootMargin: '50px' }); // Load a bit before it comes into view
  
  $$('img[data-src]').forEach(img => observer.observe(img));
}

// ============================================================
// SEARCH INTEGRATION (navbar search)
// ============================================================
function initNavbarSearch() {
  const searchInput = $('#navbar-search');
  if (!searchInput) return;
  
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && searchInput.value.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchInput.value.trim())}`;
    }
  });
  
  // Example basic autocomplete visual logic
  const searchWrapper = searchInput.closest('.search-wrapper');
  if (searchWrapper) {
    const dropdown = searchWrapper.querySelector('.search-dropdown');
    
    if (dropdown) {
      searchInput.addEventListener('input', debounce(() => {
        if (searchInput.value.trim().length > 2) {
          dropdown.classList.add('active');
          // In real app, fetch results here
        } else {
          dropdown.classList.remove('active');
        }
      }, 300));
      
      document.addEventListener('click', (e) => {
        if (!searchWrapper.contains(e.target)) {
          dropdown.classList.remove('active');
        }
      });
    }
  }
}

// ============================================================
// ACCORDION
// ============================================================
function initAccordions() {
  $$('.accordion-header').forEach(header => {
    header.addEventListener('click', () => {
      const item = header.closest('.accordion-item');
      if (!item) return;
      
      const body = item.querySelector('.accordion-body');
      if (!body) return;
      
      const isOpen = item.classList.contains('open');
      
      // Optional: Close all siblings
      const container = item.closest('.accordion-container');
      if (container) {
        $$('.accordion-item', container).forEach(el => {
          el.classList.remove('open');
          const elBody = el.querySelector('.accordion-body');
          if (elBody) elBody.style.maxHeight = '0';
        });
      }
      
      if (!isOpen) {
        item.classList.add('open');
        body.style.maxHeight = body.scrollHeight + 'px';
      }
    });
  });
}

// ============================================================
// CONFIRM DIALOGS (for delete actions)
// ============================================================
function initConfirmActions() {
  $$('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm || 'Are you sure you want to perform this action?')) {
        e.preventDefault();
      }
    });
  });
}

// ============================================================
// MODAL LOGIC
// ============================================================
function initModals() {
  $$('[data-modal-target]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = trigger.dataset.modalTarget;
      const modal = document.getElementById(targetId);
      if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // prevent scrolling
      }
    });
  });
  
  $$('.modal-close, .modal-overlay').forEach(el => {
    el.addEventListener('click', (e) => {
      // If clicking overlay, ensure it's not bubbling from modal content
      if (e.target === el || el.classList.contains('modal-close')) {
        const overlay = el.closest('.modal-overlay');
        if (overlay) {
          overlay.classList.remove('active');
          document.body.style.overflow = ''; // restore scrolling
        }
      }
    });
  });
}

// ============================================================
// INIT ALL ON DOM READY
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initFlashMessages();
  initSmoothScroll();
  initFadeAnimations();
  initDiyas();
  initDigitalDeepa();
  initTabs();
  initFooterYear();
  initLazyImages();
  initNavbarSearch();
  initAccordions();
  initConfirmActions();
  initModals();
});
