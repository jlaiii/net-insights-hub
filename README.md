# Net Insights Hub

**Live Site:** [https://jlaiii.github.io/net-insights-hub/](https://jlaiii.github.io/net-insights-hub/)

A professional, privacy-focused network and browser intelligence dashboard. Built entirely in vanilla HTML/CSS/JavaScript with zero frameworks and zero tracking cookies.

## Features

- **IP and Location** -- Real-time public IP, ISP, city, region, country, timezone, coordinates, and embedded map.
- **Global Visit Counter** -- Tracks total page loads via countapi.xyz.
- **Browser Fingerprinting** -- Generates a unique hash from canvas, WebGL, plugins, fonts, and hardware traits without cookies.
- **System and Browser Info** -- Browser name/version, OS, screen resolution, viewport, color depth, touch support, cookies, DNT, PDF viewer.
- **Hardware Details** -- CPU cores, device memory estimate, platform, and full user agent string.
- **Network Stats** -- Online status, connection type, estimated downlink, effective type, RTT, and data-saver mode.
- **Speed Test** -- Approximate download speed using Cloudflare's CDN endpoint with a live progress bar.
- **Battery Status** -- Battery level, charging state, and time remaining (where supported).
- **Privacy Checks** -- Ad-blocker detection, WebRTC local IP leak test, VPN/proxy hints, and Tor exit node detection.
- **Session Analytics** -- Page load time, referrer, local time, session start, click count, and keystroke count.

## Tech Stack

- Pure HTML5 / CSS3 / ES6+ JavaScript
- No build tools, no bundlers, no dependencies
- GitHub Pages for hosting

## APIs Used

- [ipapi.co](https://ipapi.co) -- IP geolocation and threat data
- [countapi.xyz](https://countapi.xyz) -- Visit counting
- [speed.cloudflare.com](https://speed.cloudflare.com) -- Speed test payload

## License

Open source -- feel free to fork and customize.
