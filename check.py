import pandas as pd
df = pd.read_excel(r"C:\Users\22068\PycharmProjects\PythonProject1\票价表.xlsx", header=None)
print("形状:", df.shape)
print()
for i in range(min(12, df.shape[0])):
    row = df.iloc[i, :10].tolist()
    # 把内容转成字符串方便看
    row = ['' if pd.isna(x) else str(x)[:12] for x in row]
    print(f"行{i:>2}: {row}")