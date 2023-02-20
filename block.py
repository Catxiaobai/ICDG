#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/7 11:29
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""


def basic_block():
    nodes = {}
    content = []
    nodeId = 1
    aim = 1
    with open('test.txt', 'r') as f:
        for loc, line in enumerate(f):
            if len(line.split(':')) < 2:
                continue
            line = line.strip()
            node = {}
            address = line.split(': ')[0]
            address = address.lstrip('0')
            if len(address) < 2:
                if address == '':
                    address = '0x00'
                else:
                    address = '0x0' + address
            else:
                address = '0x' + address
            opcode = line.split(': ')[1]
            if loc == aim:
                begin = address
            if opcode in ['JUMPI', 'REVERT', 'JUMP', 'RETURN', 'STOP', 'INVALID']:
                content.append(opcode)
                end = address
                stack = []  # 初始栈状态
                node.update({"id": nodeId, "begin": begin, "end": end, "content": content, "stack": stack})
                nodes.update({begin: node})
                nodeId += 1
                content = []
                aim = loc + 1
            else:
                content.append(opcode)
    # print(nodes)

    return nodes


if __name__ == '__main__':
    basic_block()
