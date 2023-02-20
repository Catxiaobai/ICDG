#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/2/15 11:20
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""


class Pair:
    def __init__(self, first=None, second=None):
        self.first = first
        self.second = second

    def getFirst(self):
        return self.first

    def setFirst(self, first):
        self.first = first

    def getSecond(self):
        return self.second

    def setSecond(self, second):
        self.second = second
