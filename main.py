import pandas as pd
import numpy as np
import json
import os

xlsx_path = r"C:\Users\22068\PycharmProjects\PythonProject1\票价表.xlsx"

df = pd.read_excel(xlsx_path, header=None)
print("DataFrame 形状:", df.shape)

# ===== 关键修正 =====
# 站名行 = 索引 6；数据从索引 7 开始
# B列(1)=起点站，C列(2)往后=票价
col_names = df.iloc[6, 2:].tolist()
row_names = df.iloc[7:, 1].tolist()
data      = df.iloc[7:, 2:].values

print("列站名数量:", len(col_names))
print("行起点数量:", len(row_names))
print("数据形状:", data.shape)
print("前 10 个列站名:", [str(x) for x in col_names[:10]])
print("前 10 个行起点:", [str(x) for x in row_names[:10]])
print("-" * 60)

# ===== 线路名（第5行，前向填充合并单元格） =====
line_raw = df.iloc[5, 2:].tolist()
line_names, cur = [], None
for x in line_raw:
    if pd.notna(x):
        s = str(x).strip()
        if s:
            cur = s
    line_names.append(cur)

# ===== 建唯一站点表 + 站点-线路映射 =====
stations, station_line = [], {}
for name, line in zip(col_names, line_names):
    if pd.notna(name):
        s = str(name).strip()
        if s and s not in stations:
            stations.append(s)
            station_line[s] = line

print("唯一站点数:", len(stations))
print("前 20 个站点:", stations[:20])

# 兜底：行里出现但列里没有的站
for name in row_names:
    if pd.notna(name):
        s = str(name).strip()
        if s and s not in stations:
            stations.append(s)
            print("补入仅出现在行中的站点:", s)
print("-" * 60)

name_to_idx = {n: i for i, n in enumerate(stations)}
N = len(stations)

fares = np.full((N, N), 255, dtype=np.uint8)
for i in range(N):
    fares[i][i] = 0

matched, skipped = 0, []
for r, row_name in enumerate(row_names):
    if pd.isna(row_name):
        continue
    from_name = str(row_name).strip()
    if from_name not in name_to_idx:
        skipped.append(from_name)
        continue
    matched += 1
    fi = name_to_idx[from_name]
    row_data = data[r]
    for c, val in enumerate(row_data):
        if c >= len(col_names) or pd.isna(val):
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
            pass  # "未开通" 之类跳过

print("成功匹配数据的起点站数量:", matched)
print("未匹配的起点站数量:", len(skipped))
if skipped[:10]:
    print("未匹配示例:", skipped[:10])
print("-" * 60)

# ===== 对称性校验 =====
asym = []
for i in range(N):
    for j in range(i + 1, N):
        a, b = fares[i][j], fares[j][i]
        if a != 255 and b != 255 and a != b:
            asym.append((stations[i], stations[j], a, b))
print("不对称总数:", len(asym))
for x in asym[:10]:
    print("不对称:", x)
print("-" * 60)

filled = int(np.sum(fares != 255))
print(f"票价覆盖率: {filled}/{N*N} = {filled/(N*N):.1%}")

# ===== 保存 =====
with open("stations.json", "w", encoding="utf-8") as f:
    json.dump(stations, f, ensure_ascii=False, indent=2)

with open("station_lines.json", "w", encoding="utf-8") as f:
    json.dump(station_line, f, ensure_ascii=False, indent=2)

fares.tofile("fares.bin")

print("已保存 stations.json，站点数:", len(stations))
print("已保存 fares.bin，大小:", os.path.getsize("fares.bin"), "bytes")
print("期望大小:", N * N, "bytes")