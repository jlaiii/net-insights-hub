with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# Replace the entire IP API list and normalizers
old_block = '''function normalizeIPWhois(raw) {
  return { ip: raw.ip, org: raw.connection ? raw.connection.org : '', asn: raw.connection ? raw.connection.asn : '', city: raw.city, region: raw.region, country: raw.country_code, country_name: raw.country, timezone: raw.timezone ? raw.timezone.id : '', latitude: raw.latitude, longitude: raw.longitude, threat: null };
}
function normalizeFreeIPAPI(raw) {
  return { ip: raw.ipAddress, org: '', asn: '', city: raw.cityName, region: raw.regionName, country: raw.countryCode, country_name: raw.countryName, timezone: raw.timeZone, latitude: raw.latitude, longitude: raw.longitude, threat: null };
}

const IP_APIS = [
  { name: 'ipapi.co', url: 'https://ipapi.co/json/', normalize: d => d },
  { name: 'ipwho.is', url: 'https://ipwho.is/', normalize: normalizeIPWhois },
  { name: 'freeipapi.com', url: 'https://freeipapi.com/api/json/', normalize: normalizeFreeIPAPI }
];'''

new_block = '''function normalizeGeoJS(raw) {
  return { ip: raw.ip, org: raw.organization || '', asn: '', city: raw.city || '', region: raw.region || '', country: raw.country_code || '', country_name: raw.country || '', timezone: raw.timezone || '', latitude: raw.latitude || 0, longitude: raw.longitude || 0, threat: null };
}
function normalizeIPInfo(raw) {
  const loc = raw.loc ? raw.loc.split(',') : ['0','0'];
  return { ip: raw.ip, org: raw.org || '', asn: '', city: raw.city || '', region: raw.region || '', country: raw.country || '', country_name: '', timezone: raw.timezone || '', latitude: parseFloat(loc[0]) || 0, longitude: parseFloat(loc[1]) || 0, threat: null };
}
function normalizeFreeIPAPI(raw) {
  return { ip: raw.ipAddress, org: raw.asnOrganization || '', asn: raw.asn || '', city: raw.cityName || '', region: raw.regionName || '', country: raw.countryCode || '', country_name: raw.countryName || '', timezone: raw.timeZone || '', latitude: raw.latitude || 0, longitude: raw.longitude || 0, threat: { proxy: raw.isProxy, vpn: false, tor: false } };
}

const IP_APIS = [
  { name: 'geojs.io', url: 'https://get.geojs.io/v1/ip/geo.json', normalize: normalizeGeoJS },
  { name: 'ipinfo.io', url: 'https://ipinfo.io/json', normalize: normalizeIPInfo },
  { name: 'freeipapi.com', url: 'https://freeipapi.com/api/json/', normalize: normalizeFreeIPAPI }
];'''
content = content.replace(old_block, new_block)

# Also update the crossCheckIP to use working APIs
old_cross = '''    // Method 1: Check ipify.org for a second opinion
    try {
      const res = await fetch('https://api.ipify.org?format=json', { cache: 'no-store' });
      const data = await res.json();
      const ipifyIP = data.ip;
      detectedIPSources.push({ source: 'ipify.org', ip: ipifyIP });
      if (ipifyIP !== ipapiIP) {
        reasons.push('IP mismatch: ipify (' + ipifyIP + ') vs ipapi (' + ipapiIP + ')');
        vpnDetected = true;
      }
    } catch(e) {}'''

new_cross = '''    // Method 1: Check ipify.org for a second opinion
    try {
      const res = await fetch('https://api.ipify.org?format=json', { cache: 'no-store' });
      const data = await res.json();
      const ipifyIP = data.ip;
      detectedIPSources.push({ source: 'ipify.org', ip: ipifyIP });
      if (ipifyIP !== ipapiIP) {
        reasons.push('IP mismatch: ipify (' + ipifyIP + ') vs active (' + ipapiIP + ')');
        vpnDetected = true;
      }
    } catch(e) {}'''
content = content.replace(old_cross, new_cross)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)
print('patched')
