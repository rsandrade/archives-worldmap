(function () {
  'use strict';

  var SUPPORTED = ['en', 'pt-br', 'es', 'zh', 'ro', 'pl'];
  var DEFAULT_LANG = 'en';
  var LANG_BASE_URL = '/static/lang/';

  // ---------------------------------------------------------------------------
  // Detect language: ?lang=xx  >  localStorage  >  browser  >  default
  // ---------------------------------------------------------------------------
  function detectLang() {
    var params = new URLSearchParams(window.location.search);
    var fromUrl = (params.get('lang') || '').toLowerCase();
    if (fromUrl && SUPPORTED.indexOf(fromUrl) !== -1) {
      localStorage.setItem('awm_lang', fromUrl);
      return fromUrl;
    }
    var stored = (localStorage.getItem('awm_lang') || '').toLowerCase();
    if (stored && SUPPORTED.indexOf(stored) !== -1) return stored;

    var nav = (navigator.language || '').toLowerCase();
    for (var i = 0; i < SUPPORTED.length; i++) {
      if (nav === SUPPORTED[i] || nav.indexOf(SUPPORTED[i]) === 0) return SUPPORTED[i];
    }
    if (nav.indexOf('pt') === 0) return 'pt-br';
    if (nav.indexOf('zh') === 0) return 'zh';
    return DEFAULT_LANG;
  }

  // ---------------------------------------------------------------------------
  // Fetch JSON and apply
  // ---------------------------------------------------------------------------
  function applyTranslations(dict) {
    var els = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++) {
      var key = els[i].getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        els[i].textContent = dict[key];
      }
    }
    // HTML translations (for strings containing links)
    var htmlEls = document.querySelectorAll('[data-i18n-html]');
    for (var h = 0; h < htmlEls.length; h++) {
      var hkey = htmlEls[h].getAttribute('data-i18n-html');
      if (dict[hkey] !== undefined) {
        htmlEls[h].innerHTML = dict[hkey];
      }
    }
    // Placeholders
    var placeholders = document.querySelectorAll('[data-i18n-placeholder]');
    for (var j = 0; j < placeholders.length; j++) {
      var pk = placeholders[j].getAttribute('data-i18n-placeholder');
      if (dict[pk] !== undefined) {
        placeholders[j].setAttribute('placeholder', dict[pk]);
      }
    }
    // Title attribute (e.g. confirm dialogs stored in data-i18n-confirm)
    var confirms = document.querySelectorAll('[data-i18n-confirm]');
    for (var c = 0; c < confirms.length; c++) {
      var ck = confirms[c].getAttribute('data-i18n-confirm');
      if (dict[ck] !== undefined) {
        confirms[c].setAttribute('data-confirm', dict[ck]);
      }
    }
    // Update page title if we have site_name
    if (dict['site_name']) {
      var titleEl = document.querySelector('title');
      if (titleEl) {
        var base = titleEl.textContent;
        // Keep "Page - Site" pattern but translate site part
        if (base.indexOf(' - ') !== -1) {
          titleEl.textContent = base.split(' - ')[0] + ' - ' + dict['site_name'];
        }
      }
    }
  }

  function highlightActive(lang) {
    var links = document.querySelectorAll('.lang-selector a');
    for (var i = 0; i < links.length; i++) {
      if (links[i].getAttribute('data-lang') === lang) {
        links[i].classList.add('active-lang');
      } else {
        links[i].classList.remove('active-lang');
      }
    }
  }

  // Preserve existing query params when switching language
  function buildLangUrl(lang) {
    var params = new URLSearchParams(window.location.search);
    params.set('lang', lang);
    return window.location.pathname + '?' + params.toString();
  }

  function initLangLinks() {
    var links = document.querySelectorAll('.lang-selector a[data-lang]');
    for (var i = 0; i < links.length; i++) {
      (function (el) {
        var lang = el.getAttribute('data-lang');
        el.setAttribute('href', buildLangUrl(lang));
        el.addEventListener('click', function (e) {
          e.preventDefault();
          localStorage.setItem('awm_lang', lang);
          // Update URL without full reload
          var newUrl = buildLangUrl(lang);
          window.history.replaceState(null, '', newUrl);
          // Fetch and apply new language
          loadAndApply(lang);
          highlightActive(lang);
        });
      })(links[i]);
    }
  }

  function loadAndApply(lang) {
    var url = LANG_BASE_URL + lang + '.json';
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (dict) { applyTranslations(dict); })
      .catch(function () {
        if (lang !== DEFAULT_LANG) loadAndApply(DEFAULT_LANG);
      });
  }

  // ---------------------------------------------------------------------------
  // Boot
  // ---------------------------------------------------------------------------
  function init() {
    var lang = detectLang();
    initLangLinks();
    highlightActive(lang);
    if (lang !== DEFAULT_LANG) {
      loadAndApply(lang);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
