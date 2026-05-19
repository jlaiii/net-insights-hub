with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# 1. Add new rows to IP card: Data Source, Data Age, API Status
old_ip_card_end = '''<div class="row"><span class="label">Coordinates</span><span class="value" id="coords">--</span></div>
<div class="map-wrap" id="mapWrap">Map loading...</div>
</div>'''
new_ip_card_end = '''<div class="row"><span class="label">Coordinates</span><span class="value" id="coords">--</span></div>
<div class="row"><span class="label">Data Source</span><span class="value" id="dataSource">--</span></div>
<div class="row"><span class="label">Data Age</span><span class="value" id="dataAge">--</span></div>
<div class="row"><span class="label">API Status</span><span class="value" id="apiStatus">Initializing...</span></div>
<div class="map-wrap" id="mapWrap">Map loading...</div>
</div>'''
content = content.replace(old_ip_card_end, new_ip_card_end)

# 2. Find and replace the entire fetchIP + renderIP + helper section
old_js_block = '''async function fetchWithTimeout(url, opts, ms) {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), ms);
  try {
    const res = await fetch(url, { ...opts, signal: ctrl.signal });
    clearTimeout(id);
    return res;
  } catch(e) {
    clearTimeout(id);
    throw e;
  }
}

function normalizeIPWhois(raw) {
  return {
    ip: raw.ip,
    org: raw.connection ? raw.connection.org : '',
    asn: raw.connection ? raw.connection.asn : '',
    city: raw.city,
    region: raw.region,
    country: raw.country_code,
    country_name: raw.country,
    timezone: raw.timezone ? raw.timezone.id : '',
    latitude: raw.latitude,
    longitude: raw.longitude,
    threat: null
  };
}

function normalizeFreeIPAPI(raw) {
  return {
    ip: raw.ipAddress,
    org: '',
    asn: '',
    city: raw.cityName,
    region: raw.regionName,
    country: raw.countryCode,
    country_name: raw.countryName,
    timezone: raw.timeZone,
    latitude: raw.latitude,
    longitude: raw.longitude,
    threat: null
  };
}

const IP_APIS = [
  {
    name: 'ipapi.co',
    url: 'https://ipapi.co/json/',
    normalize: d => d
  },
  {
    name: 'ipwho.is',
    url: 'https://ipwho.is/',
    normalize: normalizeIPWhois
  },
  {
    name: 'freeipapi.com',
    url: 'https://freeipapi.com/api/json/',
    normalize: normalizeFreeIPAPI
  }
];

async function fetchIP() {
  // Check session cache first
  try {
    const cached = sessionStorage.getItem('nih_ipcache');
    if (cached) {
      const data = JSON.parse(cached);
      const age = Date.now() - data.ts;
      if (age < 300000) { // 5 min cache
        renderIP(data);
        return;
      }
    }
  } catch(e) {}

  let lastError = '';
  for (let i = 0; i < IP_APIS.length; i++) {
    const api = IP_APIS[i];
    try {
      set('ipAddr', 'Trying ' + api.name + '...');
      const res = await fetchWithTimeout(api.url, { cache: 'no-store' }, 6000);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const raw = await res.json();
      const data = api.normalize(raw);
      if (!data.ip) throw new Error('No IP in response');

      // Cache success
      try { sessionStorage.setItem('nih_ipcache', JSON.stringify({ ...data, ts: Date.now() })); } catch(e) {}

      renderIP(data);
      return;
    } catch (e) {
      lastError = e.message || String(e);
      set('ipAddr', api.name + ' failed, retrying...');
      await new Promise(r => setTimeout(r, 400));
    }
  }

  // All failed
  set('ipAddr', 'Unavailable');
  set('isp', 'All APIs failed: ' + lastError);
}

function renderIP(data) {
  const ip = data.ip || 'Unavailable';
  detectedPublicIP = ip;
  detectedIPSources.push({ source: 'active', ip: ip });
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

  crossCheckIP(ip, data.timezone);
}
fetchIP();'''

