#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/21 16:35
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
# ! /usr/bin/python3
# -*-coding:utf-8-*-

""" 
@Time: 2023/2/15 10:29
@Author : mengjie-1998@qq.com
@Remark: 定义了一个BasicBlock类，用于表示EVM程序的基本块（basic block），即在CFG中不会被分割的最小代码块。
         该类中包含了基本块的一些属性和方法，主要涉及指令、EVM栈和跳转等方面的操作。
"""


class BasicBlock:
    # 定义一些表示跳转类型的类常量
    CONDITIONAL = 1  # 有条件跳转
    UNCONDITIONAL = 2  # 无条件跳转
    FALL = 3  # 顺序执行
    TERMINAL = 4  # 终止执行
    CROSS = 5  # 跨合约跳转

    def __init__(self):
        # 初始化一些变量
        self.startBlockPos = -1  # 当前基本块在程序中的起始位置
        self.endBlockPos = -1  # 当前基本块在程序中的结束位置
        self.instrList = []  # 存储当前基本块中的指令
        self.evmStack = []  # 存储当前基本块中的EVM栈
        self.instrString = ''  # 当前基本块的指令字符串

        # 下面是关于跳转的一些变量
        self.jumpType = 3  # 跳转类型，1表示有条件跳转，2表示无条件跳转，3表示顺序执行，4表示终止执行，5表示跨合约调用跳转
        self.fallPos = -1  # 当前基本块执行完后跳转的位置
        self.conditionalJumpPos = -1  # 有条件跳转的目标位置
        self.conditionalJumpExpression = ""  # 有条件跳转的条件表达式
        self.unconditionalJumpPos = -1  # 无条件跳转的目标位置

        self.isCircle = False  # 是否形成了循环
        self.isCircleStart = False  # 是否是循环的起点
        self.moneyCall = False  # 是否调用了合约中的send或transfer方法

        # 关于call跨合约调用相关
        self.function = "NULL"  # 标记该基本块属于哪个函数入口
        self.callJumpPos = -1  # 跨合约跳转起始位置
        self.calledFunctionJumpPos = -1  # 被调用合约目标函数位置
        self.terminalJumpPos = -1  # 结束块跳转位置
        self.isEndBlock = False  # 是否是结束块
        self.isCalledContract = False  # 是否为被调用合约
        self.isCallFunction = False  # 被调用函数

        # 添加前缀节点块，便于前向搜索
        self.prefixBlock = set()

    # 输出基本块信息
    def infoPrint(self):
        print('--------------------------基本块: ', self.startBlockPos)
        for attr in self.__dict__:
            print(self.__dict__[attr])
