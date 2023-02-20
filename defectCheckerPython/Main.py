#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/15 11:27
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import re

from DefectChecker import DefectChecker
from BinaryAnalyzer import BinaryAnalyzer
import subprocess
import time


def parserFromBytecode(bytecode):
    if len(bytecode) < 1:
        return None

    # 去除 Swarm 哈希
    bytecode = re.sub(r'a165627a7a72305820\S{64}0029$', '', bytecode)

    # 只需要运行时字节码，去除合约创建字节码
    if 'f30060806040' in bytecode:
        bytecode = bytecode[bytecode.index('f30060806040') + 4:]

    # 分析二进制代码
    binaryAnalyzer = BinaryAnalyzer(bytecode)

    # 如果二进制代码合法，则检测其各类代码质量问题
    if binaryAnalyzer.legalContract:
        try:
            defectChecker = DefectChecker(binaryAnalyzer)
            defectChecker.detectAllSmells()
            return defectChecker
        except Exception as e:
            print(e)
            return None

    return None


def parserFromSourceCodeFile(filePath, mainContracts):
    # 用 solc 编译合约源代码，获取其二进制代码
    cmd = ['solc', '--bin-runtime', filePath]
    try:
        binary = subprocess.check_output(cmd).decode()
    except subprocess.CalledProcessError as e:
        print('Compile Error:', filePath)
        return

    if not binary or len(binary) < 1:
        print('Compile Error:', filePath)
        return

    tmp = binary.split("\n")

    # 遍历 solc 输出的二进制代码字符串列表
    for i in range(len(tmp) - 1):
        # 如果当前字符串是 "Binary"，则该字符串的上一行是合约地址，下一行是合约二进制代码
        if tmp[i].startswith('Binary'):
            address = tmp[i - 1].replace('=', '').replace(' ', '').replace('\n', '')  # 获取合约地址
            bytecode = tmp[i + 1]  # 获取合约二进制代码

            # 如果该合约不是我们需要分析的主要合约，则继续遍历
            if mainContracts not in address:
                continue

            print(address)

            # 对合约二进制代码进行代码质量问题检测，并打印检测结果
            defectChecker = parserFromBytecode(bytecode)
            print(defectChecker.printAllDetectResult())


def main():
    start_time = time.time()  # 计时开始
    # 从字节码检测缺陷
    bytecode1 = "608060405260043610603e5763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416631003e2d281146043575b600080fd5b348015604e57600080fd5b5060586004356073565b60408051921515835260208301919091528051918290030190f35b6000805482018082558190831115608657fe5b9150915600"
    bytecode = "60806040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680630103c92b146100515780630fdb1c10146100a8575b600080fd5b34801561005d57600080fd5b50610092600480360381019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506100bf565b6040518082815260200191505060405180910390f35b3480156100b457600080fd5b506100bd6100d7565b005b60006020528060005260406000206000915090505481565b60008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205490506000811115610195573373ffffffffffffffffffffffffffffffffffffffff168160405160006040518083038185875af1925050505060008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055505b505600a165627a7a72305820a2a872c11cc01048a3e18a4a62a294aaec42c25f66692b299e285dea78c55d790029"
    byteDefectChecker = parserFromBytecode(bytecode1)
    print(byteDefectChecker.printAllDetectResult())
    # 从源代码检测缺陷
    # filePath = "1.sol"
    # parserFromSourceCodeFile(filePath, "Overflow")

    end_time = time.time()  # 计时结束
    print(f"Running time: {end_time - start_time:.2f} s")  # 输出总运行时间


if __name__ == '__main__':
    main()
