import re

with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# 1. Update Privacy Checks card HTML - add Detected IPs row
old_privacy = '''<div class="card">
<h2><span class="icon">PR</span> Privacy Checks</h2>
<div class="row"><span class="label">Ad Blocker</span><span class="value" id="adblock">--</span></div>
<div class="row"><span class="label">WebRTC Leak</span><span class="value" id="webrtcLeak">--</span></div>
<div class="row"><span class="label">VPN / Proxy hint</span><span class="value" id="vpnHint">--</span></div>
<div class="row"><span class="label">Tor Exit Node</span><span class="value" id="torExit">--</span></div>
</div>'''

new_privacy = '''<div class="card">
<h2><span class="icon">PR</span> Privacy Checks</h2>
<div class="row"><span class="label">Ad Blocker</span><span class="value" id="adblock">--</span></div>
<div class="row"><span class="label">WebRTC Leak</span><span class="value" id="webrtcLeak">--</span></div>
<div class="row"><span class="label">Detected Public IPs</span><span class="value ip" id="detectedIPs">--</span></div>
<div class="row"><span class="label">VPN / Proxy hint</span><span class="value" id="vpnHint">Checking...</span></div>
<div class="row"><span class="label">Tor Exit Node</span><span class="value" id="torExit">--</span></div>
<div style="margin-top:0.75rem"><button class="btn" onclick="runPrivacyScan()">Re-run Privacy Scan</button></div>
</div>'''
content = content.replace(old_privacy, new_privacy)

# 2. Replace fetchIP to include cross-check and store the IP globally
old_fetchip = """async function fetchIP() {
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

new_fetchip = """let detectedPublicIP = null;
let detectedIPSources = [];

