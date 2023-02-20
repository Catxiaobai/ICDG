#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/15 10:27
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import re
import subprocess
import threading
from typing import List, Tuple
from Pair import Pair

DIGITAL = 1  # 数字类型
STRING = 2  # 字符串类型


def runCMDWithTimeout(cmd):
    # 初始化结果为空
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


# 定义函数getDisasmCode，参数为二进制代码
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
    # 捕获所有异常
    except Exception as e:
        # 输出错误信息
        print("getDisasmCode error:", e)
    # 无论是否发生异常，都会执行finally语句块，删除tmp.txt文件
    finally:
        subprocess.call(["rm", "-f", "tmp.txt"])
    # 返回解析结果
    return disasmCode


def replaceInsr(line: str) -> str:
    # 将SUICIDE替换为SELFDESTRUCT
    line = line.replace("SUICIDE", "SELFDESTRUCT")
    # 将Missing opcode 0xfd替换为REVERT
    line = line.replace("Missing opcode 0xfd", "REVERT")
    # 将Missing opcode 0xfe替换为ASSERTFAIL
    line = line.replace("Missing opcode 0xfe", "ASSERTFAIL")
    # 将所有Missing opcode都替换为INVALID
    line = re.sub(r"Missing opcode .+?", "INVALID", line)
    return line


def Hex2Int(hex_str: str) -> int:
    # 将十六进制字符串转换为整数
    if len(hex_str) < 1:
        return 0
    return int(hex_str, 16)


def Hex2Long(hex_str: str) -> int:
    # 将十六进制字符串转换为长整型整数
    if len(hex_str) < 1:
        return 0
    return int(hex_str, 16)


def disasmParser(disasmCode: str) -> List[Tuple[int, Tuple[str, str]]]:
    """
    将EVM汇编代码字符串解析为一个由元组组成的列表，每个元组包含行号和指令。

    参数：
    disasmCode：EVM汇编代码字符串。

    返回：
    解析后的元组列表，每个元组包含行号和指令。
    """
    disasm = []
    lines = disasmCode.split("\n")
    start = False
    for line in lines:
        if not start:
            start = True
            continue
        line = replaceInsr(line)
        tmp = line.split(": ")
        # this is depends on evm verson
        # lineID = Hex2Int(tmp[0])
        if tmp[0] == '':
            continue
        lineID = int(tmp[0])
        tmp2 = tmp[1].split(" ")
        pushID = ""
        if len(tmp2) > 1:
            pushID = tmp2[1].replace("0x", "")
        instr = (tmp2[0], pushID)
        lineInstr = (lineID, instr)
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


def splitInstr2(instr):
    instr = instr.replace(" ", "")  # 去掉指令中的空格
    res = Pair()  # 用于存储解析出的指令的两部分
    flag = 0  # 标记当前字符处于括号内部还是外部。flag为0时，代表在括号外部；flag为1时，代表在第一层括号内部，以此类推
    start_pos = -1  # 记录第一层括号的起始位置
    split_pos = -1  # 记录逗号分隔符的位置
    end_pos = -1  # 记录第一层括号的结束位置
    # 对每一个字符进行处理
    for i in range(len(instr)):
        c = instr[i]
        if c == '(':
            flag += 1
            if flag == 1 and start_pos == -1:  # 如果发现第一个左括号，并且尚未记录第一层括号的起始位置
                start_pos = i
        elif c == ')':
            flag -= 1
            if flag == 1 and start_pos != -1 and split_pos != -1:  # 如果当前是第一层括号的最后一个右括号，并且已经记录下了逗号分隔符的位置
                end_pos = i + 1  # 记录第一层括号的结束位置
            elif flag == 0 and start_pos != -1 and split_pos != -1:  # 如果当前是最后一个右括号，并且已经记录下了逗号分隔符的位置
                end_pos = i  # 记录第一层括号的结束位置
        elif c == ',':
            if flag == 1 and start_pos != -1 and split_pos == -1:  # 如果当前处于第一层括号内部，并且还未记录下逗号分隔符的位置
                split_pos = i  # 记录逗号分隔符的位置
    res.setFirst(instr[start_pos + 1:split_pos])  # 解析出第一个部分
    res.setSecond(instr[split_pos + 1:end_pos])  # 解析出第二个部分
    return res


def getSlotID(condition):
    # 从字符串条件中解析出读取的 slot id
    # 示例: SLOAD_382(SHA3_381(0_379,64_378)) -> 382
    # 示例: SLOAD_382(0_64) -> 64
    slotID = -1
    p = re.compile(r"SLOAD_\d+\((\d+?)_")
    m = p.search(condition)
    if m:
        tmp = m.group(1)
        if tmp.isnumeric():
            slotID = int(tmp)
    return slotID


