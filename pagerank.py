# -*- coding: utf-8 -*-
import pandas as pd
from pygraph.classes.digraph import digraph
import csv

up_dict = {}
fans = {}
article = {}
data_set = []
up = set()


class PRIterator:
    __doc__ = '''计算一张图中的PR值'''

    def __init__(self, dg):
        self.damping_factor = 0.85  # 阻尼系数,即α
        self.max_iterations = 100  # 最大迭代次数
        self.min_delta = 0.00001  # 确定迭代是否结束的参数,即ϵ
        self.graph = dg

    def page_rank(self):
        #  先将图中没有出链的节点改为对所有节点都有出链
        for node in self.graph.nodes():
            if len(self.graph.neighbors(node)) == 0:
                for node2 in self.graph.nodes():
                    digraph.add_edge(self.graph, (node, node2))

        nodes = self.graph.nodes()
        graph_size = len(nodes)

        if graph_size == 0:
            return {}
        page_rank = dict.fromkeys(nodes, 1.0 / graph_size)  # 给每个节点赋予初始的PR值
        damping_value = (1.0 - self.damping_factor) / graph_size  # 公式中的(1−α)/N部分

        flag = False
        for i in range(self.max_iterations):
            change = 0
            for node in nodes:
                rank = 0
                for incident_page in self.graph.incidents(node):  # 遍历所有“入射”的页面
                    rank += self.damping_factor * (page_rank[incident_page] / len(self.graph.neighbors(incident_page)))
                rank += damping_value
                change += abs(page_rank[node] - rank)  # 绝对值
                page_rank[node] = rank

            print("This is NO.%s iteration" % (i + 1))
            print(page_rank)

            if change < self.min_delta:
                flag = True
                break
        if flag:
            print("finished in %s iterations!" % node)
        else:
            print("finished out of 100 iterations!")
        return page_rank


def data_read(file_name):
    with open(file_name, encoding='utf8') as f:
        content = f.read()
        content = content.split('\n\n')
    for item in content:
        # if len(data_set) > 5000:
        #     break
        data = item.split('\n')
        tmp = data[0][3:].split(' ')
        if int(data[1][5:]) > 15000:
            if tmp[1] not in up:
                up_dict[tmp[1]] = tmp[0]
                fans[tmp[1]] = data[1][5:]
                article[tmp[1]] = data[2][8:]
                up.add(tmp[1])
                data_tmp = [tmp[1]]
                for i in range(3, len(data)):
                    data_tmp.append(data[i][1:])
                data_set.append(data_tmp)


if __name__ == '__main__':
    data_read('user.txt')
    print(len(data_set))
    dg = digraph()
    dg.add_nodes(list(up))
    for i in range(len(data_set)):
        for j in range(1, len(data_set[i])):
            if data_set[i][j] in up:
                try:
                    dg.add_edge((data_set[i][0], data_set[i][j]))
                except:
                    continue

    pr = PRIterator(dg)
    page_ranks = pr.page_rank()
    id = []
    name = []
    rank =  []
    fan = []
    art = []
    for item in up:
        id.append(item)
        name.append(up_dict[item])
        rank.append(page_ranks[item])
        fan.append(fans[item])
        art.append(article[item])
    print("The final page rank is\n", page_ranks)
    # print(sorted(page_ranks))
    # print(sorted(up_dict))
    dataframe = pd.DataFrame({'id': id, 'name': name, 'rank': rank, 'fans': fan, 'articles': art})
    dataframe.to_csv("network.csv", index=False, sep=',')
