#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/21 16:35
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import utils
from BasicBlock import BasicBlock
from EvmSimulator import EvmSimulator
from graphviz import Digraph  # 导入graphviz库


class BinaryAnalyzer:
    def __init__(self):
        self.pos2BlockMap = {}  # 记录每个代码块的开始位置和结束位置
        self.publicFunctionStartList = []  # 所有其他函数可以调用的函数列表（不包括回退函数）
        self.stackEvents = []  # 栈事件
        self.allInstrs = set()  # 所有的操作指令集合
        self.startPosList = []  # 代码块的开始位置列表
        self.disasm = None  # 反汇编器对象
        self.disasmCode = ''  # 反汇编后的代码字符串
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
        self.aimDisasmCode = ''

    def getDisasmCode(self, bytecode):
        disasmCode, pos = utils.getDisasmCode(bytecode)
        self.disasmCode += disasmCode

    def getAimDisasmCode(self, bytecode):
        aimDisasmCode, pos = utils.getDisasmCode(bytecode)
        self.aimDisasmCode = aimDisasmCode
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
                    if block.startBlockPos >= self.aimContractEndPos - 1:
                        block.isCalledContract = True
                        block.callJumpPos = self.aimContractEndPos
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
                if instr == 'STOP':
                    if block.startBlockPos == self.aimContractEndPos - 2 or i == len(self.disasm) - 1:
                        block.endBlockPos = True
                    else:
                        block.endBlockPos = False
                if not block.endBlockPos:
                    if block.startBlockPos < self.aimContractEndPos - 2:
                        block.terminalJumpPos = self.aimContractEndPos - 2
                    else:
                        block.terminalJumpPos = self.disasm[-1][0]
            # 将指令对添加到块的指令列表中，并将指令添加到块的指令字符串中
            block.instrList.append(instr_pair)
            block.instrString += instr + " "
            # 将lastPos设置为当前位置，如果当前位置为最后一个位置，则将当前块的结束位置设置为lastPos，并将其添加到块映射表中
            lastPos = pos
            if i == len(self.disasm) - 1:
                block.endBlockPos = lastPos
                self.pos2BlockMap[block.startBlockPos] = block
                if block.startBlockPos >= self.aimContractEndPos - 1:
                    block.isCalledContract = True
                    block.callJumpPos = self.aimContractEndPos
        print(self.pos2BlockMap)

    def addFallEdges(self) -> None:
        # 添加从当前基本块到“落地点”（即下一个基本块）的边
        for i in range(len(self.startPosList) - 1):
            startPos = self.startPosList[i]  # 获取当前基本块的起始位置
            block = self.pos2BlockMap[startPos]  # 根据起始位置获取基本块
            if block.jumpType in {BasicBlock.FALL, BasicBlock.CONDITIONAL,
                                  BasicBlock.CROSS}:  # myTool:添加了CROSS，因为除了有跳转还有顺序执行
                block.fallPos = self.startPosList[i + 1]  # 在当前基本块上设置“落地点”（即下一个基本块的起始位置）

    def buildCFG(self, first, functionPos):
        # 通过 EVMSimulator 类的实例化获取控制流图
        simulator = EvmSimulator(self.pos2BlockMap, first, functionPos)
        # 更新控制流图相关的变量
        self.pos2BlockMap.update(simulator.pos2BlockMap)
        self.stackEvents = simulator.stackEvents
        self.versionGap = simulator.versionGap
        self.misRecognizedJump = simulator.misRecognizedJump
        if self.versionGap:
            # 如果字节码版本不支持，则打印警告信息
            print("Bytecode version may not support. The default Solidity version is 0.4.25;")
        return simulator.functionPosMap

    def flagLoop(self, totalPath, startLoopPos):
        startLoopBlock = self.pos2BlockMap[startLoopPos]  # 获取循环的起始基本块
        startLoopBlock.isCircleStart = True  # 在起始基本块上设置循环的起始标记
        start = False
        circlePath = []
        for i in range(len(totalPath)):
            pos = totalPath[i]  # 获取当前基本块的起始位置
            if pos == startLoopPos:
                start = True
            if start:
                block = self.pos2BlockMap[pos]  # 获取当前基本块
                block.isCircle = True  # 在当前基本块上设置循环标记
                circlePath.append(block.startBlockPos)  # 将当前基本块的起始位置添加到循环路径中
                if i < len(totalPath) - 1:
                    # 如果不是最后一个基本块，则添加一条从当前基本块到下一个基本块的路径
                    path = str(pos) + "_" + str(totalPath[i + 1])
                    self.allCirclePath2StartPos[path] = startLoopPos
                elif i == len(totalPath) - 1:
                    # 如果是最后一个基本块，则添加一条从当前基本块到循环起始基本块的路径
                    path = str(pos) + "_" + str(startLoopPos)
                    self.allCirclePath2StartPos[path] = startLoopPos
        self.allCirclePath.append(circlePath)  # 将循环路径添加到所有循环路径中

    def findCallPathAndLoops(self, currentPath, block, visited):
        # 从当前代码块出发，记录已访问过的起始位置
        self.visitBlock.add(block.startBlockPos)
        # 如果代码块包含CALL指令，则将当前路径添加到self.allCallPath列表中
        if "CALL " in block.instrString:
            self.allCallPath.append(currentPath)

        # 根据跳转类型分别处理条件跳转、无条件跳转和跌落跳转
        if block.jumpType == BasicBlock.CONDITIONAL:
            # 处理条件跳转的左分支
            left_branch = block.conditionalJumpPos
            path = f"{block.startBlockPos}_{left_branch}"
            self.totalEdge.add(path)

            # 如果左分支未被访问，则继续寻找
            if path not in visited and left_branch > 0:
                # 将左分支加入当前路径，然后递归调用函数查找调用路径和循环
                visited.add(path)
                newPath = currentPath.copy()
                newPath.append(left_branch)
                self.findCallPathAndLoops(newPath, self.pos2BlockMap[left_branch], visited)
            # 如果左分支已经在已知的环路上，则将该环路标记为循环
            elif path in self.allCirclePath2StartPos:
                self.flagLoop(currentPath, self.allCirclePath2StartPos[path])
            # 如果左分支指向当前路径中的某一代码块，则将该路径标记为循环
            elif left_branch > 0 and left_branch in currentPath:
                self.flagLoop(currentPath, block.startBlockPos)

            # 处理条件跳转的右分支
            right_branch = block.fallPos
            path = f"{block.startBlockPos}_{right_branch}"
            self.totalEdge.add(path)
            # 如果右分支未被访问，则继续寻找
            if path not in visited and right_branch > 0:
                # 将右分支加入当前路径，然后递归调用函数查找调用路径和循环
                visited.add(path)
                newPath = currentPath.copy()
                newPath.append(right_branch)
                self.findCallPathAndLoops(newPath, self.pos2BlockMap[right_branch], visited)
            # 如果右分支已经在已知的环路上，则将该环路标记为循环
            elif path in self.allCirclePath2StartPos:
                self.flagLoop(currentPath, self.allCirclePath2StartPos[path])
            # 如果右分支指向当前路径中的某一代码块，则将该路径标记为循环
            elif right_branch > 0 and right_branch in currentPath:
                self.flagLoop(currentPath, block.startBlockPos)

        elif block.jumpType == BasicBlock.UNCONDITIONAL:
            # 处理无条件跳转
            jumpPos = block.unconditionalJumpPos
            path = f"{block.startBlockPos}_{jumpPos}"
            self.totalEdge.add(path)
            # 如果跳转位置未被访问，则继续寻找
            if path not in visited and jumpPos > 0:
                visited.add(path)
                newPath = currentPath.copy()
                newPath.append(jumpPos)
                self.findCallPathAndLoops(newPath, self.pos2BlockMap[jumpPos], visited)
            # 如果跳转位置已经在当前路径上，则标记循环
            elif jumpPos > 0 and jumpPos in currentPath:
                self.flagLoop(currentPath, block.startBlockPos)
            # 如果跳转路径已经存在于已知循环路径列表，则标记循环
            elif path in self.allCirclePath2StartPos:
                self.flagLoop(currentPath, self.allCirclePath2StartPos[path])

        elif block.jumpType == BasicBlock.FALL:
            # 处理顺序执行
            jumpPos = block.fallPos
            path = f"{block.startBlockPos}_{jumpPos}"
            self.totalEdge.add(path)
            # 如果跳转位置未被访问，则继续寻找
            if path not in visited:
                visited.add(path)
                newPath = currentPath.copy()
                newPath.append(jumpPos)
                self.findCallPathAndLoops(newPath, self.pos2BlockMap[jumpPos], visited)

        elif block.jumpType == BasicBlock.TERMINAL:
            # 处理终止执行
            pass

        elif block.jumpType == BasicBlock.CROSS:
            # 处理跨合约
            pass

    def detectBlockFeatures(self):
        block = self.pos2BlockMap.get(0)
        # 检测公共函数的位置
        while block.fallPos != -1:
            if block.instrList[0][1][0] == "JUMPDEST":
                break
            if block.conditionalJumpPos != -1 and block.conditionalJumpExpression.startswith("EQ"):
                # 找到以EQ开头的条件语句
                self.publicFunctionStartList.append(block.conditionalJumpPos)
            else:
                # 如果没有以EQ开头的条件语句，则fallbackPos = conditionalJumpPos
                self.fallbackPos = block.conditionalJumpPos
            block = self.pos2BlockMap.get(block.fallPos)

        if len(self.pos2BlockMap) <= 4 and "CALLVALUE" in self.pos2BlockMap.get(0).instrString:
            # 检查CALLVALUE是否在第一个基本块中，如果是，则将fallbackPos设置为0
            self.fallbackPos = 0

        # 检测fallback函数的位置
        self.findCallPathAndLoops([], self.pos2BlockMap.get(0), set())

        visitedInstr = 0
        totalInstr = 0
        for key, value in self.pos2BlockMap.items():
            tmp = value
            instrNum = len(tmp.instrList)
            if tmp.startBlockPos in self.visitBlock:
                # 如果startBlockPos在visitBlock中，则表示该基本块已被访问
                visitedInstr += instrNum
            totalInstr += instrNum
            # print(visitedInstr, totalInstr)

        # 计算代码覆盖率
        self.codeCoverage = float(visitedInstr) / totalInstr
        # 计算圈复杂度
        self.cyclomaticComplexity = len(self.totalEdge) - len(self.visitBlock) + 2
        # 统计指令数量
        self.numInstrs = len(self.disasm)
        # print("Start Detecting code smells")  # 开始检测代码异味
        # print('函数入口', self.publicFunctionStartList)

    # myTool:绘制CFG图
    def drawCFG(self):
        graph = Digraph("CFG", 'comment', None, None, 'png', None, "UTF-8",
                        {'rankdir': 'TB'},
                        {'color': 'black', 'fontcolor': 'black',
                         'style': 'rounded',
                         'shape': 'box'},
                        {'color': '#999999', 'fontcolor': '#888888', 'fontsize': '10', 'fontname': 'FangSong'}, None,
                        False)
        for key, value in self.pos2BlockMap.items():
            # value.infoPrint()
            if value.function != 'NULL':
                graph.node(str(value.startBlockPos), color='red')
            else:
                graph.node(str(value.startBlockPos))
            if value.fallPos != -1:
                graph.edge(str(value.startBlockPos), str(value.fallPos))
            if value.conditionalJumpPos != -1:
                graph.edge(str(value.startBlockPos), str(value.conditionalJumpPos))
            if value.unconditionalJumpPos != -1:
                graph.edge(str(value.startBlockPos), str(value.unconditionalJumpPos))
            if value.calledFunctionJumpPos != -1:
                graph.edge(str(value.startBlockPos), str(value.calledFunctionJumpPos))
            if value.terminalJumpPos != -1:
                graph.edge(str(value.startBlockPos), str(value.terminalJumpPos))
        # graph.view()
        graph.render('cfg', view=True)

    def MCFGConstruction(self):
        self.getDisasm()
        # 获取基本块
        self.getBasicBlock()
        # 添加顺序执行edges
        self.addFallEdges()
        # 构建 CFG（控制流图）
        functionPos = {}
        if self.disasmCode != '':
            functionPos = self.buildCFG(self.aimContractEndPos - 1, {})
        self.buildCFG(0, functionPos)
        # 检测代码块的特征
        self.detectBlockFeatures()
        # myTool:绘制cfg图
        self.drawCFG()
