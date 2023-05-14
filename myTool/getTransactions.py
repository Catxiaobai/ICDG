#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time:
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""
import requests

api_key = '5YZX6Q5KZRPKG25N3RHP4XIFV8J12Z77ES'
contract_address = '0x7510792A3B1969F9307F3845CE88e39578f2bAE1'

# 构造 API 请求 URL
tx_url = f'https://api.etherscan.io/api?module=account&action=txlist&address={contract_address}&apikey={api_key}'
tx_inter_url = f'https://api.etherscan.io/api?module=account&action=txlistinternal&address={contract_address}&apikey={api_key}'

# 发送 GET 请求
response = requests.get(tx_url)
 
# 解析响应数据
if response.status_code == 200:
    result = response.json().get('result')
    if result:
        # 遍历交易记录
        for tx in result:
            # 提取所需的交易信息
            tx_hash = tx.get('hash')
            from_address = tx.get('from')
            to_address = tx.get('to')
            value = tx.get('value')

            # 打印交易信息
            print(f'Transaction Hash: {tx_hash}')
            print(f'From: {from_address}')
            print(f'To: {to_address}')
            print(f'Value: {value}')
            print('---')
    else:
        print('No transactions found for the contract.')
else:
    print('Error:', response.status_code)
