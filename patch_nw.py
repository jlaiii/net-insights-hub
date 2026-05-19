import re

with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# Replace Network card HTML
old_nw = '''<div class="card">
<h2><span class="icon">NW</span> Network</h2>
<div class="row"><span class="label">Online Status</span><span class="value" id="online"><span class="status-dot online"></span>Online</span></div>
<div class="row"><span class="label">Connection Type</span><span class="value" id="connType">--</span></div>
<div class="row"><span class="label">Downlink (est.)</span><span class="value" id="downlink">--</span></div>
<div class="row"><span class="label">Effective Type</span><span class="value" id="effType">--</span></div>
<div class="row"><span class="label">RTT</span><span class="value" id="rtt">--</span></div>
<div class="row"><span class="label">Save Data</span><span class="value" id="saveData">--</span></div>
</div>'''

new_nw = '''<div class="card">
<h2><span class="icon">NW</span> Network</h2>
<div class="row"><span class="label">Online Status</span><span class="value" id="online"><span class="status-dot online"></span>Online</span></div>
<div class="row"><span class="label">Connection Type</span><span class="value" id="connType">--</span></div>
<div class="row"><span class="label">Downlink (est.)</span><span class="value" id="downlink">--</span></div>
<div class="row"><span class="label">Effective Type</span><span class="value" id="effType">--</span></div>
<div class="row"><span class="label">RTT</span><span class="value" id="rtt">--</span></div>
<div class="row"><span class="label">Save Data</span><span class="value" id="saveData">--</span></div>
<div class="row"><span class="label">Latency (measured)</span><span class="value" id="measuredLatency">--</span></div>
<div class="row"><span class="label">Download Speed (est.)</span><span class="value" id="navSpeed">--</span></div>
<div style="margin-top:0.75rem"><button class="btn" onclick="runNetworkDiagnostics()">Run Network Diagnostics</button></div>
</div>'''
content = content.replace(old_nw, new_nw)

# Replace updateNetwork JS function
old_js = '''function updateNetwork() {
  const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  if (conn) {
    set('connType', conn.type || 'Unknown');
    set('downlink', conn.downlink ? '~' + conn.downlink + ' Mbps' : 'Unknown');
    set('effType', conn.effectiveType || 'Unknown');
    set('rtt', conn.rtt ? conn.rtt + ' ms' : 'Unknown');
    set('saveData', conn.saveData ? 'On' : 'Off');
  } else {
    set('connType', 'Not supported');
  }
}
updateNetwork();
if (navigator.connection) navigator.connection.addEventListener('change', updateNetwork);
window.addEventListener('online', () => { set('online', 'Online'); $('online').querySelector('.status-dot').className = 'status-dot online'; });
window.addEventListener('offline', () => { set('online', 'Offline'); $('online').querySelector('.status-dot').className = 'status-dot offline'; });'''

new_js = '''function updateNetwork() {
  const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  if (conn) {
    set('connType', conn.type || 'Unknown');
    set('downlink', conn.downlink ? '~' + conn.downlink + ' Mbps' : 'Unknown');
    set('effType', conn.effectiveType || 'Unknown');
    set('rtt', conn.rtt ? conn.rtt + ' ms' : 'Unknown');
    set('saveData', conn.saveData ? 'On' : 'Off');
  } else {
    set('connType', 'API not supported');
    set('downlink', 'API not supported');
    set('effType', 'API not supported');
    set('rtt', 'API not supported');
    set('saveData', 'API not supported');
  }
}
updateNetwork();
if (navigator.connection) navigator.connection.addEventListener('change', updateNetwork);
window.addEventListener('online', () => { set('online', 'Online'); $('online').querySelector('.status-dot').className = 'status-dot online'; });
window.addEventListener('offline', () => { set('online', 'Offline'); $('online').querySelector('.status-dot').className = 'status-dot offline'; });

async function runNetworkDiagnostics() {
  set('measuredLatency', 'Testing...');
  set('navSpeed', 'Testing...');

  // Measure latency via fetch to a reliable endpoint
  const latencyTimes = [];
  for (let i = 0; i < 3; i++) {
    const start = performance.now();
    try {
      await fetch('https://httpbin.org/get', { cache: 'no-store', mode: 'no-cors' });
    } catch(e) {}
    latencyTimes.push(performance.now() - start);
    await new Promise(r => setTimeout(r, 200));
  }
  const avgLat = Math.round(latencyTimes.reduce((a,b) => a+b, 0) / latencyTimes.length);
  set('measuredLatency', avgLat + ' ms');

  // Estimate from navigation timing if available
  try {
    const nav = performance.getEntriesByType('navigation')[0];
    if (nav) {
      const dur = nav.responseEnd - nav.startTime;
      const size = nav.transferSize || 0;
      if (size > 0 && dur > 0) {
        const kbps = (size * 8) / (dur / 1000) / 1024;
        set('navSpeed', '~' + kbps.toFixed(1) + ' kbps (page load est.)');
      } else {
        set('navSpeed', 'Unable to estimate');
      }
    } else if (performance.timing) {
      const t = performance.timing;
      const dur = t.responseEnd - t.navigationStart;
      const size = document.documentElement.outerHTML.length;
      if (dur > 0) {
        const kbps = (size * 8) / (dur / 1000) / 1024;
        set('navSpeed', '~' + kbps.toFixed(1) + ' kbps (page load est.)');
      }
    } else {
      set('navSpeed', 'Unable to estimate');
    }
  } catch(e) {
    set('navSpeed', 'Unable to estimate');
  }
}'''
content = content.replace(old_js, new_js)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)
print('patched')
