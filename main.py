import os
import shutil


# 删除文件夹下面的所有文件(只删除文件,不删除文件夹)
# python删除文件的方法 os.remove(path)path指的是文件的绝对路径,如：
def del_file(path):
    if os.path.exists(path):
        for i in os.listdir(path):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
            file_data = path + "\\" + i  # 当前文件夹的下面的所有东西的绝对路径
            if os.path.isfile(file_data):  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
                os.remove(file_data)
            else:
                del_file(file_data)
    else:
        os.makedirs(path)


# 多合约文件字节码
def create_evm():
    path_data = "evm"
    del_file(path_data)
    with open("solc.txt") as f:
        lines = f.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            print(lines[i])
            if lines[i].find(".sol:") != -1:
                print(lines[i].split(':')[1][:-8])
                fileName = lines[i].split(':')[1][:-8]
            if lines[i] == "Binary of the runtime part:":
                print(lines[i + 1].strip())
                # fileName = 'note.txt'
                with open(path_data+'/'+fileName+'.bytecode', 'w', encoding='utf-8') as file:
                    file.write(lines[i + 1].strip())


if __name__ == '__main__':
    create_evm()
