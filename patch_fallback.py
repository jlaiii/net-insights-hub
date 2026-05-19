with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# Replace fetchIP with smart fallback version
old_fetch = '''async function fetchIP() {
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
}
fetchIP();'''

new_fetch = '''async function fetchWithTimeout(url, opts, ms) {
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

content = content.replace(old_fetch, new_fetch)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)
print('patched')
