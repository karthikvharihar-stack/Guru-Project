/**
 * Lekhana.js — Writing pad controller for Guru Lekhana Seva
 * Handles type mode, handwrite mode, mobile mode, AJAX progress saving
 */

'use strict';

document.addEventListener('DOMContentLoaded', function () {
  const root = document.getElementById('lekhana-pad-root');
  if (!root) return;

  // Read data from root element
  const sessionUuid = root.dataset.sessionUuid;
  const guruName = root.dataset.guruName;
  const lekhanaText = root.dataset.lekhanaText.trim();
  let target = parseInt(root.dataset.target, 10);
  let completed = parseInt(root.dataset.completed, 10);
  const currentMode = root.dataset.mode || 'type';
  const doneUrl = root.dataset.doneUrl;
  const entryUrl = root.dataset.entryUrl;
  const completeUrl = root.dataset.completeUrl;
  const csrfToken = root.dataset.csrf;

  // Canvas instances
  let drawCanvas = null;
  let mobileCanvas = null;

  // Initialize canvases (lazy — only when mode is selected)
  function initCanvas(canvasId) {
    if (canvasId === 'lekhana-canvas' && !drawCanvas) {
      const el = document.getElementById('lekhana-canvas');
      if (el) {
        drawCanvas = new LekhanCanvas('lekhana-canvas', { penSize: 3 });
        bindCanvasToolbar(drawCanvas, 'btn-undo', 'btn-redo', 'btn-clear');
      }
    }
    if (canvasId === 'lekhana-canvas-mobile' && !mobileCanvas) {
      const el = document.getElementById('lekhana-canvas-mobile');
      if (el) {
        mobileCanvas = new LekhanCanvas('lekhana-canvas-mobile', { penSize: 5 });
        bindCanvasToolbar(mobileCanvas, 'mobile-btn-undo', null, 'mobile-btn-clear');
      }
    }
  }

  function bindCanvasToolbar(canvasInst, undoId, redoId, clearId) {
    document.getElementById(undoId)?.addEventListener('click', () => canvasInst.undo());
    if (redoId) document.getElementById(redoId)?.addEventListener('click', () => canvasInst.redo());
    document.getElementById(clearId)?.addEventListener('click', () => canvasInst.clear());

    // Color dots
    document.querySelectorAll('.color-dot').forEach(dot => {
      dot.addEventListener('click', () => {
        document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
        dot.classList.add('active');
        canvasInst.setPenColor(dot.dataset.color);
      });
    });

    // Pen size
    const penSize = document.getElementById('pen-size');
    penSize?.addEventListener('input', () => canvasInst.setPenSize(penSize.value));
  }

  // Initialize based on initial mode
  if (currentMode === 'handwrite') initCanvas('lekhana-canvas');
  if (currentMode === 'mobile') initCanvas('lekhana-canvas-mobile');

  // ── Mode switching ─────────────────────────────────────────────────────────
  window.switchMode = function(mode) {
    ['type', 'handwrite', 'mobile'].forEach(m => {
      const panel = document.getElementById('panel-' + (m === 'handwrite' ? 'handwrite' : m));
      if (panel) panel.classList.remove('active');
    });
    // Fix panel IDs
    const panelMap = { type: 'panel-type', handwrite: 'panel-handwrite', mobile: 'panel-mobile' };
    const activePanel = document.getElementById(panelMap[mode]);
    if (activePanel) activePanel.classList.add('active');

    document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.mode-tab[data-mode="${mode}"]`)?.classList.add('active');

    // Initialize canvas on first use
    if (mode === 'handwrite') initCanvas('lekhana-canvas');
    if (mode === 'mobile') initCanvas('lekhana-canvas-mobile');
  };

  // ── Progress update ────────────────────────────────────────────────────────
  function updateProgress(newCount) {
    completed = newCount;
    const pct = Math.min(100, Math.round((completed / target) * 100));

    const countEl = document.getElementById('completed-count');
    const fillEl = document.getElementById('progress-fill');
    const pctEl = document.getElementById('progress-pct');

    if (countEl) {
      // Animate number
      countEl.classList.add('count-bounce');
      countEl.textContent = completed;
      setTimeout(() => countEl.classList.remove('count-bounce'), 400);
    }
    if (fillEl) fillEl.style.width = pct + '%';
    if (pctEl) pctEl.textContent = pct;

    if (completed >= target) {
      triggerCompletion();
    }
  }

  // ── API: save entry ────────────────────────────────────────────────────────
  async function saveEntry(data) {
    try {
      const res = await fetch(entryUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Server error ' + res.status);
      return await res.json();
    } catch (err) {
      console.error('saveEntry error:', err);
      showError('Could not save entry. Please check your connection.');
      return null;
    }
  }

  // ── API: complete session ──────────────────────────────────────────────────
  async function completeSession() {
    try {
      const res = await fetch(completeUrl, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
      });
      const data = await res.json();
      return data;
    } catch (err) {
      console.error('completeSession error:', err);
      return null;
    }
  }

  // ── TYPE MODE ──────────────────────────────────────────────────────────────
  const typeInput = document.getElementById('type-input');
  const typeHint = document.getElementById('type-hint');
  const btnTypeSubmit = document.getElementById('btn-type-submit');

  // Live validation hint
  typeInput?.addEventListener('input', () => {
    if (!lekhanaText) return;
    const typed = normalizeText(typeInput.value);
    const target_text = normalizeText(lekhanaText);
    if (typed.length === 0) {
      typeHint.textContent = '';
      typeInput.className = 'type-input';
    } else if (target_text.startsWith(typed)) {
      typeHint.textContent = '✓ Correct so far…';
      typeHint.style.color = '#4CAF50';
      typeInput.classList.remove('invalid');
      typeInput.classList.add('valid');
    } else {
      typeHint.textContent = 'Please match the text shown above';
      typeHint.style.color = 'var(--color-saffron)';
      typeInput.classList.remove('valid');
      typeInput.classList.add('invalid');
    }
  });

  // Submit on Enter key
  typeInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      btnTypeSubmit?.click();
    }
  });

  btnTypeSubmit?.addEventListener('click', async () => {
    const typed = typeInput.value.trim();
    if (!typed) {
      showError('Please type the Lekhana text before submitting.');
      return;
    }

    // Validate if lekhana text is set; if not (placeholder), accept anything
    if (lekhanaText && !validateText(typed, lekhanaText)) {
      showError('Text does not match. Please type the Lekhana exactly as shown.');
      typeInput.classList.add('invalid');
      return;
    }

    btnTypeSubmit.disabled = true;
    btnTypeSubmit.textContent = 'Saving…';

    const result = await saveEntry({ typed_text: typed });

    if (result && result.success) {
      typeInput.value = '';
      typeInput.className = 'type-input';
      typeHint.textContent = '';
      updateProgress(result.completed_count);
    }

    btnTypeSubmit.disabled = false;
    btnTypeSubmit.textContent = 'Submit & Next ›';
  });

  // ── HANDWRITE MODE ─────────────────────────────────────────────────────────
  document.getElementById('btn-draw-submit')?.addEventListener('click', async () => {
    if (!drawCanvas) return;
    if (drawCanvas.isEmpty()) {
      showError('Please write the Lekhana before saving.');
      return;
    }

    const drawingData = drawCanvas.toDataURL();
    const btn = document.getElementById('btn-draw-submit');
    btn.disabled = true;
    btn.textContent = 'Saving…';

    const result = await saveEntry({ drawing_data: drawingData, mode: 'handwrite' });
    if (result && result.success) {
      drawCanvas.clear();
      updateProgress(result.completed_count);
    }

    btn.disabled = false;
    btn.textContent = 'Save & Next ›';
  });

  // ── MOBILE MODE ────────────────────────────────────────────────────────────
  document.getElementById('btn-mobile-submit')?.addEventListener('click', async () => {
    if (!mobileCanvas) return;
    if (mobileCanvas.isEmpty()) {
      showError('Please write the Lekhana before saving.');
      return;
    }

    const drawingData = mobileCanvas.toDataURL();
    const btn = document.getElementById('btn-mobile-submit');
    btn.disabled = true;
    btn.textContent = 'Saving…';

    const result = await saveEntry({ drawing_data: drawingData, mode: 'mobile' });
    if (result && result.success) {
      mobileCanvas.clear();
      updateProgress(result.completed_count);
    }

    btn.disabled = false;
    btn.textContent = 'Save & Next ›';
  });

  // ── Completion ─────────────────────────────────────────────────────────────
  async function triggerCompletion() {
    const overlay = document.getElementById('completion-overlay');
    if (overlay) overlay.style.display = 'flex';

    const viewBtn = document.getElementById('btn-view-completion');
    if (viewBtn) viewBtn.href = doneUrl;

    // Notify server
    await completeSession();
  }

  // ── Helpers ────────────────────────────────────────────────────────────────
  function normalizeText(str) {
    return str.trim().toLowerCase().replace(/\s+/g, ' ');
  }

  function validateText(typed, reference) {
    // Remove all whitespace and punctuation, compare lowercase
    const clean = s => s.toLowerCase().replace(/[\s.,;!?'"]/g, '');
    const t = clean(typed);
    const r = clean(reference);
    // Accept if 80%+ match (to handle minor spacing/diacritic differences)
    if (t === r) return true;
    if (r.length === 0) return true; // no reference = accept anything
    const minLen = Math.min(t.length, r.length);
    let matches = 0;
    for (let i = 0; i < minLen; i++) if (t[i] === r[i]) matches++;
    return matches / r.length >= 0.80;
  }

  function showError(msg) {
    if (window.showToast) {
      window.showToast(msg, 'danger', 4000);
    } else {
      // Fallback
      const el = document.createElement('div');
      el.style.cssText = 'position:fixed;top:90px;right:20px;background:#c62828;color:white;padding:14px 20px;border-radius:8px;z-index:9999;max-width:300px;';
      el.textContent = msg;
      document.body.appendChild(el);
      setTimeout(() => el.remove(), 4000);
    }
  }

  // Initial progress display
  updateProgress(completed);
});
