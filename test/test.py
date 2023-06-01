import os

path = './files/smartbugs'  # 输入文件夹地址
files = os.listdir(path)  # 读入文件夹
num_png = len(files)  # 统计文件夹中的文件个数
print(num_png)  # 打印文件个数
# 输出所有文件名
ss = set()
for line in files:

    ss.add(line[-3:])

print(ss)
