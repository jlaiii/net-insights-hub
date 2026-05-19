with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# 1. Make IP Expanded row hidden by default, only show when needed
old_ip_expanded_row = '''<div class="row"><span class="label">IP Expanded</span><span class="value ip" id="ipExpanded">--</span></div>'''
new_ip_expanded_row = '''<div class="row" id="ipExpandedRow" style="display:none"><span class="label">IP Expanded</span><span class="value ip" id="ipExpanded">--</span></div>'''
content = content.replace(old_ip_expanded_row, new_ip_expanded_row)

# 2. Fix expandIPv6 to return null when no expansion needed
old_expand = '''function expandIPv6(ip) {
  if (!ip || ip.indexOf(':') === -1) return ip;
  let groups = ip.split(':');
  let emptyIndex = groups.indexOf('');
  if (emptyIndex !== -1) {
    let zeros = 8 - groups.length + 1;
    let expanded = [];
    for (let i = 0; i < groups.length; i++) {
      if (groups[i] === '' && i === emptyIndex) {
        for (let z = 0; z < zeros; z++) expanded.push('0000');
      } else {
        expanded.push(groups[i].padStart(4, '0'));
      }
    }
    return expanded.join(':');
  }
  return groups.map(g => g.padStart(4, '0')).join(':');
}'''

new_expand = '''function expandIPv6(ip) {
  if (!ip || ip.indexOf(':') === -1) return null;
  let groups = ip.split(':');
  let emptyIndex = groups.indexOf('');
  let needsExp = false;
  if (emptyIndex !== -1) {
    needsExp = true;
    let zeros = 8 - groups.length + 1;
    let expanded = [];
    for (let i = 0; i < groups.length; i++) {
      if (groups[i] === '' && i === emptyIndex) {
        for (let z = 0; z < zeros; z++) expanded.push('0000');
      } else {
        expanded.push(groups[i].padStart(4, '0'));
      }
    }
    return expanded.join(':');
  }
  // Check if any group needs zero-padding
  const padded = groups.map(g => g.padStart(4, '0'));
  const result = padded.join(':');
  if (result !== ip) return result;
  return null; // Already fully expanded
}'''
content = content.replace(old_expand, new_expand)

# 3. Update fetchIP to hide/show expanded row
old_ip_exp_logic = '''    if (version === 'IPv6') {
      const expanded = expandIPv6(ip);
      set('ipExpanded', expanded, 'ip');
      const mapped = getIPv4FromMapped(ip);
      if (mapped) {
        set('ipExpanded', expanded + ' (mapped IPv4: ' + mapped + ')', 'ip');
      }
    } else {
      set('ipExpanded', ip, 'ip');
    }'''

new_ip_exp_logic = '''    if (version === 'IPv6') {
      const expanded = expandIPv6(ip);
      const mapped = getIPv4FromMapped(ip);
      if (expanded) {
        $('ipExpandedRow').style.display = 'flex';
        if (mapped) {
          set('ipExpanded', expanded + ' (mapped IPv4: ' + mapped + ')', 'ip');
        } else {
          set('ipExpanded', expanded, 'ip');
        }
      } else if (mapped) {
        $('ipExpandedRow').style.display = 'flex';
        set('ipExpanded', ip + ' (mapped IPv4: ' + mapped + ')', 'ip');
      } else {
        $('ipExpandedRow').style.display = 'none';
      }
    } else {
      $('ipExpandedRow').style.display = 'none';
      set('ipExpanded', ip, 'ip');
    }'''
content = content.replace(old_ip_exp_logic, new_ip_exp_logic)

# 4. Add CSS for better IP display and a copy button
old_css_end = '''@media(max-width:480px){header h1{font-size:1.7rem}.grid{grid-template-columns:1fr}.link-bar{flex-direction:column;gap:0.25rem}}'''
new_css_end = '''@media(max-width:480px){header h1{font-size:1.7rem}.grid{grid-template-columns:1fr}.link-bar{flex-direction:column;gap:0.25rem}}
.ip-wrap{display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;justify-content:flex-end}
.ip-wrap .value.ip{white-space:nowrap}
.ip-copy{cursor:pointer;background:transparent;border:1px solid rgba(79,193,233,0.25);color:var(--accent);padding:0.15rem 0.4rem;border-radius:0.25rem;font-size:0.7rem;opacity:0.7;transition:opacity .15s}
.ip-copy:hover{opacity:1}'''
content = content.replace(old_css_end, new_css_end)

# 5. Add copy button to IP Address row
old_ip_row = '''<div class="row"><span class="label">IP Address</span><span class="value ip" id="ipAddr">--</span></div>'''
new_ip_row = '''<div class="row"><span class="label">IP Address</span><span class="ip-wrap"><span class="value ip" id="ipAddr">--</span><button class="ip-copy" onclick="copyIP()" title="Copy IP">Copy</button></span></div>'''
content = content.replace(old_ip_row, new_ip_row)

# 6. Add copyIP function to JS (find a good spot - after fetchIP)
old_after_fetchip = '''fetchIP();

function getBrowser() {'''
new_after_fetchip = '''fetchIP();

function copyIP() {
  const ip = $('ipAddr').textContent;
  if (ip && ip !== '--' && ip !== 'Unavailable') {
    navigator.clipboard.writeText(ip).then(() => {
      const btn = document.querySelector('.ip-copy');
      const old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(() => btn.textContent = old, 1200);
    });
  }
}

function getBrowser() {'''
content = content.replace(old_after_fetchip, new_after_fetchip)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)
print('patched')
