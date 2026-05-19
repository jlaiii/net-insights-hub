with open('index.html','r',encoding='utf-8') as f:
    content = f.read()

# 1. Replace Speed Test HTML card
old_speed_html = '''<div class="card" style="grid-column:span 2">
<h2><span class="icon">SP</span> Speed Test</h2>
<p style="color:var(--muted);font-size:0.85rem;margin-bottom:1rem">Measures approximate download speed by fetching a test payload from Cloudflare's edge network.</p>
<div id="speedIdle"><button class="btn" id="startSpeed" onclick="runSpeedTest()">Start Speed Test</button></div>
<div id="speedRunning" class="hidden">
<div class="progress-bar"><div class="fill" id="speedBar"></div></div>
<p style="margin-top:0.5rem;color:var(--muted);font-size:0.85rem">Testing... <span id="speedPhase">preparing</span></p>
</div>
<div id="speedDone" class="hidden" style="margin-top:1rem">
<div class="speed-result" id="speedResult">0 Mbps</div>
<p style="color:var(--muted);font-size:0.78rem">Latency: <span id="latencyResult">--</span> &nbsp;|&nbsp; Test size: <span id="testSize">--</span></p>
<button class="btn" style="margin-top:0.75rem" onclick="runSpeedTest()">Test Again</button>
</div>
</div>'''

new_speed_html = '''<div class="card" style="grid-column:span 2">
<h2><span class="icon">SP</span> Speed Test</h2>
<p style="color:var(--muted);font-size:0.82rem;margin-bottom:1rem">Multi-phase speed analysis: latency sampling, multi-run download averaging, and upload estimation. Results are more reliable than single-payload tests.</p>

<div id="speedIdle"><button class="btn" id="startSpeed" onclick="runSpeedTest()">Start Speed Test</button></div>

<div id="speedRunning" class="hidden">
<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem">
<div class="progress-bar" style="flex:1"><div class="fill" id="speedBar"></div></div>
<span id="speedPct" style="font-size:0.8rem;color:var(--muted);min-width:36px;text-align:right">0%</span>
</div>
<p style="color:var(--muted);font-size:0.85rem;margin-bottom:0.5rem">Phase: <span id="speedPhase" style="color:var(--accent)">initializing</span></p>
<div id="liveMetrics" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:0.5rem;margin-top:0.5rem"></div>
</div>

<div id="speedDone" class="hidden" style="margin-top:1rem">
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1rem">
  <div style="background:rgba(79,193,233,0.06);border:1px solid rgba(79,193,233,0.12);border-radius:0.5rem;padding:1rem;text-align:center">
    <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.04em">Download</div>
    <div class="speed-result" id="dlSpeedResult" style="font-size:1.8rem;margin-top:0.25rem">--</div>
    <div style="font-size:0.72rem;color:var(--muted);margin-top:0.25rem">Avg of <span id="dlRuns">0</span> runs</div>
  </div>
  <div style="background:rgba(79,193,233,0.06);border:1px solid rgba(79,193,233,0.12);border-radius:0.5rem;padding:1rem;text-align:center">
    <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.04em">Upload (est.)</div>
    <div class="speed-result" id="ulSpeedResult" style="font-size:1.8rem;margin-top:0.25rem">--</div>
    <div style="font-size:0.72rem;color:var(--muted);margin-top:0.25rem">Via POST timing</div>
  </div>
  <div style="background:rgba(79,193,233,0.06);border:1px solid rgba(79,193,233,0.12);border-radius:0.5rem;padding:1rem;text-align:center">
    <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.04em">Latency</div>
    <div class="speed-result" id="latResult" style="font-size:1.8rem;margin-top:0.25rem">--</div>
    <div style="font-size:0.72rem;color:var(--muted);margin-top:0.25rem">Jitter: <span id="jitterResult">--</span></div>
  </div>
</div>
<div style="margin-top:1rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0.5rem;font-size:0.78rem;color:var(--muted)">
  <div>Download min: <span id="dlMin">--</span> Mbps</div>
  <div>Download max: <span id="dlMax">--</span> Mbps</div>
  <div>Latency min: <span id="latMin">--</span> ms</div>
  <div>Latency max: <span id="latMax">--</span> ms</div>
  <div>Total data: <span id="totalData">--</span></div>
  <div>Test server: <span id="testServer">Cloudflare / httpbin</span></div>
</div>
<button class="btn" style="margin-top:0.75rem" onclick="runSpeedTest()">Test Again</button>
</div>
</div>'''
content = content.replace(old_speed_html, new_speed_html)

