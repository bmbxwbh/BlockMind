/**
 * BlockMind — Miuix Console 本地版
 * 只加载需要的组件，不依赖 CDN
 */
(function() {
  'use strict';
  const BASE = '/static/';

  // 加载 CSS
  const cssFiles = [
    'css/tokens.css',
    'css/base.css',
    'css/animations.css',
    'css/layout.css',
    'css/navigation.css',
    'css/button.css',
    'css/card.css',
    'css/stat.css',
    'css/input.css',
    'css/table.css',
    'css/modal.css',
    'css/toast.css',
    'css/select.css',
    'css/tabs.css',
    'css/tag.css',
    'css/badge.css',
    'css/progress.css',
  ];
  cssFiles.forEach(f => {
    if (document.querySelector(`link[href="${BASE}${f}"]`)) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = BASE + f;
    document.head.appendChild(link);
  });

  // 加载工具 JS
  const utils = [
    'utils/theme.js',
    'utils/ripple.js',
    'utils/modal.js',
    'utils/toast.js',
  ];

  let loaded = 0;
  utils.forEach(f => {
    const script = document.createElement('script');
    script.src = BASE + f;
    script.onload = () => {
      loaded++;
      if (loaded === utils.length) {
        if (typeof MxTheme !== 'undefined') MxTheme.init();
        if (typeof MxRipple !== 'undefined') MxRipple.init();
        window.dispatchEvent(new CustomEvent('mx-ready'));
        console.log('%c✦ BlockMind UI loaded', 'color:#4C8BF5;font-weight:bold');
      }
    };
    document.head.appendChild(script);
  });
})();
