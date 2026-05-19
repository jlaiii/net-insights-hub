with open('index.html','r',encoding='utf-16') as f:
    lines = f.readlines()

insert_html = """  <div style="margin-top:0.75rem;position:relative;z-index:1">
    <a href="https://github.com/jlaiii/net-insights-hub" target="_blank" style="color:var(--accent);text-decoration:none;font-size:0.85rem;font-weight:500">&#128279; View on GitHub</a>
    <span style="color:var(--muted);margin:0 0.5rem">|</span>
    <a href="https://jlaiii.github.io/net-insights-hub/" target="_blank" style="color:var(--accent);text-decoration:none;font-size:0.85rem;font-weight:500">&#127760; Live Site</a>
  </div>
"""
lines.insert(55, insert_html)

with open('index.html','w',encoding='utf-8') as f:
    f.writelines(lines)
print('done')
