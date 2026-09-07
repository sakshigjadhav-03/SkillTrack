// frontend/static/js/i18n.js
// Simple client‑side i18n implementation for SkillTrack
// Supports English (en), Hindi (hi) and Marathi (mr)

const translations = {
  en: {
    "nav.home": "Home",
    "nav.dashboard": "Dashboard",
    "nav.profile": "Profile",
    "nav.logout": "Logout",
    "btn.login": "Login",
    "btn.register": "Register",
    "btn.submit": "Submit",
    "form.email": "Email",
    "form.password": "Password",
    "msg.welcome": "Welcome to SkillTrack",
    "msg.login_success": "Successfully logged in",
    "msg.login_error": "Invalid credentials",
    "footer.copyright": "© 2026 SkillTrack. All rights reserved."
    // Add more keys as needed
  },
  hi: {
    "nav.home": "मुख्य पृष्ठ",
    "nav.dashboard": "डैशबोर्ड",
    "nav.profile": "प्रोफ़ाइल",
    "nav.logout": "लॉगआउट",
    "btn.login": "लॉग इन",
    "btn.register": "रजिस्टर",
    "btn.submit": "जमा करें",
    "form.email": "ईमेल",
    "form.password": "पासवर्ड",
    "msg.welcome": "SkillTrack में आपका स्वागत है",
    "msg.login_success": "सफलतापूर्वक लॉग इन किया गया",
    "msg.login_error": "अमान्य प्रमाण",
    "footer.copyright": "© 2026 SkillTrack. सभी अधिकार सुरक्षित।"
  },
  mr: {
    "nav.home": "मुख्य पृष्ठ",
    "nav.dashboard": "डॅशबोर्ड",
    "nav.profile": "प्रोफाइल",
    "nav.logout": "लॉगआऊट",
    "btn.login": "लॉग इन",
    "btn.register": "नोंदणी",
    "btn.submit": "सबमिट",
    "form.email": "ईमेल",
    "form.password": "पासवर्ड",
    "msg.welcome": "SkillTrack वर आपले स्वागत आहे",
    "msg.login_success": "यशस्वीपणे लॉग इन केले",
    "msg.login_error": "अवैध प्रमाणपत्रे",
    "footer.copyright": "© 2026 SkillTrack. सर्व अधिकार राखीव."
  }
};

function getCurrentLang() {
  return localStorage.getItem('lang') || 'en';
}

function setLang(lang) {
  if (!translations[lang]) return;
  localStorage.setItem('lang', lang);
  document.documentElement.lang = lang;
  // Reload to apply translations across the page
  location.reload();
}

function applyTranslations() {
  const lang = getCurrentLang();
  const dict = translations[lang] || translations['en'];
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      if (el.tagName.toLowerCase() === 'input' && el.placeholder) {
        el.placeholder = dict[key];
      } else if (el.tagName.toLowerCase() === 'option') {
        el.textContent = dict[key];
      } else {
        el.textContent = dict[key];
      }
    }
  });
  const curSpan = document.getElementById('currentLang');
  if (curSpan) {
    const nameMap = { en: 'English', hi: 'हिंदी', mr: 'मराठी' }[lang];
    curSpan.textContent = nameMap || lang;
  }
}

// Event delegation for language selector
document.addEventListener('click', e => {
  if (e.target && e.target.matches('.lang-option')) {
    e.preventDefault();
    const chosen = e.target.getAttribute('data-lang');
    setLang(chosen);
  }
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', applyTranslations);
} else {
  applyTranslations();
}
