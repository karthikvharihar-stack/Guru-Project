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
// DIGITAL DEEPA FEATURE
// ============================================================
function initDigitalDeepa() {
  const deepaCanvas = $('#deepa-canvas');
  const addDeepaBtn = $('#add-deepa-btn');
  
  if (!deepaCanvas || !addDeepaBtn) return;
  
  // Load existing diyas from local storage for demo purposes
  // In a real app, this would fetch from the backend
  let diyas = [];
  try {
    diyas = JSON.parse(localStorage.getItem('deepa_diyas') || '[]');
  } catch (e) {
    diyas = [];
  }
  
  function renderDiyas() {
    deepaCanvas.innerHTML = diyas.map((d, i) =>
      `<span class="deepa-diya" style="left:${d.x}%;top:${d.y}%;animation-delay:${d.delay}s;animation-duration:${d.duration}s" title="${d.text || 'A devotee'}" tabindex="0">🪔</span>`
    ).join('');
  }
  
  function addDiya() {
    const text = prompt('In remembrance of... (optional)');
    if (text === null) return; // Cancelled
    
    const diya = {
      x: 5 + Math.random() * 90,
      y: 5 + Math.random() * 90,
      text: text.trim() || 'A Devotee',
      delay: Math.random() * 2,
      duration: 1.5 + Math.random(),
      added: new Date().toISOString()
    };
    
    diyas.push(diya);
    if (diyas.length > 100) diyas.shift(); // Keep last 100
    
    localStorage.setItem('deepa_diyas', JSON.stringify(diyas));
    renderDiyas();
    window.showToast('Diya lit successfully!', 'success');
  }
  
  addDeepaBtn.addEventListener('click', addDiya);
  renderDiyas();
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