async function fetchIP() {
  try {
    const res = await fetch('https://ipapi.co/json/');
    const data = await res.json();
    const ip = data.ip || 'Unavailable';
    detectedPublicIP = ip;
    detectedIPSources.push({ source: 'ipapi.co', ip: ip });
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
    if (data.threat && data.threat.tor) { set('torExit', 'Possible Tor exit'); $('torExit').className = 'value warn'; }
    else { set('torExit', 'Not detected'); $('torExit').className = 'value good'; }

    // Start cross-checks after we have the base IP
    crossCheckIP(ip, data.timezone);
  } catch (e) {
    set('ipAddr', 'Unavailable');
    set('isp', 'API error');
  }
}"""
content = content.replace(old_fetchip, new_fetchip)

# 3. Add new VPN detection functions before getBrowser()
old_before_browser = """function getBrowser() {
  const ua = navigator.userAgent;"""

new_before_browser = """function isPrivateIP(ip) {
  if (!ip) return false;
  if (ip.startsWith('192.168.') || ip.startsWith('10.') || ip.startsWith('172.')) {
    const parts = ip.split('.');
    if (parts.length === 4) {
      const second = parseInt(parts[1], 10);
      if (ip.startsWith('172.') && (second >= 16 && second <= 31)) return true;
    }
    if (ip.startsWith('192.168.') || ip.startsWith('10.')) return true;
  }
  if (ip === '127.0.0.1' || ip === '::1' || ip === '0:0:0:0:0:0:0:1') return true;
  if (ip.startsWith('fc') || ip.startsWith('fd')) return true;
  return false;
}

async function crossCheckIP(ipapiIP, ipapiTZ) {
  const reasons = [];
  let vpnDetected = false;

  // Method 1: Check ipify.org for a second opinion
  try {
    const res = await fetch('https://api.ipify.org?format=json', { cache: 'no-store' });
    const data = await res.json();
    const ipifyIP = data.ip;
    detectedIPSources.push({ source: 'ipify.org', ip: ipifyIP });
    if (ipifyIP !== ipapiIP) {
      reasons.push('IP mismatch: ipify (' + ipifyIP + ') vs ipapi (' + ipapiIP + ')');
      vpnDetected = true;
    }
  } catch(e) {}

  // Method 2: Timezone mismatch
  try {
    const browserTZ = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (ipapiTZ && browserTZ && ipapiTZ !== browserTZ) {
      reasons.push('Timezone mismatch: browser (' + browserTZ + ') vs IP (' + ipapiTZ + ')');
      vpnDetected = true;
    }
  } catch(e) {}

  // Method 3: Wait for WebRTC results then compare
  setTimeout(() => {
    const webrtcIPs = (window.__webrtcPublicIPs || []).filter(ip => !isPrivateIP(ip));
    if (webrtcIPs.length > 0) {
      detectedIPSources.push(...webrtcIPs.map(ip => ({ source: 'WebRTC', ip: ip })));
      const unmatched = webrtcIPs.filter(ip => ip !== ipapiIP);
      if (unmatched.length > 0) {
        reasons.push('WebRTC exposes different public IP: ' + unmatched.join(', '));
        vpnDetected = true;
      }
    }
    updateDetectedIPs();
    updateVPNHint(vpnDetected, reasons);
  }, 2500);
}

function updateDetectedIPs() {
  const unique = [];
  const seen = new Set();
  for (const src of detectedIPSources) {
    if (!seen.has(src.ip)) {
      seen.add(src.ip);
      unique.push(src.ip);
    }
  }
  if (unique.length > 0) {
    set('detectedIPs', unique.join(', '));
  } else {
    set('detectedIPs', 'None detected');
  }
}

function updateVPNHint(detected, reasons) {
  if (detected) {
    const msg = reasons.length > 0 ? 'Possible VPN/Proxy (' + reasons.length + ')' : 'Possible VPN/Proxy';
    set('vpnHint', msg);
    $('vpnHint').className = 'value warn';
    $('vpnHint').title = reasons.join('; ');
  } else {
    set('vpnHint', 'No proxy/VPN indicators');
    $('vpnHint').className = 'value good';
    $('vpnHint').title = '';
  }
}

function runPrivacyScan() {
  set('vpnHint', 'Checking...');
  $('vpnHint').className = 'value';
  detectedIPSources = [];
  detectedPublicIP = null;
  checkWebRTC();
  fetchIP();
}

function getBrowser() {
  const ua = navigator.userAgent;"""
content = content.replace(old_before_browser, new_before_browser)

# 4. Replace checkWebRTC to also capture public IPs
old_webrtc = """async function checkWebRTC() {
  try {
    const pc = new RTCPeerConnection({ iceServers: [] });
    pc.createDataChannel('');
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    setTimeout(() => {
      const lines = (pc.localDescription ? pc.localDescription.sdp : '').split('\\n');
      const ips = lines.filter(l => l.includes('candidate')).map(l => {
        const m = l.match(/([0-9]{1,3}\.){3}[0-9]{1,3}/);
        return m ? m[0] : null;
      }).filter(Boolean);
      const hasLocal = ips.some(ip => ip.startsWith('192.') || ip.startsWith('10.') || ip.startsWith('172.'));
      set('webrtcLeak', hasLocal ? 'Local IP exposed (' + ips.length + ')' : 'No local leak');
      if (hasLocal) $('webrtcLeak').className = 'value warn'; else $('webrtcLeak').className = 'value good';
    }, 1000);
  } catch(e) { set('webrtcLeak', 'Check failed'); }
}
checkWebRTC();"""

new_webrtc = """async function checkWebRTC() {
  try {
    const pc = new RTCPeerConnection({ iceServers: [] });
    pc.createDataChannel('');
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    setTimeout(() => {
      const lines = (pc.localDescription ? pc.localDescription.sdp : '').split('\\n');
      const allIPs = [];
      const candidateLines = lines.filter(l => l.includes('candidate'));
      for (const line of candidateLines) {
        // Try IPv4
        const ipv4m = line.match(/([0-9]{1,3}\.){3}[0-9]{1,3}/);
        if (ipv4m) allIPs.push(ipv4m[0]);
        // Try IPv6 in candidate
        const ipv6m = line.match(/([0-9a-fA-F]{1,4}:){2,}[0-9a-fA-F]{1,4}/);
        if (ipv6m) allIPs.push(ipv6m[0]);
      }
      window.__webrtcPublicIPs = allIPs.filter(ip => !isPrivateIP(ip));
      const hasLocal = allIPs.some(ip => isPrivateIP(ip));
      set('webrtcLeak', hasLocal ? 'Local IP exposed' : 'No local leak');
      if (hasLocal) $('webrtcLeak').className = 'value warn'; else $('webrtcLeak').className = 'value good';
    }, 1000);
  } catch(e) { set('webrtcLeak', 'Check failed'); }
}
checkWebRTC();"""
content = content.replace(old_webrtc, new_webrtc)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)
print('patched')