def getSlotAddress(condition):
    # 从字符串条件中解析出读取的 slot 对应的地址
    # 示例: ISZERO_389(GT_388(SLOAD_382(SHA3_381(0_379,64_378)),0_385)) -> SHA3(0, 64)
    address = ""
    start = -1
    end = -1
    idx = 0
    for i in range(condition.find("SLOAD_"), len(condition)):
        if condition[i] == '(':
            idx += 1
            if start == -1:
                start = i
        if condition[i] == ')':
            idx -= 1
        if idx == 0 and start > 0:
            end = i
            break
    if end > start:
        address = condition[start + 1:end]
    # 移除掉 _{数字} 形式的后缀
    address = re.sub(r"_[0-9]+", "", address)
    return address


def legalRange(pos: int, ranges: List[Tuple[int, int]]) -> bool:
    # 判断指定位置 pos 是否在 ranges 中的某个区间内
    for range_start, range_end in ranges:
        if range_start <= pos <= range_end:
            return True
    return False


def getGroundTruth(file):
    # 从文件中读取每个合约地址的 Ground Truth（即每个属性是否合规）
    groundTruthList = {}
    try:
        with open(file) as reader:
            for line in reader:
                tmp = line.strip().split(",")
                answerList = [False] * 8  # 初始化一个长度为 8 的全 False 的列表
                if tmp[1] == "1":  # 1-B: Uncheck External Calls
                    answerList[0] = True
                if tmp[3] == "1":  # 3-D: Strict Balance Equality
                    answerList[1] = True
                if tmp[5] == "1":  # 5-F: Transaction State Dependency
                    answerList[2] = True
                if tmp[8] == "1":  # 8-I: Block Info Dependency
                    answerList[3] = True
                if tmp[18] == "1":  # 18-S: Greedy Contract
                    answerList[4] = True
                if tmp[2] == "1":  # 2-C: DoS Under External Influence
                    answerList[5] = True
                if tmp[9] == "1":  # 9-J: Nest Call
                    answerList[6] = True
                if tmp[6] == "1":  # 6-G: Reentrancy
                    answerList[7] = True
                # 将 address 作为 key，answerList 作为 value，加入到字典中
                groundTruthList[tmp[0].replace("0x", "")] = answerList
    except Exception as e:
        print(e)
    return groundTruthList


def getBytecodeFromFile(file):
    bytecode = ""  # 初始化bytecode为空字符串
    try:
        with open(file) as reader:  # 读取指定文件
            bytecode = reader.read().replace("\n", "")  # 读取文件内容并去除换行符
    except Exception as e:
        print(e)  # 如果出现异常，打印异常信息
    return bytecode  # 返回读取的bytecode


def printAnswerCheck(groundTruth, defectChecker):
    # 检查项目依次为：0.未检查的外部调用；1.余额检查；2.交易状态检查；3.块信息检查；4.贪心合约检查；5.外部影响下的DoS检查；
    # 6.嵌套调用检查；7.重入检查
    if defectChecker.hasUnchechedExternalCalls != groundTruth[0]:  # 检查未检查的外部调用是否符合期望结果
        print("Uncheck External Calls check fail. The answer is", groundTruth[0])

    if defectChecker.hasStrictBalanceEquality != groundTruth[1]:  # 检查余额检查是否符合期望结果
        print("Strict Balance Equality check fail. The answer is", groundTruth[1])

    if defectChecker.hasTransactionStateDependency != groundTruth[2]:  # 检查交易状态检查是否符合期望结果
        print("Transaction State Dependency check fail. The answer is", groundTruth[2])

    if defectChecker.hasBlockInfoDependency != groundTruth[3]:  # 检查块信息检查是否符合期望结果
        print("Block Info Dependency check fail. The answer is", groundTruth[3])

    if defectChecker.hasGreedyContract != groundTruth[4]:  # 检查贪心合约检查是否符合期望结果
        print("Greedy Contract check fail. The answer is", groundTruth[4])

    if defectChecker.hasDoSUnderExternalInfluence != groundTruth[5]:  # 检查外部影响下的DoS检查是否符合期望结果
        print("DoS Under External Influence check fail. The answer is", groundTruth[5])

    if defectChecker.hasNestCall != groundTruth[6]:  # 检查嵌套调用检查是否符合期望结果
        print("Nest Call check fail. The answer is", groundTruth[6])

    if defectChecker.hasReentrancy != groundTruth[7]:  # 检查重入检查是否符合期望结果
        print("Reentrancy check fail. The answer is", groundTruth[7])
