#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/21 16:35
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import utils
from BasicBlock import BasicBlock


class BinaryAnalyzer:
    def __init__(self):
        self.pos2BlockMap = {}  # 记录每个代码块的开始位置和结束位置
        self.publicFunctionStartList = []  # 所有其他函数可以调用的函数列表（不包括回退函数）
        self.stackEvents = []  # 栈事件
        self.allInstrs = set()  # 所有的操作指令集合
        self.startPosList = []  # 代码块的开始位置列表
        self.disasm = None  # 反汇编器对象
        self.disasmCode = None  # 反汇编后的代码字符串
        self.versionGap = False  # 是否存在版本间的不兼容
        self.legalContract = True  # 是否为合法的合约代码
        self.codeCoverage = 0  # 代码覆盖率
        self.fallbackPos = -1  # 回退函数的位置
        self.misRecognizedJump = False  # 是否存在无法识别的跳转指令
        self.cyclomaticComplexity = 0  # 圈复杂度
        self.numInstrs = 0  # 指令数量

        self.visitBlock = set()  # 记录访问过的代码块
        self.totalEdge = set()  # 记录所有边
        self.allCallPath = []  # 所有调用路径
        self.allCirclePath2StartPos = {}  # 所有循环路径的起始位置
        self.allCirclePath = []  # 所有循环路径

        # 目标函数的结束位置
        self.aimContractEndPos = -1
        self.aimDisasmCode = None
        # self.getBasicBlock(bytecode)

    def getDisasmCode(self, bytecode):
        disasmCode, pos = utils.getDisasmCode(bytecode)
        self.disasmCode += disasmCode
        return pos

    def getAimDisasmCode(self, bytecode):
        aimDisasmCode, pos = utils.getDisasmCode(bytecode)
        self.aimDisasmCode += aimDisasmCode
        return pos

    def getDisasm(self):
        self.disasm = utils.disasmParser(self.aimDisasmCode, 0)
        self.disasm += utils.disasmParser(self.disasmCode, self.aimContractEndPos)
        print(self.disasm)

    def getBasicBlock(self):
        block = BasicBlock()
        # 定义一个布尔值start用来表示块的起始位置，lastPos用来存储上一个位置
        start = True
        lastPos = -1
        # 对指令进行循环处理
        for i in range(len(self.disasm)):
            # 获取指令对和位置
            instr_pair = self.disasm[i]
            pos = instr_pair[0]
            # 获取指令
            instr = instr_pair[1][0]
            # 将指令添加到所有指令集合中
            self.allInstrs.add(instr)
            # 如果块的起始位置为True或者当前指令为JUMPDEST，则创建一个新的块
            if start or instr == 'JUMPDEST':
                # 如果不是第一个块，将上一个块的结束位置设置为上一个位置，并将其添加到块映射表中
                if i != 0:
                    block.endBlockPos = lastPos
                    self.pos2BlockMap[block.startBlockPos] = block
                # 初始化一个新的块并设置其起始位置
                block = BasicBlock()
                block.startBlockPos = pos
                # 将起始位置添加到起始位置列表中
                self.startPosList.append(pos)
                start = False
            # 如果当前指令是JUMPI，则说明当前块可能是条件块
            elif instr == 'JUMPI':
                start = True
                block.jumpType = BasicBlock.CONDITIONAL
            # 如果当前指令是JUMP，则说明当前块是无条件跳转块
            elif instr == 'JUMP':
                start = True
                block.jumpType = BasicBlock.UNCONDITIONAL
            # 添加了关于跨合约的部分
            elif instr in {'CALL', 'DELEGATECALL', 'CALLCODE', 'STATICCALL'}:
                start = True
                block.jumpType = BasicBlock.CROSS
            # 如果当前指令为STOP、RETURN、REVERT、SELFDESTRUCT或ASSERTFAIL，则说明当前块是终止块
            if instr in {'STOP', 'RETURN', 'REVERT', 'SELFDESTRUCT', 'ASSERTFAIL'}:
                start = True
                block.jumpType = BasicBlock.TERMINAL
            # 将指令对添加到块的指令列表中，并将指令添加到块的指令字符串中
            block.instrList.append(instr_pair)
            block.instrString.join(f'{instr} ')
            # 将lastPos设置为当前位置，如果当前位置为最后一个位置，则将当前块的结束位置设置为lastPos，并将其添加到块映射表中
            lastPos = pos
            if i == len(self.disasm) - 1:
                block.endBlockPos = lastPos
                self.pos2BlockMap[block.startBlockPos] = block