new_js_block = '''async function fetchWithTimeout(url, opts, ms) {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), ms);
  try {
    const res = await fetch(url, { ...opts, signal: ctrl.signal });
    clearTimeout(id);
    return res;
  } catch(e) {
    clearTimeout(id);
    throw e;
  }
}

function timeAgo(ts) {
  const s = Math.floor((Date.now() - ts) / 1000);
  if (s < 10) return 'just now';
  if (s < 60) return s + ' sec ago';
  const m = Math.floor(s / 60);
  if (m < 60) return m + ' min ago';
  const h = Math.floor(m / 60);
  return h + ' hour' + (h > 1 ? 's' : '') + ' ago';
}

function normalizeIPWhois(raw) {
  return { ip: raw.ip, org: raw.connection ? raw.connection.org : '', asn: raw.connection ? raw.connection.asn : '', city: raw.city, region: raw.region, country: raw.country_code, country_name: raw.country, timezone: raw.timezone ? raw.timezone.id : '', latitude: raw.latitude, longitude: raw.longitude, threat: null };
}
function normalizeFreeIPAPI(raw) {
  return { ip: raw.ipAddress, org: '', asn: '', city: raw.cityName, region: raw.regionName, country: raw.countryCode, country_name: raw.countryName, timezone: raw.timeZone, latitude: raw.latitude, longitude: raw.longitude, threat: null };
}

const IP_APIS = [
  { name: 'ipapi.co', url: 'https://ipapi.co/json/', normalize: d => d },
  { name: 'ipwho.is', url: 'https://ipwho.is/', normalize: normalizeIPWhois },
  { name: 'freeipapi.com', url: 'https://freeipapi.com/api/json/', normalize: normalizeFreeIPAPI }
];

let currentIPData = null;

async function fetchIP() {
  set('apiStatus', 'Checking current IP...');

  // Step 1: Always check current IP via ipify (fast, no rate limits)
  let currentIP = null;
  try {
    const res = await fetchWithTimeout('https://api.ipify.org?format=json', { cache: 'no-store' }, 4000);
    const d = await res.json();
    currentIP = d.ip;
  } catch(e) { /* ipify failed, try next */ }

  if (!currentIP) {
    try {
      const res = await fetchWithTimeout('https://checkip.amazonaws.com/', { cache: 'no-store' }, 4000);
      currentIP = (await res.text()).trim();
    } catch(e) { /* amazon failed too */ }
  }

  // Step 2: Check if we have cached data for this exact IP
  let useCache = false;
  let cachedData = null;
  try {
    const raw = sessionStorage.getItem('nih_ipcache');
    if (raw) {
      cachedData = JSON.parse(raw);
      if (cachedData.ip === currentIP) {
        useCache = true;
        set('apiStatus', 'Using cached location for IP ' + currentIP);
      }
    }
  } catch(e) {}

  if (useCache && cachedData) {
    renderIP(cachedData, true);
    startAgeTimer(cachedData.ts);
    return;
  }

  // Step 3: IP changed or no cache - fetch fresh location data
  set('apiStatus', 'IP changed or no cache. Fetching location...');
  const statusParts = [];
  let lastError = '';

  for (let i = 0; i < IP_APIS.length; i++) {
    const api = IP_APIS[i];
    try {
      set('apiStatus', 'Trying ' + api.name + '...');
      statusParts.push(api.name + ': trying');
      const res = await fetchWithTimeout(api.url, { cache: 'no-store' }, 6000);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const raw = await res.json();
      const data = api.normalize(raw);
      if (!data.ip) throw new Error('No IP in response');

      // Success - build status string
      const finalStatus = IP_APIS.map((a, idx) => {
        if (idx === i) return a.name + ': OK';
        if (idx < i) return a.name + ': failed';
        return a.name + ': skipped';
      }).join(' | ');
      set('apiStatus', finalStatus);

      // Cache with timestamp
      data._source = api.name;
      data.ts = Date.now();
      try { sessionStorage.setItem('nih_ipcache', JSON.stringify(data)); } catch(e) {}
      currentIPData = data;
      renderIP(data, false);
      startAgeTimer(data.ts);
      return;
    } catch (e) {
      lastError = e.message || String(e);
      statusParts.push(api.name + ': failed (' + lastError + ')');
      set('apiStatus', statusParts.join(' | '));
      if (i < IP_APIS.length - 1) await new Promise(r => setTimeout(r, 300));
    }
  }

  // All failed
  set('apiStatus', 'All APIs failed. Last: ' + lastError);
  set('ipAddr', currentIP || 'Unavailable');
  set('isp', 'All location APIs failed');
  set('dataSource', 'None');
  set('dataAge', 'Never');
}

function startAgeTimer(ts) {
  function tick() {
    if (!currentIPData || currentIPData.ts !== ts) return;
    set('dataAge', timeAgo(ts));
    setTimeout(tick, 10000);
  }
  tick();
}

function renderIP(data, fromCache) {
  const ip = data.ip || 'Unavailable';
  detectedPublicIP = ip;
  detectedIPSources.push({ source: 'active', ip: ip });
  set('ipAddr', ip, 'ip');
  set('isp', data.org || data.asn || 'Unknown');
  set('city', data.city || 'Unknown');
  set('region', data.region || 'Unknown');
  set('country', data.country_name ? data.country_name + ' (' + data.country + ')' : data.country);
  set('tz', data.timezone || 'Unknown');
  set('coords', data.latitude ? data.latitude + ', ' + data.longitude : 'Unknown');
  set('dataSource', data._source || 'Unknown' + (fromCache ? ' (cached)' : ''));
  set('dataAge', timeAgo(data.ts || Date.now()));

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

  crossCheckIP(ip, data.timezone);
}
fetchIP();'''
content = content.replace(old_js_block, new_js_block)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)
print('patched')
