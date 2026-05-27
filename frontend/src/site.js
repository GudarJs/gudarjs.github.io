import './site.css';

import hljs from 'highlight.js/lib/core';
import 'highlight.js/styles/github-dark.css';

import python     from 'highlight.js/lib/languages/python';
import javascript from 'highlight.js/lib/languages/javascript';
import bash       from 'highlight.js/lib/languages/bash';
import django     from 'highlight.js/lib/languages/django';
import sql        from 'highlight.js/lib/languages/sql';
import xml        from 'highlight.js/lib/languages/xml';   // covers HTML
import css        from 'highlight.js/lib/languages/css';
import cpp        from 'highlight.js/lib/languages/cpp';
import dart       from 'highlight.js/lib/languages/dart';
import yaml       from 'highlight.js/lib/languages/yaml';
import kotlin     from 'highlight.js/lib/languages/kotlin';
import swift      from 'highlight.js/lib/languages/swift';

hljs.registerLanguage('python',     python);
hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('bash',       bash);
hljs.registerLanguage('django',     django);
hljs.registerLanguage('sql',        sql);
hljs.registerLanguage('html',       xml);
hljs.registerLanguage('css',        css);
hljs.registerLanguage('cpp',        cpp);
hljs.registerLanguage('dart',       dart);
hljs.registerLanguage('yaml',       yaml);
hljs.registerLanguage('kotlin',     kotlin);
hljs.registerLanguage('swift',      swift);

document.addEventListener('DOMContentLoaded', () => {
  hljs.highlightAll();

  // Scroll-aware avatar in the topbar.
  const topbar   = document.querySelector('.topbar');
  const heroPhoto = document.querySelector('.hero-photo, .orbit-profile');
  if (!topbar) return;

  const setAvatar = (show) => topbar.classList.toggle('topbar--avatar', show);

  if (heroPhoto) {
    const io = new IntersectionObserver(
      ([entry]) => setAvatar(!entry.isIntersecting),
      { rootMargin: '-72px 0px 0px 0px', threshold: 0 }
    );
    io.observe(heroPhoto);
    setAvatar(false);
  } else {
    const onScroll = () => setAvatar(window.scrollY > 40);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // cv.html#print auto-opens the print dialog for "Download PDF" CTAs.
  if (location.hash === '#print') {
    setTimeout(() => window.print(), 500);
  }
});
