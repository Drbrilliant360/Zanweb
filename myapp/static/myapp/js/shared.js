/* ============================================================
   ZANCHANGEMAKERS — SHARED COMPONENTS (shared.js)
   Injects: Navigation, Footer, Chatbot on every page
   Also provides: API helpers for all pages
   ============================================================ */

/* ── API Helpers ── */
const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('zcm_access_token');
}

function getRefreshToken() {
  return localStorage.getItem('zcm_refresh_token');
}

function setTokens(access, refresh) {
  localStorage.setItem('zcm_access_token', access);
  if (refresh) localStorage.setItem('zcm_refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('zcm_access_token');
  localStorage.removeItem('zcm_refresh_token');
}

function isAuthenticated() {
  return !!getToken();
}

async function apiFetch(path, options = {}) {
  const url = API_BASE + path;
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401 && getRefreshToken()) {
    const refresh = getRefreshToken();
    const refreshRes = await fetch(API_BASE + '/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (refreshRes.ok) {
      const data = await refreshRes.json();
      setTokens(data.access, refresh);
      headers['Authorization'] = 'Bearer ' + data.access;
      const retryRes = await fetch(url, { ...options, headers });
      return retryRes;
    }
    clearTokens();
  }
  return res;
}

async function apiGet(path) {
  return apiFetch(path);
}

async function apiPost(path, body) {
  return apiFetch(path, { method: 'POST', body: JSON.stringify(body) });
}

async function apiPatch(path, body) {
  return apiFetch(path, { method: 'PATCH', body: JSON.stringify(body) });
}

async function apiDelete(path) {
  return apiFetch(path, { method: 'DELETE' });
}

async function apiPut(path, body) {
  return apiFetch(path, { method: 'PUT', body: JSON.stringify(body) });
}

