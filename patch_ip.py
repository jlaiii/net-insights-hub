import re

with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# 1. Add new rows to IP card HTML after Country row
old_ip_rows = '''<div class="row"><span class="label">Country</span><span class="value" id="country">--</span></div>
<div class="row"><span class="label">Timezone</span><span class="value" id="tz">--</span></div>'''
new_ip_rows = '''<div class="row"><span class="label">Country</span><span class="value" id="country">--</span></div>
<div class="row"><span class="label">IP Version</span><span class="value" id="ipVersion">--</span></div>
<div class="row"><span class="label">IP Expanded</span><span class="value ip" id="ipExpanded">--</span></div>
<div class="row"><span class="label">Timezone</span><span class="value" id="tz">--</span></div>'''
content = content.replace(old_ip_rows, new_ip_rows)

# 2. Replace fetchIP function body to include expansion logic
old_fetch = """async function fetchIP() {
  try {
    const res = await fetch('https://ipapi.co/json/');
    const data = await res.json();
    set('ipAddr', data.ip, 'ip');
    set('isp', data.org || data.asn || 'Unknown');
    set('city', data.city || 'Unknown');
    set('region', data.region || 'Unknown');
    set('country', data.country_name ? data.country_name + ' (' + data.country + ')' : data.country);
    set('tz', data.timezone || 'Unknown');
    set('coords', data.latitude ? data.latitude + ', ' + data.longitude : 'Unknown');
    if (data.latitude) {
      $('mapWrap').innerHTML = '<iframe loading="lazy" allowfullscreen src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d30000!2d' + data.longitude + '!3d' + data.latitude + '!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sus!4v1" style="filter:invert(90%) hue-rotate(180deg)"></iframe>';
    }
    if (data.threat && (data.threat.proxy || data.threat.vpn || data.threat.tor)) {
      set('vpnHint', data.threat.vpn ? 'Possible VPN detected' : data.threat.proxy ? 'Proxy detected' : 'Suspicious');
      $('vpnHint').className = 'value warn';
    } else {
      set('vpnHint', 'No proxy/VPN indicators');
      $('vpnHint').className = 'value good';
    }
    if (data.threat && data.threat.tor) { set('torExit', 'Possible Tor exit'); $('torExit').className = 'value warn'; }
    else { set('torExit', 'Not detected'); $('torExit').className = 'value good'; }
  } catch (e) {
    set('ipAddr', 'Unavailable');
    set('isp', 'API error');
  }
}"""

new_fetch = """function expandIPv6(ip) {
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
}
function getIPVersion(ip) {
  if (!ip) return 'Unknown';
  if (ip.indexOf('.') !== -1 && ip.indexOf(':') === -1) return 'IPv4';
  if (ip.indexOf(':') !== -1) return 'IPv6';
  return 'Unknown';
}
function getIPv4FromMapped(ip) {
  const prefix = '::ffff:';
  if (ip && ip.toLowerCase().startsWith(prefix)) {
    return ip.slice(prefix.length);
  }
  return null;
}

async function fetchIP() {
  try {
    const res = await fetch('https://ipapi.co/json/');
    const data = await res.json();
    const ip = data.ip || 'Unavailable';
    set('ipAddr', ip, 'ip');
    set('isp', data.org || data.asn || 'Unknown');
    set('city', data.city || 'Unknown');
    set('region', data.region || 'Unknown');
    set('country', data.country_name ? data.country_name + ' (' + data.country + ')' : data.country);
    set('tz', data.timezone || 'Unknown');
    set('coords', data.latitude ? data.latitude + ', ' + data.longitude : 'Unknown');

    const version = getIPVersion(ip);
    set('ipVersion', version);

    if (version === 'IPv6') {
      const expanded = expandIPv6(ip);
      set('ipExpanded', expanded, 'ip');
      const mapped = getIPv4FromMapped(ip);
      if (mapped) {
        set('ipExpanded', expanded + ' (mapped IPv4: ' + mapped + ')', 'ip');
      }
    } else {
      set('ipExpanded', ip, 'ip');
    }

    if (data.latitude) {
      $('mapWrap').innerHTML = '<iframe loading="lazy" allowfullscreen src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d30000!2d' + data.longitude + '!3d' + data.latitude + '!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sus!4v1" style="filter:invert(90%) hue-rotate(180deg)"></iframe>';
    }
    if (data.threat && (data.threat.proxy || data.threat.vpn || data.threat.tor)) {
      set('vpnHint', data.threat.vpn ? 'Possible VPN detected' : data.threat.proxy ? 'Proxy detected' : 'Suspicious');
      $('vpnHint').className = 'value warn';
    } else {
      set('vpnHint', 'No proxy/VPN indicators');
      $('vpnHint').className = 'value good';
    }
    if (data.threat && data.threat.tor) { set('torExit', 'Possible Tor exit'); $('torExit').className = 'value warn'; }
    else { set('torExit', 'Not detected'); $('torExit').className = 'value good'; }
  } catch (e) {
    set('ipAddr', 'Unavailable');
    set('isp', 'API error');
  }
}"""

content = content.replace(old_fetch, new_fetch)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)

print('patched')