# 2. Replace runSpeedTest JS
old_speed_js = """async function runSpeedTest() {
  $('speedIdle').classList.add('hidden');
  $('speedRunning').classList.remove('hidden');
  $('speedDone').classList.add('hidden');
  $('speedBar').style.width = '0%';
  $('speedPhase').textContent = 'measuring latency';
  const latencyStart = performance.now();
  try { await fetch('https://httpbin.org/get', { cache: 'no-store', mode: 'no-cors' }); } catch(e){}
  const latency = Math.round(performance.now() - latencyStart);
  $('speedPhase').textContent = 'downloading test payload';
  const testUrl = 'https://speed.cloudflare.com/__down?bytes=25000000';
  const startTime = performance.now();
  let lastLoaded = 0;
  try {
    const response = await fetch(testUrl, { cache: 'no-store' });
    const reader = response.body.getReader();
    const contentLength = +(response.headers.get('Content-Length') || 25000000);
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      lastLoaded += value.length;
      const pct = Math.min((lastLoaded / contentLength) * 100, 100);
      $('speedBar').style.width = pct + '%';
    }
    const duration = (performance.now() - startTime) / 1000;
    const bits = lastLoaded * 8;
    const mbps = (bits / duration / 1000000).toFixed(2);
    const mb = (lastLoaded / 1000000).toFixed(1);
    $('speedRunning').classList.add('hidden');
    $('speedDone').classList.remove('hidden');
    $('speedResult').textContent = mbps + ' Mbps';
    $('latencyResult').textContent = latency + ' ms';
    $('testSize').textContent = mb + ' MB';
  } catch (e) {
    $('speedPhase').textContent = 'Test failed. Retrying with smaller payload...';
    try {
      const smallStart = performance.now();
      const smallRes = await fetch('https://speed.cloudflare.com/__down?bytes=5000000', { cache: 'no-store' });
      await smallRes.arrayBuffer();
      const smallDur = (performance.now() - smallStart) / 1000;
      const smallBits = 5000000 * 8;
      const smallMbps = (smallBits / smallDur / 1000000).toFixed(2);
      $('speedRunning').classList.add('hidden');
      $('speedDone').classList.remove('hidden');
      $('speedResult').textContent = smallMbps + ' Mbps';
      $('latencyResult').textContent = latency + ' ms';
      $('testSize').textContent = '5.0 MB (fallback)';
    } catch (e2) {
      $('speedRunning').classList.add('hidden');
      $('speedDone').classList.remove('hidden');
      $('speedResult').textContent = 'Failed';
    }
  }
}"""

