/**
 * LekhanCanvas — HTML5 Canvas drawing engine for Guru Lekhana Seva
 * Supports: mouse, touch (single touch), stylus (Pointer Events)
 * Includes smoothing, history (undo/redo), and responsive resizing.
 */

'use strict';

class LekhanCanvas {
  /**
   * Initialize the canvas engine
   * @param {string} canvasId - The ID of the canvas element
   * @param {Object} options - Configuration options
   */
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) throw new Error(`Canvas #${canvasId} not found`);
    this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });
    
    // Options with defaults
    this.penColor = options.penColor || '#2C1810';
    this.penSize = options.penSize || 3;
    this.backgroundColor = options.backgroundColor || '#FEFDF7';
    this.onDrawEnd = options.onDrawEnd || (() => {});
    
    // Drawing state
    this.isDrawing = false;
    this.lastX = 0;
    this.lastY = 0;
    this.lastPressure = 0.5;
    
    // Bezier smoothing queue
    this.points = []; 
    
    // Undo/redo stacks
    this.history = [];
    this.redoStack = [];
    this.MAX_HISTORY = 20;
    
    this.init();
  }
  
  /**
   * Set up the canvas, event listeners, and initial state
   */
  init() {
    this.resizeCanvas();
    this.fillBackground();
    this.saveToHistory();
    this.attachEvents();
    
    // Setup resize handler with debounce to prevent excessive redrawing
    window.addEventListener('resize', this.debounce(() => this.resize(), 300));
  }
  
  /**
   * Properly size the canvas accounting for high DPI displays (Retina)
   */
  resizeCanvas() {
    const container = this.canvas.parentElement;
    const rect = container.getBoundingClientRect();
    const pixelRatio = window.devicePixelRatio || 1;
    
    // Attempt to save current drawing to restore after resize
    let imageData = null;
    try {
      if (this.canvas.width > 0 && this.canvas.height > 0) {
        imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
      }
    } catch (e) {
      console.warn("Could not save image data before resize", e);
    }
    
    // Set actual canvas size (internal resolution)
    this.canvas.width = Math.floor(rect.width * pixelRatio);
    this.canvas.height = Math.floor((rect.height || 400) * pixelRatio);
    
    // Set CSS display size
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = (rect.height || 400) + 'px';
    
    // Scale context to match pixel ratio
    this.ctx.scale(pixelRatio, pixelRatio);
    
    this.fillBackground();
    
    // Attempt to restore drawing
    if (imageData) {
      try { 
        this.ctx.putImageData(imageData, 0, 0); 
      } catch(e) {
        console.warn("Could not restore image data after resize", e);
      }
    }
    
    this.updateContextSettings();
  }
  
  /**
   * Ensure context settings are correct (often reset after resize)
   */
  updateContextSettings() {
    this.ctx.lineCap = 'round';
    this.ctx.lineJoin = 'round';
    this.ctx.imageSmoothingEnabled = true;
  }
  
  /**
   * Fill the canvas with the background color
   */
  fillBackground() {
    this.ctx.fillStyle = this.backgroundColor;
    // Fill slightly larger area to avoid edge artifacts
    this.ctx.fillRect(-10, -10, (this.canvas.width / (window.devicePixelRatio || 1)) + 20, (this.canvas.height / (window.devicePixelRatio || 1)) + 20);
  }
  
  /**
   * Attach all necessary input events, preferring Pointer Events if available
   */
  attachEvents() {
    // Disable context menu on right click to allow drawing
    this.canvas.addEventListener('contextmenu', e => e.preventDefault());
    
    if (window.PointerEvent) {
      // Modern browsers: handles mouse, touch, and stylus uniformly
      this.canvas.addEventListener('pointerdown', e => this.onPointerDown(e));
      this.canvas.addEventListener('pointermove', e => this.onPointerMove(e));
      this.canvas.addEventListener('pointerup', e => this.onPointerUp(e));
      this.canvas.addEventListener('pointercancel', e => this.onPointerUp(e));
      this.canvas.addEventListener('pointerleave', e => this.onPointerUp(e));
    } else {
      // Fallback for older browsers
      this.canvas.addEventListener('mousedown', e => this.onMouseDown(e));
      this.canvas.addEventListener('mousemove', e => this.onMouseMove(e));
      this.canvas.addEventListener('mouseup', e => this.onPointerUp(e));
      this.canvas.addEventListener('mouseleave', e => this.onPointerUp(e));
      
      // Touch events need passive: false to call preventDefault
      this.canvas.addEventListener('touchstart', e => { 
        e.preventDefault(); 
        this.onTouchStart(e); 
      }, { passive: false });
      this.canvas.addEventListener('touchmove', e => { 
        e.preventDefault(); 
        this.onTouchMove(e); 
      }, { passive: false });
      this.canvas.addEventListener('touchend', e => this.onPointerUp(e), { passive: false });
    }
  }
  
  // ─── Input Handlers ───────────────────────────────────────────
  
  onPointerDown(e) {
    if (e.button !== 0 && e.pointerType === 'mouse') return; // Only left click for mouse
    
    this.canvas.setPointerCapture(e.pointerId);
    this.isDrawing = true;
    this.points = [];
    
    const pos = this.getCanvasPos(e);
    this.lastX = pos.x;
    this.lastY = pos.y;
    this.lastPressure = e.pressure !== undefined ? e.pressure : 0.5;
    
    this.points.push(pos);
    this.redoStack = []; // Clear redo stack on new action
    
    // Draw a single dot in case of a simple tap
    this.ctx.beginPath();
    this.ctx.arc(pos.x, pos.y, this.penSize / 2, 0, Math.PI * 2);
    this.ctx.fillStyle = this.penColor;
    this.ctx.fill();
  }
  
  onPointerMove(e) {
    if (!this.isDrawing) return;
    
    // Prevent default scrolling on touch devices if captured as pointer
    if (e.pointerType === 'touch') {
      e.preventDefault();
    }
    
    const pos = this.getCanvasPos(e);
    const pressure = e.pressure !== undefined ? e.pressure : 0.5;
    
    this.points.push(pos);
    this.drawSmooth(pos, pressure);
    
    this.lastX = pos.x;
    this.lastY = pos.y;
    this.lastPressure = pressure;
  }
  
  onPointerUp(e) {
    if (!this.isDrawing) return;
    this.isDrawing = false;
    this.points = [];
    this.saveToHistory();
    this.onDrawEnd();
  }
  
  // ─── Mouse Fallbacks ───────────────────────────────────────────
  
  onMouseDown(e) {
    if (e.button !== 0) return;
    this.isDrawing = true;
    this.points = [];
    const pos = this.getCanvasPos(e);
    this.lastX = pos.x;
    this.lastY = pos.y;
    this.redoStack = [];
    this.points.push(pos);
  }
  
  onMouseMove(e) {
    if (!this.isDrawing) return;
    const pos = this.getCanvasPos(e);
    this.points.push(pos);
    this.drawSmooth(pos, 0.5);
    this.lastX = pos.x;
    this.lastY = pos.y;
  }
  
  // ─── Touch Fallbacks ───────────────────────────────────────────
  
  onTouchStart(e) {
    if (e.touches.length > 1) return; // Ignore multi-touch
    const touch = e.touches[0];
    this.isDrawing = true;
    this.points = [];
    const pos = this.getCanvasPos(touch);
    this.lastX = pos.x;
    this.lastY = pos.y;
    this.redoStack = [];
    this.points.push(pos);
  }
  
  onTouchMove(e) {
    if (!this.isDrawing) return;
    const touch = e.touches[0];
    const pos = this.getCanvasPos(touch);
    this.points.push(pos);
    this.drawSmooth(pos, 0.5);
    this.lastX = pos.x;
    this.lastY = pos.y;
  }
  
  // ─── Core Drawing Logic ───────────────────────────────────────
  
  /**
   * Draw with Bezier smoothing to prevent jagged edges
   */
  drawSmooth(current, pressure = 0.5) {
    const ctx = this.ctx;
    const last = { x: this.lastX, y: this.lastY };
    
    this.updateContextSettings();
    
    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    
    if (this.points.length > 2) {
      // Quadratic Bezier interpolation using midpoints
      const p0 = this.points[this.points.length - 3];
      const p1 = this.points[this.points.length - 2];
      const mid1 = { x: (p0.x + p1.x) / 2, y: (p0.y + p1.y) / 2 };
      const mid2 = { x: (p1.x + current.x) / 2, y: (p1.y + current.y) / 2 };
      
      // Move back slightly to create seamless connection
      ctx.moveTo(mid1.x, mid1.y);
      ctx.quadraticCurveTo(p1.x, p1.y, mid2.x, mid2.y);
    } else {
      // Simple line for the first few points
      ctx.lineTo(current.x, current.y);
    }
    
    // Vary line width slightly based on pressure if available
    // pressure is usually 0.0 to 1.0. Default mouse is 0.5.
    const pressureMod = 0.5 + pressure; // maps 0-1 to 0.5-1.5
    const lineWidth = Math.max(1, this.penSize * pressureMod);
    
    ctx.strokeStyle = this.penColor;
    ctx.lineWidth = lineWidth;
    
    // Subtle opacity adjustment based on speed/pressure
    ctx.globalAlpha = Math.min(1, 0.85 + (pressure * 0.2));
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  }
  
  // ─── Helpers ──────────────────────────────────────────────────
  
  /**
   * Get accurate canvas coordinates regardless of scaling
   */
  getCanvasPos(e) {
    const rect = this.canvas.getBoundingClientRect();
    const pixelRatio = window.devicePixelRatio || 1;
    
    // Extract clientX/Y from either mouse/pointer event or touch object
    const clientX = e.clientX !== undefined ? e.clientX : (e.touches && e.touches[0] ? e.touches[0].clientX : 0);
    const clientY = e.clientY !== undefined ? e.clientY : (e.touches && e.touches[0] ? e.touches[0].clientY : 0);
    
    // Map screen coordinate to internal canvas resolution coordinate
    return {
      x: (clientX - rect.left) * (this.canvas.width / rect.width / pixelRatio),
      y: (clientY - rect.top) * (this.canvas.height / rect.height / pixelRatio)
    };
  }
  
  // ─── Public API ───────────────────────────────────────────────
  
  /**
   * Clear the entire canvas
   */
  clear() {
    this.fillBackground();
    this.redoStack = [];
    this.saveToHistory();
    this.onDrawEnd();
  }
  
  /**
   * Undo last stroke
   */
  undo() {
    if (this.history.length <= 1) return; // Keep initial empty state
    
    // Pop current state to redo stack
    this.redoStack.push(this.history.pop());
    
    // Restore previous state
    const previousState = this.history[this.history.length - 1];
    this.ctx.putImageData(previousState, 0, 0);
    this.onDrawEnd();
  }
  
  /**
   * Redo last undone stroke
   */
  redo() {
    if (!this.redoStack.length) return;
    
    const state = this.redoStack.pop();
    this.history.push(state);
    this.ctx.putImageData(state, 0, 0);
    this.onDrawEnd();
  }
  
  saveToHistory() {
    try {
      const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
      this.history.push(imageData);
      if (this.history.length > this.MAX_HISTORY) {
        this.history.shift();
      }
    } catch(e) {
      console.warn("Could not save history state", e);
    }
  }
  
  /**
   * Check if canvas is virtually empty (matches background color)
   */
  isEmpty() {
    try {
      const data = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height).data;
      
      // Parse background hex to RGB roughly
      let r = 254, g = 253, b = 247; // Default #FEFDF7
      if (this.backgroundColor.startsWith('#')) {
        const hex = this.backgroundColor.substring(1);
        if (hex.length === 6) {
          r = parseInt(hex.substring(0, 2), 16);
          g = parseInt(hex.substring(2, 4), 16);
          b = parseInt(hex.substring(4, 6), 16);
        }
      }
      
      // Check pixels (skip every 16th pixel for performance)
      for (let i = 0; i < data.length; i += 64) {
        // If pixel differs from background by more than threshold
        if (Math.abs(data[i] - r) > 10 || 
            Math.abs(data[i+1] - g) > 10 || 
            Math.abs(data[i+2] - b) > 10) {
          return false;
        }
      }
      return true;
    } catch(e) {
      console.warn("Cannot verify if empty", e);
      return false; // Assume not empty if can't read
    }
  }
  
  toDataURL(type = 'image/png', quality = 1.0) {
    return this.canvas.toDataURL(type, quality);
  }
  
  toBlob(callback, type = 'image/png', quality = 1.0) {
    if (this.canvas.toBlob) {
      this.canvas.toBlob(callback, type, quality);
    } else {
      // Fallback
      const dataURL = this.toDataURL(type, quality);
      const arr = dataURL.split(',');
      const mime = arr[0].match(/:(.*?);/)[1];
      const bstr = atob(arr[1]);
      let n = bstr.length;
      const u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      callback(new Blob([u8arr], { type: mime }));
    }
  }
  
  setPenColor(color) { 
    this.penColor = color; 
  }
  
  setPenSize(size) { 
    this.penSize = parseInt(size, 10); 
  }
  
  /**
   * Advanced resize handling to preserve drawing
   */
  resize() {
    try {
      const dataURL = this.canvas.toDataURL();
      this.resizeCanvas();
      const img = new Image();
      img.onload = () => {
        // Draw the saved image back onto the resized canvas
        const pixelRatio = window.devicePixelRatio || 1;
        // Reset transform to draw image correctly
        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.drawImage(img, 0, 0, this.canvas.width, this.canvas.height);
        // Restore scale
        this.ctx.scale(pixelRatio, pixelRatio);
        this.saveToHistory();
      };
      img.src = dataURL;
    } catch(e) {
      // Cross-origin issues might prevent toDataURL
      this.resizeCanvas();
    }
  }
  
  debounce(fn, delay) {
    let t;
    return (...args) => { 
      clearTimeout(t); 
      t = setTimeout(() => fn(...args), delay); 
    };
  }
}

// Expose to window
window.LekhanCanvas = LekhanCanvas;