(function () {
  'use strict';

  /* ── helpers ── */
  function currentPage() {
    return window.location.pathname.split('/').pop() || 'index.html';
  }

  function isActive(href) {
    return window.location.pathname === href ? 'active' : '';
  }

  // URLs — prefer a data element injected by the layout, fall back to hardcoded paths
  let djangoUrls = {};
  try {
    djangoUrls = JSON.parse(document.getElementById('django-urls-data').textContent);
  } catch (e) {
    // hardcoded fallback paths are defined in each access below
  }

  /* ── NAVIGATION ── */
  function buildNav() {
    const links = [
      { href: djangoUrls.home || '/',           label: 'Home' },
      { href: djangoUrls.about || '/about/',     label: 'About Us' },
      { href: djangoUrls.programs || '/programs/',  label: 'Programs' },
      { href: djangoUrls.volunteer || '/volunteer/', label: 'Volunteer Hub' },
      { href: djangoUrls.gallery || '/gallery/',   label: 'Gallery' },
      { href: djangoUrls.stories || '/stories/',   label: 'Stories' },
      { href: djangoUrls.contact || '/contact/',   label: 'Contact' },
      { href: djangoUrls.register || '/register/',  label: 'Sign Up' },
    ];

    const linksHTML = links.map(l =>
      `<a href="${l.href}" class="${isActive(l.href)}">${l.label}</a>`
    ).join('');

    const mobileLinksHTML = links.map(l =>
      `<a href="${l.href}" class="${isActive(l.href)}">${l.label}</a>`
    ).join('');

    const header = document.createElement('header');
    header.className = 'zcm-header';
    header.innerHTML = `
      <nav class="zcm-nav">
        <a href="${djangoUrls.home || '/'}" class="zcm-logo">
          <img src="/static/myapp/ZANCHANGEMAKERS  LOGO.png" alt="Zanchangemakers Logo">
        </a>
        <div class="zcm-links">
          ${linksHTML}
          <a href="${djangoUrls.login || '/login/'}" class="btn-login ${isActive(djangoUrls.login || '/login/')}">Login</a>
          <a href="${djangoUrls.donate || '/donate/'}" class="btn-donate ${isActive(djangoUrls.donate || '/donate/')}">Donate</a>
        </div>
        <button class="zcm-hamburger" id="zcmHamburger" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
      </nav>
      <div class="zcm-mobile-nav" id="zcmMobileNav">
        ${mobileLinksHTML}
        <a href="${djangoUrls.login || '/login/'}" class="btn-login ${isActive(djangoUrls.login || '/login/')}">Login</a>
        <a href="${djangoUrls.donate || '/donate/'}" class="btn-donate ${isActive(djangoUrls.donate || '/donate/')}">Donate ❤</a>
      </div>
    `;

    // Insert at top of body
    document.body.insertBefore(header, document.body.firstChild);

    // Hamburger toggle
    document.getElementById('zcmHamburger').addEventListener('click', function () {
      document.getElementById('zcmMobileNav').classList.toggle('open');
    });
  }

  /* ── FOOTER ── */
  function buildFooter() {
    const footer = document.createElement('div');
    footer.innerHTML = `
      <div class="zcm-info-bar">
        <div class="ib-inner">
          <div class="ib-item">
            <div class="ib-icon"><i class="fa-solid fa-phone"></i></div>
            <div class="ib-text">
              <span>Call Us</span>
              <p>+255 777 426 972</p>
            </div>
          </div>
          <div class="ib-item">
            <div class="ib-icon"><i class="fa-solid fa-envelope"></i></div>
            <div class="ib-text">
              <span>Email Us</span>
              <p>info@zanchangemakers.co.tz</p>
            </div>
          </div>
          <div class="ib-item">
            <div class="ib-icon"><i class="fa-solid fa-location-dot"></i></div>
            <div class="ib-text">
              <span>Headquarters</span>
              <p>Zanzibar, Tanzania</p>
            </div>
          </div>
        </div>
      </div>

      <footer class="zcm-footer">
        <div class="ft-inner">
          <div class="ft-grid">

            <div class="ft-col">
              <div class="ft-logo">
                <span>Zanchangemakers</span>
              </div>
              <p>Building a leadership-driven volunteer movement to catalyze youth empowerment and community transformation across Tanzania.</p>
              <div class="ft-partner-logos">
                <img src="/static/myapp/ZANCHANGEMAKERS  LOGO.png" alt="Zanchangemakers Logo">
                <img src="/static/myapp/YVF LOGO.png" alt="YVF Logo">
              </div>
            </div>

            <div class="ft-col">
              <h3>Quick Links</h3>
              <ul class="ft-links">
                <li><a href="https://www.ajira.go.tz">Tanzania Ajira Portal</a></li>
                <li><a href="https://www.utumishi.go.tz">Public Service Recruitment Secretariat</a></li>
                <li><a href="https://portal.vijana.go.tz">Vijana Portal</a></li>
                <li><a href="https://www.linkedin.com/jobs">LinkedIn Jobs</a></li>
              </ul>
            </div>

            <div class="ft-col">
              <h3>Follow Us</h3>
              <p>Stay connected and follow our journey of inspiring youth changemakers.</p>
              <div class="ft-socials">
                <a href="https://facebook.com/zanchangemakers" target="_blank" title="Facebook">
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 12.06C22 6.51 17.52 2 12 2S2 6.51 2 12.06c0 5 3.66 9.15 8.44 9.94v-7.03H7.9v-2.91h2.54V9.85c0-2.51 1.49-3.9 3.77-3.9 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.78-1.63 1.58v1.9h2.78l-.45 2.91h-2.33v7.03C18.34 21.21 22 17.06 22 12.06z"/>
                  </svg>
                </a>
                <a href="https://instagram.com/zanchangemakers" target="_blank" title="Instagram">
                  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 2C4.24 2 2 4.24 2 7v10c0 2.76 2.24 5 5 5h10c2.76 0 5-2.24 5-5V7c0-2.76-2.24-5-5-5H7zm10 2c1.66 0 3 1.34 3 3v10c0 1.66-1.34 3-3 3H7c-1.66 0-3-1.34-3-3V7c0-1.66 1.34-3 3-3h10zM12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 2a3 3 0 1 1 0 6 3 3 0 0 1 0-6zm5.5-3.25a1.25 1.25 0 1 0 0 2.5 1.25 1.25 0 0 0 0-2.5z"/>
                  </svg>
                </a>
              </div>
              <div style="margin-top:20px;">
                <a href="${djangoUrls.donate || '/donate/'}" class="btn-donate">Donate Now ❤</a>
              </div>
            </div>

            <div class="ft-col">
              <h3>Newsletter</h3>
              <p>Subscribe to follow our community cohort updates and program schedules.</p>
              <div class="ft-newsletter">
                <input type="email" placeholder="Your email address" id="zcmNewsEmail">
                <button onclick="zcmSubscribe()">Subscribe Now →</button>
              </div>
              <div id="zcmNewsMsg" style="display:none;margin-top:10px;color:#4ade80;font-size:0.8rem;font-weight:600;">
                ✓ Thank you for subscribing!
              </div>
            </div>

          </div>

          <div class="ft-copyright">
            <p>© 2026 <span>Zanchangemakers Initiative</span>. All rights reserved. | Empowering Youth. Inspiring Change. Building Communities.</p>
          </div>
        </div>
      </footer>
    `;

    document.body.appendChild(footer);
  }

  /* ── CHATBOT ── */
  // Notice that templates strings read directly from djangoUrls object here as well
  const BOT_RESPONSES = {
    default: `Thanks for reaching out! 😊 For more help, please <a href="${djangoUrls.contact || '/contact/'}" style='color:#F5C300;text-decoration:underline;'>contact us</a> or call +255 777 426 972.`,
    hello: "Hello! 👋 Welcome to Zanchangemakers! How can I help you today? Ask me about our programs, volunteering, or how to donate.",
    volunteer: `We'd love to have you volunteer! 🌟 Visit our <a href="${djangoUrls.volunteer || '/volunteer/'}" style='color:#F5C300;text-decoration:underline;'>Volunteer Hub</a> to learn more and sign up.`,
    programs: `We run youth leadership, employability, and civic engagement programs. 🎯 See all details on our <a href="${djangoUrls.programs || '/programs/'}" style='color:#F5C300;text-decoration:underline;'>Programs page</a>.`,
    donate: `Your support means the world! ❤️ Visit our <a href="${djangoUrls.donate || '/donate/'}" style='color:#F5C300;text-decoration:underline;'>Donate page</a> to contribute.`,
    contact: `You can reach us at info@zanchangemakers.co.tz or call +255 777 426 972. 📞 Or visit our <a href="${djangoUrls.contact || '/contact/'}" style='color:#F5C300;text-decoration:underline;'>Contact page</a>.`,
    about: `Zanchangemakers was founded in 2021 to empower youth through volunteerism and leadership. Learn more on our <a href="${djangoUrls.about || '/about/'}" style='color:#F5C300;text-decoration:underline;'>About Us page</a>. 🌍`,
    gallery: `Check out our work and events in the <a href="${djangoUrls.gallery || '/gallery/'}" style='color:#F5C300;text-decoration:underline;'>Gallery</a>! 📸`,
    register: `Ready to join us? <a href="${djangoUrls.register || '/register/'}" style='color:#F5C300;text-decoration:underline;'>Register here</a> to become part of the movement! 🚀`,
    stories: `Read inspiring stories from our community on the <a href="${djangoUrls.stories || '/stories/'}" style='color:#F5C300;text-decoration:underline;'>Stories page</a>. ✨`,
  };

  function getBotResponse(msg) {
    const m = msg.toLowerCase();
    if (m.includes('hello') || m.includes('hi') || m.includes('hey')) return BOT_RESPONSES.hello;
    if (m.includes('volunteer')) return BOT_RESPONSES.volunteer;
    if (m.includes('program') || m.includes('training')) return BOT_RESPONSES.programs;
    if (m.includes('donat') || m.includes('support') || m.includes('fund')) return BOT_RESPONSES.donate;
    if (m.includes('contact') || m.includes('phone') || m.includes('email')) return BOT_RESPONSES.contact;
    if (m.includes('about') || m.includes('who') || m.includes('story') || m.includes('founded')) return BOT_RESPONSES.about;
    if (m.includes('gallery') || m.includes('photo') || m.includes('picture')) return BOT_RESPONSES.gallery;
    if (m.includes('register') || m.includes('join') || m.includes('sign up')) return BOT_RESPONSES.register;
    if (m.includes('stories') || m.includes('inspiration')) return BOT_RESPONSES.stories;
    return BOT_RESPONSES.default;
  }

  function buildChatbot() {
    const widget = document.createElement('div');
    widget.innerHTML = `
      <button class="zcm-chat-btn" id="zcmChatBtn" aria-label="Open chat">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
        </svg>
        <span class="zcm-chat-badge">1</span>
      </button>

      <div class="zcm-chatbox" id="zcmChatbox">
        <div class="chat-head">
          <div class="chat-head-avatar">
            <img src="/static/myapp/head logo.png" alt="Zanchangemakers_Logo">
          </div>
          <div class="chat-head-info">
            <h4>Zanchangemakers Support</h4>
            <span>Help support</span>
          </div>
          <button class="chat-close" id="zcmChatClose" aria-label="Close chat">✕</button>
        </div>
        <div class="chat-messages" id="zcmMessages">
          <div class="chat-bubble bot">👋 Hello! Welcome to <strong>Zanchangemakers</strong>. How can I help you today?</div>
        </div>
        <div class="chat-quick-btns">
          <button onclick="zcmQuickMsg('Volunteer')">Volunteer</button>
          <button onclick="zcmQuickMsg('Programs')">Programs</button>
          <button onclick="zcmQuickMsg('Donate')">Donate</button>
          <button onclick="zcmQuickMsg('Contact')">Contact</button>
        </div>
        <div class="chat-input-row">
          <input type="text" id="zcmChatInput" placeholder="Type your message..." onkeydown="if(event.key==='Enter') zcmSendMsg()">
          <button onclick="zcmSendMsg()" aria-label="Send">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(widget);

    document.getElementById('zcmChatBtn').addEventListener('click', function () {
      document.getElementById('zcmChatbox').classList.toggle('open');
      document.querySelector('.zcm-chat-badge').style.display = 'none';
    });

    document.getElementById('zcmChatClose').addEventListener('click', function () {
      document.getElementById('zcmChatbox').classList.remove('open');
    });
  }

  /* ── GLOBAL FUNCTIONS (called from inline HTML) ── */
  window.zcmSendMsg = function () {
    const input = document.getElementById('zcmChatInput');
    const msg = input.value.trim();
    if (!msg) return;
    addChatBubble(msg, 'user');
    input.value = '';
    setTimeout(function () {
      addChatBubble(getBotResponse(msg), 'bot');
    }, 600);
  };

  window.zcmQuickMsg = function (msg) {
    addChatBubble(msg, 'user');
    setTimeout(function () {
      addChatBubble(getBotResponse(msg), 'bot');
    }, 600);
  };

  window.zcmSubscribe = async function () {
    const email = document.getElementById('zcmNewsEmail').value.trim();
    if (!email || !email.includes('@')) {
      alert('Please enter a valid email address.');
      return;
    }
    try {
      const res = await apiPost('/newsletter/', { email });
      if (res.ok) {
        document.getElementById('zcmNewsMsg').style.display = 'block';
        document.getElementById('zcmNewsEmail').value = '';
      } else {
        alert('Subscription failed. Please try again.');
      }
    } catch (e) {
      alert('Network error. Please try again.');
    }
  };

  function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function addChatBubble(msg, type) {
    const messages = document.getElementById('zcmMessages');
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble ' + type;
    bubble.innerHTML = type === 'user' ? escapeHTML(msg) : msg;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  /* ── INIT ── */
  function init() {
    buildNav();
    buildFooter();
    buildChatbot();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

document.addEventListener('DOMContentLoaded', () => {
  const targets = document.querySelectorAll('section, .card, .gallery-item, .hero, .container img');
  targets.forEach(el => el.classList.add('motion-reveal'));
  
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('show'); }
    });
  }, { threshold: 0.12 });
  
  document.querySelectorAll('.motion-reveal').forEach(el => io.observe(el));

  document.querySelectorAll('img').forEach(img => {
    img.addEventListener('mousemove', () => {
      img.style.transform = 'scale(1.04)';
    });
    img.addEventListener('mouseleave', () => {
      img.style.transform = '';
    });
  });
});