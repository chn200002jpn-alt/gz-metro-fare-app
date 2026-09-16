# -*- coding: utf-8 -*-
"""
地铁票价数据清洗脚本 v2
输入：票价表.xlsx（和本脚本同目录）
输出：
  stations.json        - 站点列表（按 Excel 列顺序）
  station_lines2.json  - {站名: [线路...]}  换乘站含多条线路
  fares.bin            - N×N uint8 票价矩阵（255 = 无数据）
"""

import os
import json
import numpy as np
import pandas as pd

# ============ 配置 ============
BASE_DIR  = r"C:\Users\22068\PycharmProjects\PythonProject1"
XLSX_PATH = os.path.join(BASE_DIR, "票价表.xlsx")
OUT_DIR   = BASE_DIR

# Excel 结构
ROW_LINE_NAMES = 2
ROW_STATION    = 3
ROW_DATA_START = 4
COL_STATION    = 1
COL_DATA_START = 2

# ============ 读 Excel ============
print(f"读取: {XLSX_PATH}")
df = pd.read_excel(XLSX_PATH, header=None)
print(f"DataFrame 形状: {df.shape}")

col_names = df.iloc[ROW_STATION, COL_DATA_START:].tolist()
row_names = df.iloc[ROW_DATA_START:, COL_STATION].tolist()
data      = df.iloc[ROW_DATA_START:, COL_DATA_START:].values

print(f"列站名数量: {len(col_names)}")
print(f"行起点数量: {len(row_names)}")
print(f"数据形状  : {data.shape}")

# ============ 线路名（第5行，前向填充）============
line_raw = df.iloc[ROW_LINE_NAMES, COL_DATA_START:].tolist()
line_names = []
cur = None
for x in line_raw:
    if pd.notna(x):
        s = str(x).strip()
        if s:
            cur = s
    line_names.append(cur)

# ============ 建站点列表 + 站点→多线路映射 ============
stations = []
station_lines2 = {}

for name, line in zip(col_names, line_names):
    if pd.isna(name):
        continue
    s = str(name).strip()
    if not s:
        continue
    if s not in stations:
        stations.append(s)
    if line:
        line = str(line).strip()
        if line:
            station_lines2.setdefault(s, [])
            if line not in station_lines2[s]:
                station_lines2[s].append(line)

# 兜底：行里出现但列里没有的站
for name in row_names:
    if pd.isna(name):
        continue
    s = str(name).strip()
    if s and s not in stations:
        print(f"[警告] 站点仅出现在行中，补入: {s}")
        stations.append(s)
        station_lines2.setdefault(s, ['未知线路'])

print(f"唯一站点数: {len(stations)}")

# ============ 建票价矩阵 ============
name_to_idx = {n: i for i, n in enumerate(stations)}
N = len(stations)

fares = np.full((N, N), 255, dtype=np.uint8)
for i in range(N):
    fares[i][i] = 0

matched = 0
skipped_rows = []

for r, row_name in enumerate(row_names):
    if pd.isna(row_name):
        continue
    from_name = str(row_name).strip()
    if from_name not in name_to_idx:
        skipped_rows.append(from_name)
        continue
    matched += 1
    fi = name_to_idx[from_name]
    row_data = data[r]
    for c, val in enumerate(row_data):
        if c >= len(col_names):
            break
        if pd.isna(val):
            continue
        to_raw = col_names[c]
        if pd.isna(to_raw):
            continue
        to_name = str(to_raw).strip()
        if to_name not in name_to_idx:
            continue
        ti = name_to_idx[to_name]
        try:
            fares[fi][ti] = int(val)
        except (ValueError, TypeError):
            pass

print(f"成功匹配的起点站: {matched}")
print(f"未匹配的起点站  : {len(skipped_rows)}")
if skipped_rows[:10]:
    print(f"未匹配示例      : {skipped_rows[:10]}")

# ============ 对称性检查 ============
asym = 0
for i in range(N):
    for j in range(i + 1, N):
        a, b = fares[i][j], fares[j][i]
        if a != 255 and b != 255 and a != b:
            asym += 1
            if asym <= 5:
                print(f"[不对称] {stations[i]} <-> {stations[j]}: {a} vs {b}")
print(f"不对称总数: {asym}")

filled = int(np.sum(fares != 255))
print(f"票价覆盖率: {filled}/{N*N} = {filled/(N*N):.1%}")

# ============ 保存 ============
out_stations = os.path.join(OUT_DIR, "stations.json")
out_lines2   = os.path.join(OUT_DIR, "station_lines2.json")
out_fares    = os.path.join(OUT_DIR, "fares.bin")

with open(out_stations, "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

with open(out_lines2, "w", encoding="utf-8") as f:
    json.dump(station_lines2, f, ensure_ascii=False, indent=2)

fares.tofile(out_fares)

print("-" * 50)
print(f"已保存 {out_stations}  (站点数 {len(stations)})")
print(f"已保存 {out_lines2}")
print(f"已保存 {out_fares}  ({os.path.getsize(out_fares)} bytes, 期望 {N*N})")

# ============ 换乘站预览 ============
multi = {s: lns for s, lns in station_lines2.items() if len(lns) > 1}
print("-" * 50)
print(f"换乘站数量: {len(multi)}")
for s, lns in list(multi.items())[:8]:
    print(f"  {s}: {' / '.join(lns)}")