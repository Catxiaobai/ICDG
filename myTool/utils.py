#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/21 16:40
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import re
import subprocess
import threading

DIGITAL = 1  # 数字类型
STRING = 2  # 字符串类型


def runCMDWithTimeout(cmd):
    # 反编译字节码
    result = None
    try:
        # 执行命令并返回一个 Popen 对象
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 设置超时时间
        timer = threading.Timer(10, proc.kill)
        # 启动定时器
        timer.start()
        # 获取执行结果和错误信息
        out, err = proc.communicate()
        # 关闭定时器
        timer.cancel()
        # 解码结果为 utf-8 编码的字符串
        result = out.decode("utf-8")
    except subprocess.CalledProcessError as e:
        # 处理 CalledProcessError 异常并输出错误信息
        print(cmd[-1], "===> error:", e.returncode, e.output)
    except Exception as e:
        # 处理其他异常并输出错误信息
        print(cmd[-1], "===> error:", e)
    # 返回执行结果
    return result


# 定义函数getDisarmCode，参数为二进制代码
def getDisasmCode(binary):
    # 初始化变量disasmCode
    disasmCode = ""
    # 如果二进制代码以"0x"开头，去掉"0x"
    if binary.startswith("0x"):
        binary = binary[2:]
    try:
        # 将二进制代码写入tmp.txt文件
        with open("tmp.txt", "w") as f:
            f.write(binary)
        # 调用外部程序evm-1.8.14解析tmp.txt文件中的字节码
        disasmCode = runCMDWithTimeout(["evm", "disasm", "tmp.txt"])
        # print(disasmCode)
    # 捕获所有异常
    except Exception as e:
        # 输出错误信息
        print("getDisasmCode error:", e)
    # 无论是否发生异常，都会执行finally语句块，删除tmp.txt文件
    finally:
        subprocess.call(["rm", "-f", "tmp.txt"])
    # 返回解析结果
    if disasmCode is None or len(disasmCode) < 1 or 'STOP' not in disasmCode:
        return print('Disasm Failed')
    # print(int(disasmCode.split('\n')[-2].split(':')[0]))
    return disasmCode, int(disasmCode.split('\n')[-2].split(':')[0])


def replaceInstr(line):
    # 将SUICIDE替换为SELFDESTRUCT
    line = line.replace("SUICIDE", "SELFDESTRUCT")
    # 将Missing opcode 0xfd替换为REVERT
    line = line.replace("Missing opcode 0xfd", "REVERT")
    # 将Missing opcode 0xfe替换为ASSERTFAIL
    line = line.replace("Missing opcode 0xfe", "ASSERTFAIL")
    # 将所有Missing opcode都替换为INVALID
    line = re.sub(r"Missing opcode .+?", "INVALID", line)
    return line


def disasmParser(disasmCode, startId):
    disasm = []
    if int(startId) > 0:
        disasm.append((int(startId) - 1, ('JUMPDEST', ' ')))
    lines = disasmCode.split("\n")
    for i, line in enumerate(lines):
        if ':' not in line:
            continue
        line = replaceInstr(line)
        tmp = line.split(": ")
        # this is depends on evm version
        # lineID = Hex2Int(tmp[0])
        if tmp[0] == '':
            continue
        lineId = int(tmp[0]) + int(startId)
        tmp2 = tmp[1].split(" ")
        pushId = ""
        if len(tmp2) > 1:
            pushId = tmp2[1].replace("0x", "")
        instr = (tmp2[0], pushId)
        lineInstr = (lineId, instr)
        disasm.append(lineInstr)
    return disasm


def getType(instr):
    """
    检查指令是否为字符串，返回值为1表示是整数，返回值为2表示是字符串。Solidity没有双精度数。

    参数：
    instr: 元组类型，包含EVM指令操作码和操作数。

    返回：
    返回值为1表示操作数是整数，返回值为2表示操作数是字符串。
    """
    # 1: integer, 2: string. Solidity doesn't have double
    result = 1
    for i in range(len(instr)):
        if instr[i].isdigit() or instr[i] == '_':
            continue
        else:
            result = 2
            break
    return result
