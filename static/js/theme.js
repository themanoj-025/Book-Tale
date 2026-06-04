/* ═══════════════════════════════════════════════════════════════════
   theme.js — BookTale Cinematic Theme Switcher
   ═══════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const STORAGE_KEY = 'bt-theme';
  const HTML = document.documentElement;
  const BLINK_DURATION = 300; // ms

  // ── Detect initial theme ────────────────────────────────────────
  function getInitialTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') return stored;
    // Respect system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  // ── Apply theme ─────────────────────────────────────────────────
  function applyTheme(theme, animate) {
    HTML.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);

    // Update the toggle button icon
    const btn = document.getElementById('btThemeToggle');
    if (btn) {
      const icon = btn.querySelector('i') || btn.querySelector('.theme-icon');
      if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
      }
    }

    // Dispatch event so other modules can react
    document.dispatchEvent(new CustomEvent('bt-theme-changed', { detail: { theme } }));

    // Cinematic blink effect
    if (animate !== false) {
      cinematicBlink(theme);
    }
  }

  // ── Cinematic Blink ─────────────────────────────────────────────
  let blinkOverlay = null;

  function cinematicBlink(theme, intensity) {
    intensity = intensity || 0.15;

    if (!blinkOverlay) {
      blinkOverlay = document.createElement('div');
      blinkOverlay.id = 'bt-blink-overlay';
      blinkOverlay.style.cssText =
        'position:fixed;inset:0;z-index:99999;pointer-events:none;' +
        'background:#000;opacity:0;transition:opacity ' + (BLINK_DURATION / 2) + 'ms ease;';
      document.body.appendChild(blinkOverlay);
    }

    // Flash it
    blinkOverlay.style.transition = 'none';
    blinkOverlay.style.opacity = '0';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        blinkOverlay.style.transition = 'opacity ' + (BLINK_DURATION / 4) + 'ms ease';
        blinkOverlay.style.opacity = String(intensity);
        setTimeout(() => {
          blinkOverlay.style.transition = 'opacity ' + (BLINK_DURATION / 2) + 'ms ease';
          blinkOverlay.style.opacity = '0';
        }, BLINK_DURATION / 3);
      });
    });
  }

  // ── Toggle ──────────────────────────────────────────────────────
  function toggleTheme() {
    const current = HTML.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next, true);
  }

  // ── Init ────────────────────────────────────────────────────────
  function init() {
    // Apply saved/system theme
    const theme = getInitialTheme();
    applyTheme(theme, false);

    // Listen for toggle button clicks
    document.addEventListener('click', function (e) {
      const btn = e.target.closest('#btThemeToggle');
      if (btn) {
        e.preventDefault();
        toggleTheme();
      }
    });

    // Listen for system color scheme changes
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    if (mq.addEventListener) {
      mq.addEventListener('change', function (e) {
        // Only auto-switch if user hasn't manually set a preference
        if (!localStorage.getItem(STORAGE_KEY)) {
          applyTheme(e.matches ? 'dark' : 'light', true);
        }
      });
    }
  }

  // ── Expose ──────────────────────────────────────────────────────
  window.BookTale = window.BookTale || {};
  window.BookTale.theme = { toggle: toggleTheme, apply: applyTheme, getInitialTheme: getInitialTheme };

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
