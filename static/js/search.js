/* ═══════════════════════════════════════════════════════════════════
   search.js — BookTale Live Search with cover previews
   - Debounced (300ms) search via GET /api/books/search?q=
   - Floating dropdown with cover thumbnails
   - Arrow key navigation + Enter to go to book detail
   - ScaleY open/close animation
   ═══════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const SEARCH_ENDPOINT = '/api/books';
  const DEBOUNCE_MS = 300;
  const MAX_RESULTS = 8;

  // ── State ──────────────────────────────────────────────────────
  let searchContainer = null;
  let searchInput = null;
  let searchResults = null;
  let activeIndex = -1;
  let currentItems = [];
  let debounceTimer = null;
  let isOpen = false;

  // ── Init ────────────────────────────────────────────────────────
  function init() {
    // Look for the sidebar search input
    searchInput = document.querySelector('.rside-search input') ||
                  document.querySelector('#searchInput');

    if (!searchInput) return;

    // Create dropdown container
    searchContainer = document.createElement('div');
    searchContainer.className = 'bt-search-dropdown';
    searchContainer.id = 'btSearchDropdown';
    searchContainer.setAttribute('role', 'listbox');
    searchContainer.setAttribute('aria-label', 'Search suggestions');
    searchInput.parentNode.appendChild(searchContainer);

    searchResults = searchContainer;

    // Bind events
    searchInput.addEventListener('input', onInput);
    searchInput.addEventListener('keydown', onKeyDown);
    searchInput.addEventListener('blur', function () {
      // Delay so click on result registers
      setTimeout(() => close(), 200);
    });
    searchInput.addEventListener('focus', function () {
      if (currentItems.length > 0) open();
    });

    // Listen for overlay search integration
    document.addEventListener('bt-search-overlay', function (e) {
      const q = e.detail && e.detail.query;
      if (q) {
        currentItems = e.detail.results || [];
        if (currentItems.length > 0) open();
      }
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && isOpen) {
        close();
        searchInput.blur();
      }
    });

    // Close on click outside
    document.addEventListener('click', function (e) {
      if (isOpen && !e.target.closest('.bt-search-dropdown') &&
          !e.target.closest('.rside-search')) {
        close();
      }
    });
  }

  // ── Input Handler (debounced) ──────────────────────────────────
  function onInput() {
    const q = searchInput.value.trim();
    clearTimeout(debounceTimer);

    if (q.length < 2) {
      close();
      return;
    }

    debounceTimer = setTimeout(() => performSearch(q), DEBOUNCE_MS);
  }

  async function performSearch(q) {
    try {
      const resp = await fetch(SEARCH_ENDPOINT + '?q=' + encodeURIComponent(q) + '&limit=' + MAX_RESULTS);
      if (!resp.ok) return;
      const data = await resp.json();

      // Support both envelope and raw array
      let items = Array.isArray(data) ? data : (data.data || data.books || data.results || []);

      items = items.slice(0, MAX_RESULTS);
      currentItems = items;
      activeIndex = -1;

      if (items.length === 0) {
        renderEmpty();
        open();
        return;
      }

      renderResults(items);
      open();
    } catch (err) {
      // Silent fail
    }
  }

  // ── Render ──────────────────────────────────────────────────────
  function renderResults(items) {
    if (!searchResults) return;

    let html = '';
    items.forEach(function (item, idx) {
      const title = item.title || item.name || 'Unknown';
      const author = item.author || '';
      const coverUrl = item.cover_url || item.thumbnail || '';
      const bookId = item.book_id || item.id || '';
      const avail = item.available_copies > 0;

      const coverHtml = coverUrl
        ? '<img src="' + escapeAttr(coverUrl) + '" alt="" class="bt-search-cover" loading="lazy">'
        : '<div class="bt-search-cover bt-search-cover-placeholder">' +
          (title.charAt(0).toUpperCase()) + '</div>';

      html += '<div class="bt-search-item" role="option" data-id="' + escapeAttr(bookId) +
        '" data-index="' + idx + '" tabindex="-1">' +
        coverHtml +
        '<div class="bt-search-item-info">' +
        '<div class="bt-search-item-title">' + escapeHtml(title) + '</div>' +
        (author ? '<div class="bt-search-item-author">' + escapeHtml(author) + '</div>' : '') +
        '</div>' +
        '<span class="bt-search-item-badge ' + (avail ? 'bt-badge-avail' : 'bt-badge-out') + '">' +
        (avail ? 'Available' : 'Out') + '</span>' +
        '</div>';
    });

    searchResults.innerHTML = html;

    // Click handlers
    searchResults.querySelectorAll('.bt-search-item').forEach(function (el) {
      el.addEventListener('mousedown', function (e) {
        e.preventDefault();
        const id = el.dataset.id;
        if (id) navigateTo(id);
      });
    });
  }

  function renderEmpty() {
    if (!searchResults) return;
    searchResults.innerHTML =
      '<div class="bt-search-empty" role="status">No books found</div>';
  }

  // ── Open / Close ────────────────────────────────────────────────
  function open() {
    if (!searchContainer) return;
    if (isOpen) return;
    isOpen = true;
    searchContainer.classList.add('bt-search-open');
  }

  function close() {
    if (!searchContainer) return;
    if (!isOpen) return;
    isOpen = false;
    searchContainer.classList.remove('bt-search-open');
    activeIndex = -1;
  }

  // ── Keyboard Navigation ────────────────────────────────────────
  function onKeyDown(e) {
    if (!isOpen) return;

    const items = searchResults.querySelectorAll('.bt-search-item');

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, items.length - 1);
        updateActive(items);
        break;

      case 'ArrowUp':
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, -1);
        updateActive(items);
        break;

      case 'Enter':
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < items.length) {
          const id = items[activeIndex].dataset.id;
          if (id) navigateTo(id);
        } else if (items.length > 0) {
          const id = items[0].dataset.id;
          if (id) navigateTo(id);
        }
        break;
    }
  }

  function updateActive(items) {
    items.forEach(function (el, idx) {
      el.classList.toggle('bt-search-active', idx === activeIndex);
      if (idx === activeIndex) {
        el.setAttribute('aria-selected', 'true');
        el.scrollIntoView({ block: 'nearest' });
      } else {
        el.removeAttribute('aria-selected');
      }
    });
  }

  // ── Navigate to Book ────────────────────────────────────────────
  function navigateTo(bookId) {
    close();
    searchInput.blur();
    window.location.href = '/books/' + encodeURIComponent(bookId);
  }

  // ── Utilities ───────────────────────────────────────────────────
  function escapeHtml(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

  function escapeAttr(str) {
    return String(str).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  // ── Auto-init ───────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
