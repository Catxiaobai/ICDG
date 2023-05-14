#! /usr/bin/python3
# -*-coding:utf-8-*-

"""
@Time: 2023/5/04 10:32
@Author : mengjie-1998@qq.com
@Remark: a brief description
"""

import random

# 定义输入域范围（32位二进制编码）
input_domain = {
    'param1': (0, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff),
    'param2': (0, 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff),
    # 可根据实际情况添加更多参数
}

# 定义遗传算法参数
population_size = 10
max_generations = 10
mutation_rate = 0.1


# 生成随机的测试用例个体
def generate_test_case():
    test_case = {}
    for param, (min_val, max_val) in input_domain.items():
        test_case[param] = random.randint(min_val, max_val)
    return test_case


# 计算个体的适应度（覆盖的路径与目标路径之间的相似度）
def calculate_fitness(individual, path, pos2BlockMap):
    CALLDATA = '0x' + hex(int(pos2BlockMap[path[0]].function))[2:].zfill(8) + hex(individual['param1'])[2:].zfill(32) + hex(
        individual['param1'])[2:].zfill(32)
    # 初始化
    cross_level = 0
    control_level = 0
    branch_distance = len(path)
    for p in path:
        if pos2BlockMap[p].isCallFunction:
            cross_level += 1
        if pos2BlockMap[p].conditionalJumpExpression != "":
            control_level += 1

    for i, p in enumerate(path):
        branch_distance -= 1
        if pos2BlockMap[p].isCallFunction:
            cross_level -= 1
        if pos2BlockMap[p].conditionalJumpExpression != '':
            control_level -= 1
            # 开始计算适应度
            # print(pos2BlockMap[p].conditionalJumpExpression)
            # print(CALLDATA)

    f = control_level + (1 - 1.01 ** -branch_distance)
    F = cross_level + (1 - 1.01 ** -f)
    return F


# 选择操作（使用轮盘赌选择）
def selection(population):
    max_fitness = max(individual['fitness'] for individual in population)
    adjusted_fitness = [max_fitness - individual['fitness'] for individual in population]
    total_fitness = sum(adjusted_fitness)
    probabilities = [fitness / total_fitness for fitness in adjusted_fitness]
    selected = random.choices(population, probabilities, k=2)
    return selected[0], selected[1]


# 交叉操作
def crossover(parent1, parent2):
    child = {}
    for param in input_domain.keys():
        if random.random() < 0.5:
            child[param] = parent1[param]
        else:
            child[param] = parent2[param]
    return child


# 变异操作
def mutation(individual):
    mutated = individual.copy()
    for param in input_domain.keys():
        if random.random() < mutation_rate:
            mutated[param] = random.randint(*input_domain[param])
    return mutated


# 主程序
def genetic_algorithm(path, pos2BlockMap):
    path.reverse()
    population = []
    for _ in range(population_size):
        test_case = generate_test_case()
        fitness = calculate_fitness(test_case, path, pos2BlockMap)
        population.append({'test_case': test_case, 'fitness': fitness})
    best_individual = min(population, key=lambda ind: ind['fitness'])
    if best_individual['fitness'] == 0:
        print("Target path is covered by the generated test case!")
        return 1

    for generation in range(max_generations):
        new_population = []
        for _ in range(population_size):
            parent1, parent2 = selection(population)
            child = crossover(parent1['test_case'], parent2['test_case'])
            child = mutation(child)
            fitness = calculate_fitness(child, path, pos2BlockMap)
            new_population.append({'test_case': child, 'fitness': fitness})

        population = new_population

        best_individual = min(population, key=lambda ind: ind['fitness'])
        print(f"Generation {generation + 1}: Best fitness = {best_individual['fitness']}")

        if best_individual['fitness'] == 0:
            print("Target path is covered by the generated test case!")
            return 1

    print("Failed to cover the target path!")
    return 0