new_speed_js = """function setProgress(pct, phase) {
  $('speedBar').style.width = pct + '%';
  $('speedPct').textContent = Math.round(pct) + '%';
  if (phase) $('speedPhase').textContent = phase;
}

async function runSpeedTest() {
  $('speedIdle').classList.add('hidden');
  $('speedRunning').classList.remove('hidden');
  $('speedDone').classList.add('hidden');
  setProgress(0, 'initializing');

  const latencySamples = [];
  const downloadSpeeds = [];
  let totalBytes = 0;

  // Phase 1: Latency sampling (5 pings)
  setProgress(5, 'latency sampling (5 pings)');
  for (let i = 0; i < 5; i++) {
    const s = performance.now();
    try { await fetch('https://httpbin.org/get', { cache: 'no-store', mode: 'no-cors' }); } catch(e){}
    latencySamples.push(performance.now() - s);
    setProgress(5 + (i + 1) * 4, 'latency ping ' + (i + 1) + '/5');
    await new Promise(r => setTimeout(r, 150));
  }

  const latAvg = Math.round(latencySamples.reduce((a,b) => a+b, 0) / latencySamples.length);
  const latMin = Math.round(Math.min(...latencySamples));
  const latMax = Math.round(Math.max(...latencySamples));
  const jitter = Math.round(latencySamples.slice(1).map((v,i) => Math.abs(v - latencySamples[i])).reduce((a,b) => a+b, 0) / (latencySamples.length - 1));

  // Phase 2: Download runs (3 runs, increasing payload sizes)
  const payloads = [5000000, 15000000, 25000000];
  for (let run = 0; run < payloads.length; run++) {
    const bytes = payloads[run];
    setProgress(25 + (run / payloads.length) * 60, 'download run ' + (run + 1) + '/3 (' + (bytes/1000000).toFixed(0) + ' MB)');
    const start = performance.now();
    let loaded = 0;
    try {
      const res = await fetch('https://speed.cloudflare.com/__down?bytes=' + bytes, { cache: 'no-store' });
      const reader = res.body.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        loaded += value.length;
      }
    } catch(e) {
      // Try fallback with smaller
      try {
        const fbRes = await fetch('https://speed.cloudflare.com/__down?bytes=5000000', { cache: 'no-store' });
        await fbRes.arrayBuffer();
        loaded = 5000000;
      } catch(e2) { loaded = 0; }
    }
    const dur = (performance.now() - start) / 1000;
    if (loaded > 0 && dur > 0) {
      const mbps = (loaded * 8) / dur / 1000000;
      downloadSpeeds.push(mbps);
      totalBytes += loaded;
    }
  }

  // Phase 3: Upload estimation
  setProgress(88, 'upload estimation');
  let uploadMbps = 0;
  try {
    const uploadData = new Uint8Array(2 * 1024 * 1024); // 2 MB
    for (let i = 0; i < uploadData.length; i++) uploadData[i] = Math.floor(Math.random() * 256);
    const ulStart = performance.now();
    await fetch('https://httpbin.org/post', { method: 'POST', body: uploadData, cache: 'no-store', mode: 'no-cors' });
    const ulDur = (performance.now() - ulStart) / 1000;
    uploadMbps = ((2 * 1024 * 1024 * 8) / ulDur / 1000000);
  } catch(e) { uploadMbps = 0; }

  setProgress(100, 'complete');

  // Show results
  $('speedRunning').classList.add('hidden');
  $('speedDone').classList.remove('hidden');

  const dlAvg = downloadSpeeds.length > 0 ? (downloadSpeeds.reduce((a,b) => a+b, 0) / downloadSpeeds.length) : 0;
  const dlMinVal = downloadSpeeds.length > 0 ? Math.min(...downloadSpeeds) : 0;
  const dlMaxVal = downloadSpeeds.length > 0 ? Math.max(...downloadSpeeds) : 0;

  $('dlSpeedResult').textContent = dlAvg > 0 ? dlAvg.toFixed(2) + ' Mbps' : 'Failed';
  $('dlRuns').textContent = downloadSpeeds.length;
  $('ulSpeedResult').textContent = uploadMbps > 0 ? uploadMbps.toFixed(2) + ' Mbps' : 'Unavailable';
  $('latResult').textContent = latAvg + ' ms';
  $('jitterResult').textContent = jitter + ' ms';
  $('dlMin').textContent = dlMinVal.toFixed(2);
  $('dlMax').textContent = dlMaxVal.toFixed(2);
  $('latMin').textContent = latMin;
  $('latMax').textContent = latMax;
  $('totalData').textContent = (totalBytes / (1024*1024)).toFixed(1) + ' MB downloaded';
}"""
content = content.replace(old_speed_js, new_speed_js)

with open('index.html','w',encoding='utf-8') as f:
    f.write(content)
print('patched')
