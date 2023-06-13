#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/21 16:13
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import os
import re
import subprocess
import time

from BinaryAnalyzer import BinaryAnalyzer
from VulnerabilityScanner import VulnerabilityScanner


def parserFromAimBytecode(bytecode):
    if len(bytecode) < 1:
        return None

    # 去除 Swarm 哈希
    bytecode = re.sub(r'a165627a7a72305820\S{64}0029$', '', bytecode)

    # 只需要运行时字节码，去除合约创建字节码
    if 'f30060806040' in bytecode:
        createBytecode = bytecode[:bytecode.index('f30060806040') + 4]
        bytecode = bytecode[bytecode.index('f30060806040') + 4:]
        # print(createBytecode)

    return bytecode


def parserFromBytecode(bytecode):
    if len(bytecode) < 1:
        return None

    # 去除 Swarm 哈希
    bytecode = re.sub(r'a165627a7a72305820\S{64}0029$', '', bytecode)

    binaryAnalyzer = BinaryAnalyzer()
    # 只需要运行时字节码，去除合约创建字节码
    if 'f30060806040' in bytecode:
        createBytecode = bytecode[:bytecode.index('f30060806040') + 4]  # todo:暂未使用创建时代码
        bytecode = bytecode[bytecode.index('f30060806040') + 4:]
        pos = binaryAnalyzer.getAimDisasmCode(bytecode) + 2
        binaryAnalyzer.aimContractEndPos = pos
    binaryAnalyzer.MCFGConstruction()

    # 如果二进制代码合法，则检测其各类代码质量问题
    if binaryAnalyzer.legalContract:
        try:
            vulnScan = VulnerabilityScanner(binaryAnalyzer)
            vulnScan.scanVulnerability()
        except Exception as e:
            print(e)


def parserFromSourceCodeFiles(file, aimContract):
    """
    从源代码文件开始进行解析，适用情形为多个合约写在一个sol文件
    :param file: 输入文件
    :param aimContract: 待检测合约
    """
    # 用 solc 编译合约源代码，获取其二进制代码
    cmd = ['solc', '--bin', '--optimize', file]
    try:
        binary = subprocess.check_output(cmd).decode()
    except subprocess.CalledProcessError as e:
        print('Compile Error:', file)
        return

    if not binary or len(binary) < 1:
        print('Compile Error:', file)
        return

    tmp = binary.split("\n")

    binaryAnalyzer = BinaryAnalyzer()
    # 遍历 solc 输出的二进制代码字符串列表
    for i in range(len(tmp) - 1):
        # 如果当前字符串是 "Binary"，则该字符串的上一行是合约地址，下一行是合约二进制代码
        if tmp[i].startswith('Binary'):
            name = tmp[i - 1].replace('=', '').replace(' ', '').replace('\n', '')  # 获取合约名称
            bytecode = tmp[i + 1]  # 获取该合约二进制代码
            bytecode = parserFromAimBytecode(bytecode)
            # 如果该合约是我们需要分析的主要合约，则记录结束节点位置
            if aimContract in name:
                pos = binaryAnalyzer.getAimDisasmCode(bytecode) + 2
                binaryAnalyzer.aimContractEndPos = pos
            else:
                binaryAnalyzer.getDisasmCode(bytecode)

    binaryAnalyzer.MCFGConstruction()

    if binaryAnalyzer.legalContract:
        try:
            vulnScan = VulnerabilityScanner(binaryAnalyzer)
            vulnScan.scanVulnerability()
        except Exception as e:
            print(e)


def parserFromSourceCodeFiles2(file):
    """
    从源代码文件开始进行解析，适用情形为多个合约写在一个sol文件
    :param file: 输入文件
    :param aimContract: 待检测合约
    """
    # 用 solc 编译合约源代码，获取其二进制代码
    cmd = ['solc', '--bin', '--optimize', file]
    try:
        binary = subprocess.check_output(cmd).decode()
    except subprocess.CalledProcessError as e:
        print('Compile Error:', file)
        return

    if not binary or len(binary) < 1:
        print('Compile Error:', file)
        return

    tmp = binary.split("\n")

    binaryAnalyzer = BinaryAnalyzer()
    # 遍历 solc 输出的二进制代码字符串列表
    aimContract = False
    for i in range(len(tmp) - 1):
        # 如果当前字符串是 "Binary"，则该字符串的上一行是合约地址，下一行是合约二进制代码
        if tmp[i].startswith('Binary'):
            name = tmp[i - 1].replace('=', '').replace(' ', '').replace('\n', '')  # 获取合约名称
            bytecode = tmp[i + 1]  # 获取该合约二进制代码
            bytecode = parserFromAimBytecode(bytecode)
            # 如果该合约是我们需要分析的主要合约，则记录结束节点位置
            if not aimContract:
                aimContract = True
                pos = binaryAnalyzer.getAimDisasmCode(bytecode) + 2
                binaryAnalyzer.aimContractEndPos = pos
            else:
                if bytecode is not None:
                    binaryAnalyzer.getDisasmCode(bytecode)

    binaryAnalyzer.MCFGConstruction(file)

    # if binaryAnalyzer.legalContract:
    #     try:
    #         vulnScan = VulnerabilityScanner(binaryAnalyzer)
    #         vulnScan.scanVulnerability()
    #     except Exception as e:
    #         print(e)


def main():
    start_time = time.time()  # 计时开始
    # 从源代码检测缺陷
    # file = "timestamps/1.sol"
    # parserFromSourceCodeFiles(file, "Test2")
    # 文件夹下检测
    filePath = "../files/example/"
    pathList = os.listdir(filePath)
    pathList.sort()
    for fileName in pathList:
        print(fileName)
        file = filePath + fileName
        parserFromSourceCodeFiles2(file)
        # break
    end_time = time.time()  # 计时结束
    print(f"Running time: {end_time - start_time:.2f} s")  # 输出总运行时间


if __name__ == '__main__':
    main()
