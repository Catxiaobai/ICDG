#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/22 11:53
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import re

from BasicBlock import BasicBlock
import utils


def printStack(instr, current_PC, evmStack):
    # 将堆栈中的元素用空格隔开
    res = " ".join(evmStack)
    if len(res) == 0:
        res = "NULL"
    # 打印指令、当前PC和堆栈
    return f"{instr} ==> {current_PC} ==> {res}"


class EvmSimulator:
    LOOP_LIMITED = 3  # 边访问限制的次数，即最多访问三次

    def __init__(self, pos2BlockMap, first, functionPos):
        """
        EVMSimulator类的构造函数，创建一个以字节码为输入的模拟器对象
        :param pos2BlockMap: 字节码与基本块之间的映射表
        """
        self.edgeVisTimes = {}  # 记录每条边被访问的次数
        self.pos2BlockMap = pos2BlockMap  # 字节码与基本块之间的映射表
        self.stackEvents = []  # 模拟栈事件的列表
        self.versionGap = False  # 是否存在版本差异
        self.misRecognizedJump = False  # 是否存在错误的跳转
        self.functionPosMap = {}  # 记录函数的起始块
        self.functionPosMap.update(functionPos)
        start = self.pos2BlockMap[first]  # 获取第一个基本块
        self.dfsExeBlock(start, start.evmStack.copy())  # 从第一个基本块开始DFS执行

    def dfsExeBlock(self, block, fatherEvmStack):
        # 用父堆栈复制新堆栈
        block.evmStack = fatherEvmStack.copy()
        # 遍历区块中的每个指令，执行指令
        for instr in block.instrList:
            self.exeInstr(block, instr, block.evmStack)

        # 处理不同类型的跳转
        if block.jumpType == BasicBlock.CONDITIONAL:  # 条件跳转
            left_branch = block.conditionalJumpPos  # 左分支跳转位置
            if left_branch == -1:  # 如果左分支跳转位置无效
                return
            # 添加前缀节点
            self.pos2BlockMap[left_branch].prefixBlock.add(block.startBlockPos)
            # 标记已访问过的边，递归执行左分支区块
            if self.flagVisEdge(block.startBlockPos, left_branch):
                self.dfsExeBlock(self.pos2BlockMap.get(left_branch), block.evmStack)

            right_branch = block.fallPos  # 右分支跳转位置
            # 添加前缀节点
            self.pos2BlockMap[right_branch].prefixBlock.add(block.startBlockPos)
            # 标记已访问过的边，递归执行右分支区块
            if self.flagVisEdge(block.startBlockPos, right_branch):
                self.dfsExeBlock(self.pos2BlockMap.get(right_branch), block.evmStack)

        elif block.jumpType == BasicBlock.UNCONDITIONAL:  # 无条件跳转
            jumpPos = block.unconditionalJumpPos  # 跳转位置
            if jumpPos == -1:  # 如果跳转位置无效
                return
            # 添加前缀节点
            self.pos2BlockMap[jumpPos].prefixBlock.add(block.startBlockPos)
            # 标记已访问过的边，递归执行跳转位置指向的区块
            if self.flagVisEdge(block.startBlockPos, jumpPos):
                self.dfsExeBlock(self.pos2BlockMap.get(jumpPos), block.evmStack)

        elif block.jumpType == BasicBlock.FALL:  # 跳转到块末尾
            jumpPos = block.fallPos  # 跳转位置
            # 添加前缀节点
            self.pos2BlockMap[jumpPos].prefixBlock.add(block.startBlockPos)
            # 标记已访问过的边，递归执行跳转位置指向的区块
            if self.flagVisEdge(block.startBlockPos, jumpPos):
                self.dfsExeBlock(self.pos2BlockMap.get(jumpPos), block.evmStack)

        # 增加块终止和跨合约跳转
        elif block.jumpType == BasicBlock.TERMINAL:  # 块终止
            if self.pos2BlockMap[block.terminalJumpPos].isCallFunction:
                self.pos2BlockMap[block.startBlockPos].isCallFunction = True

        elif block.jumpType == BasicBlock.CROSS:
            left_branch = block.calledFunctionJumpPos  # 左分支跳转位置
            if left_branch != -1:  # 如果左分支跳转位置无效
                # 添加前缀节点
                self.pos2BlockMap[left_branch].prefixBlock.add(block.startBlockPos)
            # 标记已访问过的边，递归执行左分支区块
            if left_branch != -1 and self.flagVisEdge(block.startBlockPos, left_branch):
                self.dfsExeBlock(self.pos2BlockMap.get(left_branch), block.evmStack)

            right_branch = block.fallPos  # 右分支跳转位置
            # 添加前缀节点
            self.pos2BlockMap[right_branch].prefixBlock.add(block.startBlockPos)
            # 标记已访问过的边，递归执行右分支区块
            if self.flagVisEdge(block.startBlockPos, right_branch):
                self.dfsExeBlock(self.pos2BlockMap.get(right_branch), block.evmStack)

    def flagVisEdge(self, currentBlockID, jumpPos):
        """
        标记访问的边，并返回边是否可以继续访问
        :param currentBlockID: 当前基本块的ID
        :param jumpPos: 跳转的位置
        :return: 返回True表示可以访问该边，返回False表示不能访问该边
        """
        edgeVis = f"{currentBlockID}_{jumpPos}"  # 构造边的访问标记
        visTimes = self.edgeVisTimes.get(edgeVis, 0)  # 获取边的访问次数
        if visTimes == EvmSimulator.LOOP_LIMITED:  # 如果边的访问次数达到上限，则不能再访问
            return False
        visTimes += 1  # 增加边的访问次数
        self.edgeVisTimes[edgeVis] = visTimes  # 更新边的访问次数记录
        return True  # 返回True表示可以访问该边

    def exeInstr(self, currentBlock, instr_pair, evmStack):
        # 获取当前块的ID，指令和指令位置
        currentBlockID = currentBlock.startBlockPos
        instr = instr_pair[1][0]
        current_PC = instr_pair[0]
        legalInstr = True
        # 每条指令以 "指令名_指令位置" 的格式压入EVM栈中
        if instr == "JUMP":
            if len(evmStack) >= 1:
                # 获取跳转位置
                address = evmStack.pop()
                legalJump = False
                # 判断跳转位置是否合法
                if utils.getType(address) == utils.DIGITAL:
                    jumpPos = int(address.split("_")[0])
                    if currentBlock.isCalledContract:
                        jumpPos += currentBlock.callJumpPos

                    # 如果跳转位置是0或者不在pos2BlockMap中，则跳转不合法
                    if jumpPos == 0 or jumpPos not in self.pos2BlockMap:
                        self.pos2BlockMap[currentBlockID].unconditionalJumpPos = -1
                        legalJump = True
                        self.versionGap = True
                    # 如果跳转位置是一个JUMPDEST，则跳转合法
                    elif self.pos2BlockMap[jumpPos].instrList[0][1][0] == "JUMPDEST":
                        self.pos2BlockMap[currentBlockID].unconditionalJumpPos = jumpPos
                        legalJump = True
                        # 将jumpPos标记为被调用函数
                        if self.pos2BlockMap[currentBlockID].isCallFunction:
                            self.pos2BlockMap[jumpPos].isCallFunction = True

                # 跳转不合法，打印错误信息
                if not legalJump:
                    print(f"Cannot Recognize Jump Pos \"{address}\" on PC: {current_PC}")
                    self.misRecognizedJump = True
            # EVM栈为空，跳转不合法
            else:
                legalInstr = False

        elif instr == "JUMPI":
            # 判断栈内是否有两个元素
            if len(evmStack) >= 2:
                # 从栈顶依次弹出两个元素
                address = evmStack.pop()
                condition = evmStack.pop()
                legalJump = False
                # print('jumpiAddress: ', address)
                # 判断地址是否是数字
                if utils.getType(address) == utils.DIGITAL:
                    # 解析跳转位置
                    jumpPos = int(address.split("_")[0])
                    if currentBlock.isCalledContract:
                        jumpPos += currentBlock.callJumpPos
                    if jumpPos == 0 or jumpPos not in self.pos2BlockMap:
                        # 设置当前块的有条件跳转位置和条件表达式
                        self.versionGap = True
                        self.pos2BlockMap[currentBlockID].conditionalJumpPos = -1
                        legalJump = True
                        self.pos2BlockMap[currentBlockID].conditionalJumpExpression = condition
                    elif self.pos2BlockMap[jumpPos].instrList[0][1][0] == "JUMPDEST":
                        # 设置当前块的有条件跳转位置和条件表达式
                        self.pos2BlockMap[currentBlockID].conditionalJumpPos = jumpPos
                        self.pos2BlockMap[currentBlockID].conditionalJumpExpression = condition
                        legalJump = True
                        if condition.startswith("EQ"):
                            if re.split('[(_,)]', condition)[2].isdigit():
                                self.pos2BlockMap[jumpPos].function = re.split('[(_,)]', condition)[2]
                            else:
                                self.pos2BlockMap[jumpPos].function = re.split('[(_,)]', condition)[-3]
                            if currentBlock.isCalledContract:
                                if re.split('[(_,)]', condition)[2].isdigit():
                                    self.functionPosMap.update({re.split('[(_,)]', condition)[2]: jumpPos})
                                else:
                                    self.functionPosMap.update({re.split('[(_,)]', condition)[-3]: jumpPos})
                                # print(re.split('[(_,)]', condition))
                        # 将jumpPos标记为被调用函数
                        if self.pos2BlockMap[currentBlockID].isCallFunction:
                            self.pos2BlockMap[jumpPos].isCallFunction = True

                if not legalJump:
                    # 未能解析出跳转地址，报错
                    print(f"Error JUMPI on: {current_PC}")
                    self.misRecognizedJump = True
            else:
                legalInstr = False

        elif instr in {'CALL', 'DELEGATECALL', 'CALLCODE', 'STATICCALL'}:
            if len(evmStack) >= 7:
                outgas = evmStack.pop()
                recipient = evmStack.pop()
                transfer_amount = evmStack.pop()
                start_data_input = evmStack.pop()
                size_data_input = evmStack.pop()
                start_data_output = evmStack.pop()
                size_data_ouput = evmStack.pop()
                currentBlock.moneyCall = True

                if utils.getType(transfer_amount) == utils.DIGITAL:
                    amount = int(transfer_amount.split("_")[0])
                    if amount == 0:
                        # 调用
                        currentBlock.moneyCall = False
                        legalJump = False
                        aim = evmStack[-2]

                        jumpPos = int(self.functionPosMap[aim.split('_')[0]])
                        # 如果跳转位置是0或者不在pos2BlockMap中，则跳转不合法
                        if jumpPos == 0 or jumpPos not in self.pos2BlockMap:
                            self.pos2BlockMap[currentBlockID].calledFunctionJumpPos = -1
                            legalJump = True
                            self.versionGap = True
                        # 如果跳转位置是一个JUMPDEST，则跳转合法
                        elif self.pos2BlockMap[jumpPos].instrList[0][1][0] == "JUMPDEST":
                            self.pos2BlockMap[currentBlockID].calledFunctionJumpPos = jumpPos
                            legalJump = True
                            # 将jumpPos标记为被调用函数
                            self.pos2BlockMap[jumpPos].isCallFunction = True
                        if not legalJump:
                            # 未能解析出跳转地址，报错
                            print(f"Error CALL on: {current_PC}")
                            self.misRecognizedJump = True

                        # 标记调用返回边
                        self.pos2BlockMap[self.functionPosMap['STOP']].calledFunctionJumpPos = self.pos2BlockMap[
                            currentBlockID].fallPos
                        self.pos2BlockMap[self.functionPosMap['STOP']].isCallFunction = True
                else:
                    # 转账
                    pass
                result = instr + "_" + str(current_PC)
                evmStack.append(result)
            else:
                legalInstr = False
        elif instr == "STOP":
            # STOP 指令，不做任何操作
            pass

        elif instr == "ADD":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    # 如果弹出的两个操作数都是数字类型，则将其相加，并将结果重新压入栈中
                    res = int(first.split("_")[0]) + int(second.split("_")[0])
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    # 否则，将操作转为字符串，作为新元素压入栈中
                    res = "ADD_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                # 如果栈中元素不足，则标记为非法指令
                legalInstr = False

        elif instr == "MUL":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    # 如果弹出的两个操作数都是数字类型，则将其相乘，并将结果重新压入栈中
                    res = int(first.split("_")[0]) * int(second.split("_")[0])
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    # 否则，将操作转为字符串，作为新元素压入栈中
                    res = "MUL_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                # 如果栈中元素不足，则标记为非法指令
                legalInstr = False

        elif instr == "SUB":
            if len(evmStack) >= 2:
                first = evmStack.pop()  # 取出栈顶的第一个操作数
                second = evmStack.pop()  # 取出栈顶的第二个操作数
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    # 如果两个操作数都是数字，则执行减法运算
                    res = int(first.split("_")[0]) - int(second.split("_")[0])
                    evmStack.append(str(res) + "_" + str(current_PC))  # 将运算结果入栈
                else:
                    # 如果两个操作数不都是数字，则将操作表达式入栈
                    res = "SUB_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "DIV":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    # 如果两个操作数都是数字，则执行除法运算
                    if int(second.split("_")[0]) == 0:  # 判断除数是否为0
                        res = 0
                    else:
                        res = int(int(first.split("_")[0]) / int(second.split("_")[0]))
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    # 如果两个操作数不都是数字，则将操作表达式入栈
                    res = "DIV_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "SDIV":
            if len(evmStack) >= 2:  # 检查栈中是否有足够的元素
                first = evmStack.pop()  # 弹出栈顶元素
                second = evmStack.pop()  # 弹出次顶元素
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:  # 检查元素是否为数字
                    if int(second.split("_")[0]) == 0:  # 避免除数为0
                        res = 0
                    else:
                        tmp = 1
                        if int(int(first.split("_")[0]) / int(second.split("_")[0])) < 0:  # 如果结果是负数，标记负号并对其进行取绝对值操作
                            tmp = -1
                        res = tmp * abs(int(int(first.split("_")[0]) / int(second.split("_")[0])))  # 进行有符号整数除法
                    evmStack.append(str(res) + "_" + str(current_PC))  # 将结果压入栈中
                else:  # 如果元素不是数字，则创建一个新的字符串来表示操作
                    res = "SDIV_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False  # 如果没有足够的元素，则该指令非法

        elif instr == "MOD":
            if len(evmStack) >= 2:  # 检查栈中是否有足够的元素
                first = evmStack.pop()  # 弹出栈顶元素
                second = evmStack.pop()  # 弹出次顶元素
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:  # 检查元素是否为数字
                    if int(second.split("_")[0]) == 0:  # 避免除数为0
                        res = 0
                    else:
                        res = int(first.split("_")[0]) % int(second.split("_")[0])  # 求模操作
                    evmStack.append(str(res) + "_" + str(current_PC))  # 将结果压入栈中
                else:  # 如果元素不是数字，则创建一个新的字符串来表示操作
                    res = "MOD_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False  # 如果没有足够的元素，则该指令非法

        elif instr == "SMOD":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    if int(second.split("_")[0]) == 0:
                        res = 0
                    else:
                        res = int(first.split("_")[0]) % int(second.split("_")[0])
                        if res * int(first.split("_")[0]) < 0:
                            res *= -1
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "SMOD_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "ADDMOD":
            if len(evmStack) >= 3:
                first = evmStack.pop()
                second = evmStack.pop()
                third = evmStack.pop()
                if (utils.getType(first) == utils.DIGITAL and
                        utils.getType(second) == utils.DIGITAL and
                        utils.getType(third) == utils.DIGITAL):
                    if int(third.split("_")[0]) == 0:
                        res = 0
                    else:
                        res = (int(first.split("_")[0]) + int(second.split("_")[0])) % int(third.split("_")[0])
                    evmStack.append(f"{res}_{current_PC}")
                else:
                    res = f"ADDMOD_{current_PC}({first},{second})"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "MULMOD":
            if len(evmStack) >= 3:
                first = evmStack.pop()
                second = evmStack.pop()
                third = evmStack.pop()
                if (utils.getType(first) == utils.DIGITAL and
                        utils.getType(second) == utils.DIGITAL and
                        utils.getType(third) == utils.DIGITAL):
                    res = (int(first.split("_")[0]) * int(second.split("_")[0])) % int(third.split("_")[0])
                    evmStack.append(f"{res}_{current_PC}")
                else:
                    res = f"MULMOD_{current_PC}({first},{second})"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "EXP":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    res = int(pow(int(first.split("_")[0]), int(second.split("_")[0])))
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "EXP_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "SIGNEXTEND":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    f = int(first.split("_")[0])
                    s = int(second.split("_")[0])
                    if f >= 32 or f < 0:
                        res = s
                    else:
                        tmp = 8 * f + 7
                        if (s & (1 << tmp)) == 1:
                            res = s | (int(pow(2, 256)) - (1 << tmp))
                        else:
                            res = s & ((1 << tmp) - 1)
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "SIGNEXTEND_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "LT" or instr == "SLT":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    if int(first.split("_")[0]) < int(second.split("_")[0]):
                        evmStack.append("1_" + str(current_PC))
                    else:
                        evmStack.append("0_" + str(current_PC))
                else:
                    res = "LT_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "GT" or instr == "SGT":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    if int(first.split("_")[0]) > int(second.split("_")[0]):
                        evmStack.append("1_" + str(current_PC))
                    else:
                        evmStack.append("0_" + str(current_PC))
                else:
                    res = "GT_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "EQ":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    if int(first.split("_")[0]) == int(second.split("_")[0]):
                        evmStack.append("1_" + str(current_PC))
                    else:
                        evmStack.append("0_" + str(current_PC))
                else:
                    if first.split("_")[0] == second.split("_")[0]:
                        evmStack.append("1_" + str(current_PC))
                    else:
                        res = "EQ_" + str(current_PC) + "(" + first + "," + second + ")"
                        evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "ISZERO":
            if len(evmStack) >= 1:
                first = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL:
                    if int(first.split("_")[0]) == 0:
                        evmStack.append("1_" + str(current_PC))
                    else:
                        evmStack.append("0_" + str(current_PC))
                else:
                    res = "ISZERO_" + str(current_PC) + "(" + first + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "AND":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    res = int(first.split("_")[0]) & int(second.split("_")[0])
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "AND_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "OR":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    res = int(first.split("_")[0]) | int(second.split("_")[0])
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "OR_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "XOR":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    res = int(first.split("_")[0]) ^ int(second.split("_")[0])
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "XOR_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "NOT":
            if len(evmStack) >= 1:
                first = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL:
                    res = ~int(first.split("_")[0])
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "NOT_" + str(current_PC) + "(" + first + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "BYTE":
            if len(evmStack) >= 2:
                first = evmStack.pop()
                second = evmStack.pop()
                if utils.getType(first) == utils.DIGITAL and utils.getType(second) == utils.DIGITAL:
                    f = int(first.split("_")[0])
                    s = int(second.split("_")[0])
                    byte_idx = 32 - f - 1
                    if f >= 32 or f < 0:
                        res = 0
                    else:
                        res = s & (255 << (8 * byte_idx))
                        res = res >> (8 * byte_idx)
                    evmStack.append(str(res) + "_" + str(current_PC))
                else:
                    res = "BYTE_" + str(current_PC) + "(" + first + "," + second + ")"
                    evmStack.append(res)
            else:
                legalInstr = False

        elif instr == "SHA3":
            if len(evmStack) >= 2:
                top1 = evmStack.pop()
                top2 = evmStack.pop()
                result = "SHA3_" + str(current_PC) + "(" + top1 + "," + top2 + ")"
                evmStack.append(result)
            else:
                legalInstr = False

        elif instr == "ADDRESS":
            result = "ADDRESS_" + str(current_PC)
            evmStack.append(result)

        elif instr == "BALANCE":
            if len(evmStack) >= 1:
                top1 = evmStack.pop()
                result = "BALANCE_" + str(current_PC) + "(" + top1 + ")"
                evmStack.append(result)
            else:
                legalInstr = False

        elif instr == "ORIGIN":
            result = "ORIGIN_" + str(current_PC)
            evmStack.append(result)

        elif instr == "CALLER":
            result = "CALLER_" + str(current_PC)
            evmStack.append(result)

        elif instr == "CALLVALUE":
            result = "CALLVALUE_" + str(current_PC)
            evmStack.append(result)

        elif instr == "CALLDATALOAD":
            if len(evmStack) >= 1:
                top1 = evmStack.pop()
                result = f"CALLDATALOAD_{current_PC}({top1})"
                evmStack.append(result)
            else:
                legalInstr = False

        elif instr == "CALLDATASIZE":
            result = f"CALLDATASIZE_{current_PC}"
            evmStack.append(result)

        elif instr == "CALLDATACOPY":
            if len(evmStack) >= 3:
                evmStack.pop()
                evmStack.pop()
                evmStack.pop()
            else:
                legalInstr = False

        elif instr == "CODESIZE":
            result = f"CODESIZE_{current_PC}"
            evmStack.append(result)

        elif instr == "CODECOPY":
            if len(evmStack) >= 3:
                evmStack.pop()
                evmStack.pop()
                evmStack.pop()
            else:
                legalInstr = False

        elif instr == "GASPRICE":
            result = "GASPRICE_" + str(current_PC)
            evmStack.append(result)

        elif instr == "EXTCODESIZE":
            if len(evmStack) >= 1:
                top1 = evmStack.pop()
                result = "EXTCODESIZE_" + str(current_PC) + "(" + top1 + ")"
                evmStack.append(result)
            else:
                legalInstr = False

        elif instr == "EXTCODECOPY":
            if len(evmStack) >= 4:
                evmStack.pop()
                evmStack.pop()
                evmStack.pop()
                evmStack.pop()
            else:
                legalInstr = False

        elif instr == "RETURNDATASIZE":
            result = "RETURNDATASIZE_" + str(current_PC)
            evmStack.append(result)

        elif instr == "RETURNDATACOPY":
            if len(evmStack) >= 3:
                evmStack.pop()
                evmStack.pop()
                evmStack.pop()
            else:
                legalInstr = False

        elif instr == "BLOCKHASH":
            if len(evmStack) >= 1:
                top1 = evmStack.pop()
                result = f"BLOCKHASH_{current_PC}({top1})"
                evmStack.append(result)
            else:
                legalInstr = False

        elif instr == "COINBASE":
            result = f"COINBASE_{current_PC}"
            evmStack.append(result)

        elif instr == "TIMESTAMP":
            result = f"TIMESTAMP_{current_PC}"
            evmStack.append(result)

        elif instr == "NUMBER":
            result = f"NUMBER_{current_PC}"
            evmStack.append(result)

        elif instr == "DIFFICULTY":
            result = f"DIFFICULTY_{current_PC}"
            evmStack.append(result)

        elif instr == "GASLIMIT":
            result = f"GASLIMIT_{current_PC}"
            evmStack.append(result)

        elif instr == "POP":
            if len(evmStack) >= 1:
                evmStack.pop()
            else:
                legalInstr = False

        elif instr == "MLOAD":
            if len(evmStack) >= 1:
                address = evmStack.pop()
                result = "MLOAD_" + str(current_PC) + "(" + address + ")"
                evmStack.append(result)
            else:
                legalInstr = False

        elif instr == "MSTORE" or instr == "MSTORE8":
            if len(evmStack) >= 2:
                evmStack.pop()
                evmStack.pop()
            else:
                legalInstr = False

        elif instr == "SSTORE":
            if len(evmStack) >= 2:
                evmStack.pop()
                evmStack.pop()
            else:
                legalInstr = False

        elif instr == "SLOAD":
            if len(evmStack) >= 1:
                top1 = evmStack.pop()
                result = "SLOAD_" + str(current_PC) + "(" + top1 + ")"
                evmStack.append(result)
            else:
                legalInstr = False

        elif instr == "PC":
            result = "PC_" + str(current_PC)
            evmStack.append(result)

        elif instr == "MSIZE":
            result = "MSIZE_" + str(current_PC)
            evmStack.append(result)

        elif instr == "GAS":
            result = "GAS_" + str(current_PC)
            evmStack.append(result)

        elif instr == "JUMPDEST":
            pass

        elif instr.startswith("PUSH"):
            pushedValue = instr_pair[1][1]
            if pushedValue.startswith("0"):
                pushedValue = pushedValue.replace("0+", "", 1)
            if len(pushedValue) == 0:
                pushedValue = "0"
            if len(pushedValue) <= 10:
                pushvalue = int(pushedValue, 16)
                evmStack.append(str(pushvalue) + "_" + str(current_PC))
            else:
                evmStack.append(instr + "_" + str(current_PC))

        elif instr.startswith("DUP"):
            dp = int(instr.replace("DUP", ""))
            if len(evmStack) >= dp:
                tmp = []
                for i in range(dp):
                    tmp.append(evmStack.pop())
                dup_value = tmp[dp - 1]
                for i in range(dp - 1, -1, -1):
                    evmStack.append(tmp[i])
                evmStack.append(str(dup_value))
            else:
                legalInstr = False

        elif instr.startswith("SWAP"):
            sp = int(instr.replace("SWAP", ""))
            if len(evmStack) > sp:
                tmp = []
                for i in range(sp + 1):
                    tmp.append(evmStack.pop())
                evmStack.append(tmp[0])
                for i in range(len(tmp) - 2, 0, -1):
                    evmStack.append(tmp[i])
                evmStack.append(tmp[-1])
            else:
                legalInstr = False

        elif instr.startswith("LOG"):
            lp = int(instr.replace("LOG", ""))
            if len(evmStack) >= lp + 2:
                for i in range(lp + 2):
                    evmStack.pop()
            else:
                legalInstr = False

        elif instr == "CREATE":
            if len(evmStack) >= 3:
                evmStack.pop()
                evmStack.pop()
                evmStack.pop()
                result = "CREATE_" + str(current_PC)
                evmStack.append(result)
            else:
                legalInstr = False

        # elif instr == "CALL":
        #     if len(evmStack) >= 7:
        #         outgas = evmStack.pop()
        #         recipient = evmStack.pop()
        #         transfer_amount = evmStack.pop()
        #         start_data_input = evmStack.pop()
        #         size_data_input = evmStack.pop()
        #         start_data_output = evmStack.pop()
        #         size_data_ouput = evmStack.pop()
        #         result = "CALL_" + str(current_PC)
        #         evmStack.append(result)
        #         currentBlock.moneyCall = True
        #         if utils.getType(transfer_amount) == utils.DIGITAL:
        #             amount = int(transfer_amount.split("_")[0])
        #             if amount == 0:
        #                 currentBlock.moneyCall = False
        #     else:
        #         legalInstr = False

        # elif instr == "CALLCODE":
        #     if len(evmStack) >= 7:
        #         for i in range(7):
        #             evmStack.pop()
        #         result = "CALLCODE_" + str(current_PC)
        #         evmStack.append(result)
        #     else:
        #         legalInstr = False

        elif instr == "RETURN" or instr == "REVERT":
            if len(evmStack) >= 2:
                evmStack.pop()
                evmStack.pop()
            else:
                legalInstr = False
            if currentBlock.isCalledContract:
                self.functionPosMap.update({'STOP': currentBlock.terminalJumpPos})

        # elif instr == "DELEGATECALL":
        #     if len(evmStack) >= 6:
        #         for i in range(6):
        #             evmStack.pop()
        #         result = "DELEGATECALL_" + str(current_PC)
        #         evmStack.append(result)
        #     else:
        #         legalInstr = False

        # elif instr == "STATICCALL":
        #     if len(evmStack) >= 6:
        #         for i in range(6):
        #             evmStack.pop()
        #         result = "STATICCALL_" + str(current_PC)
        #         evmStack.append(result)
        #     else:
        #         legalInstr = False

        elif instr == "SELFDESTRUCT" or instr == "REVERT":
            if len(evmStack) >= 1:
                evmStack.pop()
                return
            else:
                legalInstr = False

        elif instr == "INVALID" or instr == "ASSERTFAIL":
            pass

        else:
            print("Cannot recognize instr: " + instr)

        if not legalInstr:
            print("Error with instr: " + instr + " - " + str(current_PC))

        self.stackEvents.append(printStack(instr, current_PC, evmStack))
