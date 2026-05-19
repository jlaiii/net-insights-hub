import re

with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# 1. Replace visitCounter HTML block
old_html = '<div class="meta" id="visitCounter"><span class="loader"></span> Loading visits...</div>'
new_html = '''<div class="meta" id="visitCounter" style="cursor:pointer;position:relative" onclick="toggleVisitTip()">
  <span id="visitCountText">Loading visits...</span>
  <div id="visitTip" class="visit-tip">This count is stored locally in your browser using localStorage. It tracks how many times you have visited this page on this device.</div>
</div>'''
content = content.replace(old_html, new_html)

# 2. Replace fetchVisits JS function
old_js = """async function fetchVisits() {
  try {
    const ns = 'net-insights-hub'; const key = 'visits';
    await fetch('https://api.countapi.xyz/hit/' + ns + '/' + key);
    const res = await fetch('https://api.countapi.xyz/get/' + ns + '/' + key);
    const data = await res.json();
    $('visitCounter').innerHTML = 'Visits: ' + (data.value || 0).toLocaleString();
  } catch(e) {
    $('visitCounter').innerHTML = 'Visit counter unavailable';
  }
}
fetchVisits();"""

new_js = """function getStoredVisits() {
  try {
    const raw = localStorage.getItem('nih_visits');
    return raw ? parseInt(raw, 10) : 0;
  } catch(e) { return 0; }
}
function incrementVisits() {
  try {
    const count = getStoredVisits() + 1;
    localStorage.setItem('nih_visits', count.toString());
    return count;
  } catch(e) { return 1; }
}
function showVisitCount() {
  const count = incrementVisits();
  $('visitCountText').textContent = 'Visits: ' + count.toLocaleString();
}
function toggleVisitTip() {
  const tip = $('visitTip');
  tip.classList.toggle('show');
}
showVisitCount();"""

content = content.replace(old_js, new_js)

# 3. Add tooltip CSS before closing </style>
old_css = "@media(max-width:480px){header h1{font-size:1.7rem}.grid{grid-template-columns:1fr}.link-bar{flex-direction:column;gap:0.25rem}}"
new_css = """@media(max-width:480px){header h1{font-size:1.7rem}.grid{grid-template-columns:1fr}.link-bar{flex-direction:column;gap:0.25rem}}
.visit-tip{position:absolute;top:120%;left:50%;transform:translateX(-50%);width:260px;background:var(--surface);border:1px solid var(--border);border-radius:0.5rem;padding:0.75rem;font-size:0.8rem;color:var(--muted);box-shadow:0 8px 24px rgba(0,0,0,0.3);opacity:0;pointer-events:none;transition:opacity .2s;z-index:100;text-align:center}
.visit-tip.show{opacity:1;pointer-events:auto}
#visitCounter:hover .visit-tip{opacity:1;pointer-events:auto}
.visit-tip::before{content:'';position:absolute;bottom:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-bottom-color:var(--border)}"""
content = content.replace(old_css, new_css)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)

print('patched')
