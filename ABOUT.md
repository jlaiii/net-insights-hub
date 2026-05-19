# About Net Insights Hub

## Purpose

Net Insights Hub was built to give users a clear, visual window into the data their browser and network connection expose to every website they visit. Most people are unaware how much information is available -- from exact location and ISP to a unique browser fingerprint. This project makes that invisible data visible in a clean, professional interface.

## How It Works

Everything runs client-side in the browser. When you load the page:

1. **IP Lookup** -- The browser calls `ipapi.co/json/` to fetch your public IP and geolocation.
2. **Fingerprinting** -- JavaScript gathers canvas data, WebGL vendor/renderer, installed plugins, fonts, screen resolution, timezone, and hardware specs to create a hash. This hash can often uniquely identify your browser even without cookies.
3. **Network Info** -- The Navigator API exposes connection type, downlink estimate, and RTT.
4. **Speed Test** -- A known-size payload is downloaded from Cloudflare's edge network. The time taken is used to calculate approximate Mbps.
5. **Privacy Checks** -- A bait element tests for ad blockers. WebRTC is probed for local IP leaks.
6. **Visit Counter** -- `countapi.xyz` increments and returns a global hit count for this namespace.

## Privacy

- No cookies are set or read.
- No analytics scripts (Google, Meta, etc.) are loaded.
- All fingerprinting is done in real-time on your device.
- The only third-party requests are to ipapi.co, countapi.xyz, and Cloudflare for the speed test.

## Browser Support

Works best in modern Chromium, Firefox, Safari, and Edge. Some APIs (battery, connection info) may be restricted or unavailable depending on your browser and privacy settings.

## Future Ideas

- Upload speed test
- Latency/jitter test (ping to multiple endpoints)
- Dark/light theme toggle
- Export report as JSON or PDF
- Historical visit graphs

---

Built by [jlaiii](https://github.com/jlaiii) with curiosity and caffeine.
