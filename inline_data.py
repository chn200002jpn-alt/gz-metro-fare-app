# -*- coding: utf-8 -*-
import json, base64, os

WWW = os.path.join(os.path.dirname(__file__), 'www')

with open(os.path.join(WWW, 'stations.json'), encoding='utf-8') as f:
    stations = json.load(f)
with open(os.path.join(WWW, 'station_lines2.json'), encoding='utf-8') as f:
    lines = json.load(f)
with open(os.path.join(WWW, 'coords.json'), encoding='utf-8') as f:
    coords = json.load(f)
with open(os.path.join(WWW, 'fares.bin'), 'rb') as f:
    fares_b64 = base64.b64encode(f.read()).decode()

with open(os.path.join(WWW, 'index.html'), encoding='utf-8') as f:
    html = f.read()

# 在 </head> 之前插入数据 <script>
data_script = f'''
<script>
  window.__STATIONS__ = {json.dumps(stations, ensure_ascii=False)};
  window.__LINES__ = {json.dumps(lines, ensure_ascii=False)};
  window.__COORDS__ = {json.dumps(coords, ensure_ascii=False)};
  window.__FARES_B64__ = "{fares_b64}";
</script>
'''

html = html.replace('</head>', data_script + '</head>')

with open(os.path.join(WWW, 'index_inline.html'), 'w', encoding='utf-8') as f:
    f.write(html)

print('已生成 www/index_inline.html')