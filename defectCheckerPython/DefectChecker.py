#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/15 10:29
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""

import re
from collections import deque

import Utils
from BasicBlock import BasicBlock


class DefectChecker:
    def __init__(self, binaryAnalyzer):
        self.hasUnchechedExternalCalls = False
        self.hasStrictBalanceEquality = False
        self.hasTransactionStateDependency = False
        self.hasBlockInfoDependency = False
        self.hasGreedyContract = False
        self.hasDoSUnderExternalInfluence = False
        self.hasNestCall = False
        self.hasReentrancy = False
        self.binaryAnalyzer = binaryAnalyzer

    def detectAllSmells(self):
        self.hasUnchechedExternalCalls = self.detectUnchechedExternalCalls()
        self.hasStrictBalanceEquality = self.detectStrictBalanceEquality()
        self.hasTransactionStateDependency = self.detectTransactionStateDependency()
        self.hasBlockInfoDependency = self.detectBlockInfoDependency()
        self.hasGreedyContract = self.detectGreedyContract()
        self.hasDoSUnderExternalInfluence = self.detectDoSUnderExternalInfluence()
        self.hasNestCall = self.detectNestCall()
        self.hasReentrancy = self.detectReentrancy()

    def detectUnchechedExternalCalls(self):
        if "CALL" not in self.binaryAnalyzer.allInstrs:
            return False
        res = False
        start = False
        callPC = ""
        for event in self.binaryAnalyzer.stackEvents:
            eventLog = event.split(" ==> ")[2]
            if eventLog.startswith("CALL_"):
                start = True
                callPC = eventLog.split(" ")[0]
                continue
            if start:
                # CALL instr does not checked by ISZERO
                if callPC not in eventLog:
                    res = True
                    break
                if eventLog.startswith("ISZERO_"):
                    top = eventLog.split(" ")[0]
                    # if CALL instr is checked by ISZERO, it means it's a legal CALL
                    if callPC in top:
                        callPC = ""
                        start = False
        return res

    def detectStrictBalanceEquality(self):
        if "BALANCE" not in self.binaryAnalyzer.allInstrs:
            return False
        res = False
        startBalance = False
        startEQ = False
        balancePC = ""
        eqPC = ""
        for event in self.binaryAnalyzer.stackEvents:
            eventLog = event.split(" ==> ")[2].split(" ")[0]
            if eventLog.startswith("BALANCE_"):
                startBalance = True
                balancePC = eventLog.split(" ")[0]
                continue
            if startBalance:
                if balancePC not in eventLog:
                    startBalance = False
                    startEQ = False
                    balancePC = ""
                    eqPC = ""
                    continue
                if startEQ:
                    if eqPC not in eventLog:
                        startBalance = False
                        startEQ = False
                        balancePC = ""
                        eqPC = ""
                        continue
                    if eventLog.startswith("ISZERO_"):
                        top = eventLog.split(" ")[0]
                        if eqPC in top:
                            res = True
                            break
                if eventLog.startswith("EQ_"):
                    startEQ = True
                    eqPC = eventLog.split(" ")[0]
        return res

    def detectTransactionStateDependency(self):
        if "ORIGIN" not in self.binaryAnalyzer.allInstrs:
            return False
        res = False
        start = False
        originPC = ""
        for event in self.binaryAnalyzer.stackEvents:
            eventLog = event.split(" ==> ")[2]
            if eventLog.startswith("ORIGIN_"):
                start = True
                originPC = eventLog.split(" ")[0]
                continue
            if start:
                if originPC not in eventLog:
                    start = False
                    originPC = ""
                    continue
                if eventLog.startswith("EQ_"):
                    top = eventLog.split(" ")[0]
                    if originPC in top:
                        res = True
                        break
        return res

    def detectBlockInfoDependency(self):
        blockInstr = ["BLOCKHASH", "COINBASE", "NUMBER", "DIFFICULTY", "GASLIMIT"]
        res = False
        for pos, block in self.binaryAnalyzer.pos2BlockMap.items():
            if len(block.conditionalJumpExpression) > 1:
                for instr in blockInstr:
                    if instr in block.conditionalJumpExpression:
                        res = True
                        break
        return res

    def isPayable(self, startPos):
        if startPos == -1:
            return False
        payable = True
        block = self.binaryAnalyzer.pos2BlockMap.get(startPos)
        fall = self.binaryAnalyzer.pos2BlockMap.get(block.fallPos)
        conditionalJumpExpression = block.conditionalJumpExpression
        if "CALLVALUE" in conditionalJumpExpression:
            if re.match(r"ISZERO_[0-9]+?\(CALLVALUE_[0-9]+?\)", conditionalJumpExpression):
                if fall.jumpType == BasicBlock.TERMINAL:
                    payable = False
        if conditionalJumpExpression == "" and block.jumpType == BasicBlock.TERMINAL:
            payable = False
        return payable

    def detectGreedyContract(self):
        if "SELFDESTRUCT" in self.binaryAnalyzer.allInstrs:
            return False
        payable = False
        can_sent_money = False
        if self.isPayable(self.binaryAnalyzer.fallbackPos):
            payable = True
        for pos in self.binaryAnalyzer.publicFunctionStartList:
            if self.isPayable(pos):
                payable = True
        for entry in self.binaryAnalyzer.pos2BlockMap.items():
            block = entry[1]
            # if block.moneyCall:
            if "CALL " in block.instrString:
                can_sent_money = True
        if payable and not can_sent_money:
            return True
        return False

    def detectDoSUnderExternalInfluence(self):
        for entry in self.binaryAnalyzer.pos2BlockMap.items():
            block = entry[1]
            if block.isCircle:
                if block.jumpType == BasicBlock.CONDITIONAL and block.moneyCall:
                    fall = self.binaryAnalyzer.pos2BlockMap.get(block.fallPos)
                    if fall.jumpType == BasicBlock.TERMINAL:
                        return True
        return False

    def detectNestCall(self):
        if "CALL" not in self.binaryAnalyzer.allInstrs:
            return False
        if "SLOAD" not in self.binaryAnalyzer.allInstrs:
            return False

        slotID = -1
        slotSizeLimit = False  # if do not limit slot size && have CALL ==> Nest Call
        hasCall = False

        for pos, block in self.binaryAnalyzer.pos2BlockMap.items():
            if block.isCircleStart:
                condition = block.conditionalJumpExpression
                if "SLOAD" not in condition:
                    continue

                slotID = Utils.getSlotID(condition)
                if slotID == -1:
                    continue

                # BFS-travel to circle body and detect whether a jumpCondition contains slotID.
                que = deque()
                visited = set()
                visited.add(block.startBlockPos)
                que.append(self.binaryAnalyzer.pos2BlockMap[block.conditionalJumpPos])
                que.append(self.binaryAnalyzer.pos2BlockMap[block.fallPos])

                while que:
                    topBlock = que.popleft()
                    if len(topBlock.conditionalJumpExpression) > 0:
                        if "SLOAD_" in topBlock.conditionalJumpExpression and (
                                "LT" in topBlock.conditionalJumpExpression or "GT" in topBlock.conditionalJumpExpression):
                            id = Utils.getSlotID(topBlock.conditionalJumpExpression)
                            if id == slotID:
                                tmp = topBlock.instrString.split(" ")
                                idx = 0
                                for idx in range(len(tmp)):
                                    if tmp[idx] == "SLOAD":
                                        break
                                if idx > 2:
                                    if tmp[idx - 1].startswith("DUP") and tmp[idx - 2].startswith("PUSH"):
                                        slotSizeLimit = True
                                        break

                        # if topBlock.instrString.toString().contains("CALL "):
                    if topBlock.moneyCall:
                        hasCall = True

                    if topBlock.jumpType == BasicBlock.CONDITIONAL:
                        if topBlock.conditionalJumpPos > 0:
                            child1 = self.binaryAnalyzer.pos2BlockMap[topBlock.conditionalJumpPos]
                            if child1.isCircle and child1.startBlockPos not in visited:
                                que.append(child1)
                            visited.add(child1.startBlockPos)

                        child2 = self.binaryAnalyzer.pos2BlockMap[topBlock.fallPos]
                        if child2.isCircle and child2.startBlockPos not in visited:
                            que.append(child2)
                        visited.add(child2.startBlockPos)

                    elif topBlock.jumpType == BasicBlock.UNCONDITIONAL:
                        if topBlock.unconditionalJumpPos > 0:
                            child = self.binaryAnalyzer.pos2BlockMap[topBlock.unconditionalJumpPos]
                            if child.isCircle and child.startBlockPos not in visited:
                                que.append(child)
                            visited.add(child.startBlockPos)

                    elif topBlock.jumpType == BasicBlock.FALL:
                        child = self.binaryAnalyzer.pos2BlockMap[topBlock.fallPos]
                        if child.isCircle and child.startBlockPos not in visited:
                            que.append(child)
                        visited.add(child.startBlockPos)

                if slotSizeLimit:
                    return False

        if hasCall:
            return True
        return False

    def detectReentrancy(self):
        # TODO: multiple CALL or SLOAD in one path
        # Currently, we can only detect one SLOAD, SSTORE, CALL in one path
        if "CALL" not in self.binaryAnalyzer.allInstrs:
            return False
        if "SLOAD" not in self.binaryAnalyzer.allInstrs:
            return False

        # Step 1: travel all paths and select paths with "CALL" instr
        # Step 2: obtain all path conditions on the selected paths
        # Step 3: if a condition contains "SLOAD", then obtain its address.
        # Step 4: detect whether the address is modified before the "CALL" instr.(SSTORE_PC && CALL_PC)
        # findCallPath([], self.binaryAnalyzer.pos2BlockMap[0], set())
        for path in self.binaryAnalyzer.allCallPath:
            address = ""
            callPC = -1
            sstorePC = -1
            sloadPC = -1
            gasLimited = False
            legalTransferAmount = True
            legalRange = []

            # get SLOAD address
            for blockID in path:
                block = self.binaryAnalyzer.pos2BlockMap[blockID]
                legalRange.append((block.startBlockPos, block.endBlockPos))
                if len(block.conditionalJumpExpression) > 1:
                    if "SLOAD" in block.conditionalJumpExpression:
                        address = Utils.getSlotAddress(block.conditionalJumpExpression)
                        for instr in block.instrList:
                            if instr[1][0] == "SLOAD":
                                sloadPC = instr[0]

            # this path does not read from storage ==> this path does not have reentrancy bug
            if sloadPC == -1:
                continue

            for i in range(len(self.binaryAnalyzer.stackEvents) - 1):
                eventLog = self.binaryAnalyzer.stackEvents[i].split(" ==> ")

                # get SSTORE PC
                if eventLog[0] == "SSTORE":
                    pc = int(eventLog[1])

                    # this SSTORE is in current range
                    if Utils.legalRange(pc, legalRange):
                        tmp = self.binaryAnalyzer.stackEvents[i - 1].split(" ==> ")
                        top = tmp[2].split(" ")[0]
                        if len(top) > 0:
                            top = re.sub(r"_[0-9]+", "", top)
                            # SSTORE read the same address with SLOAD, if sstorePC < CallPC ==> do not have reentrancy
                            if len(top) > 0 and top == address:
                                sstorePC = int(eventLog[1])

                if (eventLog[0] == "CALL"):
                    pc = int(eventLog[1])

                    # detect whether this CALL belongs to current path
                    if (Utils.legalRange(pc, legalRange)):
                        tmp = self.binaryAnalyzer.stackEvents[i - 1].split(" ==> ")
                        top = tmp[2].split(" ")[0]
                        if (len(top) > 0):
                            # detect gas limitation, if CALL is created by send or transfer, then it will limit gas to 2300
                            if ("2300_" in top):
                                gasLimited = True
                            elif (Utils.getType(top) == Utils.DIGITAL):
                                limitNum = int(top.split("_")[0])
                                if (limitNum <= 2300):
                                    gasLimited = True

                            else:
                                callPC = pc
                                gasLimited = False  # false is the default value

                        transfer_amount = tmp[2].split(" ")[2]
                        if (Utils.getType(transfer_amount) == Utils.DIGITAL):
                            amount = int(transfer_amount.split("_")[0])
                            if (amount == 0):
                                legalTransferAmount = False
                            else:
                                legalTransferAmount = True
                        else:
                            legalTransferAmount = True

            if (not gasLimited and (sstorePC == -1 or sstorePC > callPC) and (
                    callPC > sloadPC) and legalTransferAmount):
                return True

        return False

    def printAllDetectResult(self):
        res = ""
        res += "Uncheck External Calls: " + str(self.hasUnchechedExternalCalls) + "\n"
        res += "Strict Balance Equality: " + str(self.hasStrictBalanceEquality) + "\n"
        res += "Transaction State Dependency: " + str(self.hasTransactionStateDependency) + "\n"
        res += "Block Info Dependency: " + str(self.hasBlockInfoDependency) + "\n"
        res += "Greedy Contract: " + str(self.hasGreedyContract) + "\n"
        res += "DoS Under External Influence: " + str(self.hasDoSUnderExternalInfluence) + "\n"
        res += "Nest Call: " + str(self.hasNestCall) + "\n"
        res += "Reentrancy: " + str(self.hasReentrancy) + "\n"
        res += "Code Coverage:" + str(self.binaryAnalyzer.codeCoverage) + "\n"
        res += "Miss recognized Jump: " + str(self.binaryAnalyzer.misRecognizedJump) + "\n"
        res += "Cyclomatic Complexity: " + str(self.binaryAnalyzer.cyclomatic_complexity) + "\n"
        res += "Number of Instructions: " + str(self.binaryAnalyzer.numInster) + "\n"
        return res
