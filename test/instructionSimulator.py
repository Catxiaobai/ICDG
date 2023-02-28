#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/7 13:51
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import copy

import block
import re

evm_memory = []
evm_storage = []


def change_hex(n):
    a = int(n, 16)
    a = a + 1
    a = str(hex(a))
    if len(a) < 4:
        a = '0x0' + a[-1]
    return a


def cal(n):
    return int(n, 16)


def instruction_simulator():
    nodes = block.basic_block()
    edges = {}
    print(nodes)
    queue = ['0x00']
    # todo:如果不同基本块都跳转一个地点，会出现evm_stack丢失现象，未解决，如基本块3
    while len(queue) > 0:
        val = queue[0]
        queue.pop(0)
        content = nodes[val]['content']
        edge = []
        evm_stack = nodes[val]['stack']
        for c in content:
            c = c.split()
            if c[0] == 'PUSH' or re.match('PUSH[0-9]+', c[0]):
                evm_stack.append(c[1])
            elif c[0] == 'MSTORE':
                evm_stack.pop()
                evm_stack.pop()
            elif c[0] == 'SSTORE':
                evm_stack.pop()
                evm_stack.pop()
            elif c[0] == 'SLOAD':
                evm_stack.pop()
                # evm_stack.append('1')
            elif c[0] == 'MLOAD':
                evm_stack.pop()
                # evm_stack.append('1')
            elif c[0] in ['CALLDATASIZE', 'CALLDATALOAD', 'CALLVALUE']:
                evm_stack.append('0x01')
            elif c[0] in ['LT', 'GT', 'SLT', 'SGT', 'EQ']:
                evm_stack.pop()
                evm_stack.pop()
                evm_stack.append(0)
            elif c[0] == 'ISZERO':
                evm_stack.pop()
                evm_stack.append(1)
            elif c[0] in ['DIV', 'SDIV']:
                a = cal(evm_stack.pop())
                b = cal(evm_stack.pop())
                evm_stack.append(str(hex(int(b / a))))
            elif c[0] in ['ADD']:
                a = cal(evm_stack.pop())
                b = cal(evm_stack.pop())
                evm_stack.append(str(hex(a + b)))
            elif c[0] in ['MUL']:
                a = cal(evm_stack.pop())
                b = cal(evm_stack.pop())
                evm_stack.append(str(hex(a * b)))
            elif c[0] in ['SUB']:
                a = cal(evm_stack.pop())
                b = cal(evm_stack.pop())
                evm_stack.append(str(hex(a - b)))
            elif c[0] in ['AND']:
                a = cal(evm_stack.pop())
                b = cal(evm_stack.pop())
                evm_stack.append(str(hex(a & b)))
            elif c[0] in ['OR']:
                a = cal(evm_stack.pop())
                b = cal(evm_stack.pop())
                evm_stack.append(str(hex(a | b)))
            elif c[0] in ['XOR']:
                a = cal(evm_stack.pop())
                b = cal(evm_stack.pop())
                evm_stack.append(str(hex(a ^ b)))
            elif c[0] in ['NOT']:
                a = cal(evm_stack.pop())
                evm_stack.append(str(hex(~a)))
            elif re.match('DUP[0-9]+', c[0]):
                # 复制栈顶第n个元素到栈顶
                length = eval(c[0].split('DUP')[-1])
                evm_stack.append(evm_stack[-length])
            elif re.match('SWAP[0-9]+', c[0]):
                # 交换栈顶第n个元素和栈顶
                length = eval(c[0].split('SWAP')[-1]) + 1
                temp = evm_stack[-1]
                evm_stack[-1] = evm_stack[-length]
                evm_stack[-length] = temp
            elif c[0] == 'POP':
                evm_stack.pop()
            elif c[0] == 'REVERT':
                pass
            elif c[0] == 'JUMP':
                jump_aim = evm_stack[-1]
                evm_stack.pop()
                edge.append(nodes[jump_aim]['id'])
                nodes[jump_aim]['stack'] = copy.deepcopy(evm_stack)
                edges.update({nodes[val]['id']: edge})
                if jump_aim not in queue:
                    queue.append(jump_aim)
                # print(edges)
            elif c[0] == 'JUMPI':
                jump_aim = evm_stack[-1]
                evm_stack.pop()
                evm_stack.pop()
                edge.append(nodes[val]['id'] + 1)
                edge.append(nodes[jump_aim]['id'])
                nodes[change_hex(nodes[val]['end'])]['stack'] = copy.deepcopy(evm_stack)
                nodes[jump_aim]['stack'] = copy.deepcopy(evm_stack)
                edges.update({nodes[val]['id']: edge})
                if jump_aim not in queue:
                    queue.append(jump_aim)
                if change_hex(nodes[val]['end']) not in queue:
                    queue.append(change_hex(nodes[val]['end']))
                # print(edges)
            elif c[0] == 'RETURN':
                pass
            elif c[0] == 'STOP':
                pass
            elif c[0] == 'INVALID':
                pass
            elif c[0] in ['JUMPDEST']:
                pass
            else:
                print(c[0])
    print(edges)


if __name__ == '__main__':
    instruction_simulator()
