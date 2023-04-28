from Model.bm25Model import bm25_for_search
from now_tools import get_flow_chart_rels, get_flow_chart_nodes, get_infos_from_FEN, count_diversity, judge_whether_the_function_is_clone
import tqdm
import numpy as np
import re
from collections import Counter
from tools.neo4j_commands import Neo4jCommands
from gensim.models.word2vec import Word2VecKeyedVectors
import math

class code_recommendation(bm25_for_search, Neo4jCommands):

    def __init__(self, configs):
        bm25_for_search.__init__(self, configs)
        self.configs = configs
        self.bm25_Model, self.corpus, self.dict_corpusid_FEN,  = self.bm25_load()
        # self.recommendation_results = {'result': []}

    def find_node_by_FEN(self,FEN):
        node = self.configs.graph.run("match(node{FEN:'%s'}) return node" %(FEN))
        return list(node)[0]


    def find_nodes_by_query(self, query):
        model = Word2VecKeyedVectors.load_word2vec_format('Model/dim_150_dic.bin')
        query = query.split()
        scores = self.bm25_Model.get_scores(query)

        best_matched_index = np.argsort(scores)[::-1]

        # #compare cb1
        # #the function name + comment or function name + completed desctiption + flow chart, the difference at the bm25 courpus
        # success_find_num = 0
        # list_of_matched_nodes = []
        # matched_functions_list = []
        # for merged_info_index in tqdm.tqdm(best_matched_index):
        #     if success_find_num == self.configs.top_n:
        #         break
        #     info = self.corpus[merged_info_index]
        #     FEN = self.dict_corpusid_FEN[merged_info_index]
        #     matched_node = self.find_node_by_FEN(FEN)
        #     matched_node_function_code = matched_node['node']['Function_Code'].replace('\\n', '\n')
        #
        #     matched_functions_list.append(matched_node_function_code)
        #     list_of_matched_nodes.append(matched_node)
        #     success_find_num += 1
        #
        # list_of_matched_nodes_after_ptSort = list_of_matched_nodes
        # # aveSimilarity = count_diversity(matched_functions_list, self.configs.top_n, model)

        # #
        # #compare cb2
        # best_matched_merged_codes = set()
        # best_matched_infos = set()
        #
        # success_find_num = 0
        # list_of_matched_nodes = []
        # list_of_composition_count = []
        # for merged_info_index in tqdm.tqdm(best_matched_index):
        #     if success_find_num == self.configs.top_n:
        #         break
        #     info = self.corpus[merged_info_index]
        #     FEN = self.dict_corpusid_FEN[merged_info_index]
        #     matched_node = self.find_node_by_FEN(FEN)
        #     matched_node_function_code = matched_node['node']['Function_Code'].replace('\\n', '\n')
        #
        #     isClone = judge_whether_the_function_is_clone(best_matched_merged_codes, matched_node_function_code, model)
        #     if isClone == True:
        #         continue
        #
        #     # if info in best_matched_infos:
        #     #     continue
        #
        #     list_of_matched_nodes.append(matched_node)
        #
        #     # matched_node_composition_count = int(matched_node['node']['Composition_Count'])
        #
        #     # list_of_composition_count.append(matched_node_composition_count)
        #     print(scores[merged_info_index])
        #     best_matched_merged_codes.add(matched_node_function_code)
        #     success_find_num += 1
        #
        # list_of_matched_nodes_after_ptSort = list_of_matched_nodes
        # # aveSimilarity = count_diversity(best_matched_merged_codes, self.configs.top_n, model)

        #compare cb3
        best_matched_merged_codes = set()
        best_matched_infos = set()

        success_find_num = 0
        list_of_matched_nodes = []
        list_of_matched_node_scores = []
        for merged_info_index in tqdm.tqdm(best_matched_index):
            if success_find_num == self.configs.top_n:
                break
            info = self.corpus[merged_info_index]
            FEN = self.dict_corpusid_FEN[merged_info_index]
            matched_node = self.find_node_by_FEN(FEN)
            matched_node_function_code = matched_node['node']['Function_Code'].replace('\\n', '\n')

            isClone = judge_whether_the_function_is_clone(best_matched_merged_codes, matched_node_function_code, model)
            if isClone == True:
                continue

            # if info in best_matched_infos:
            #     continue

            list_of_matched_nodes.append(matched_node)
            composition_count = int(matched_node['node']['Composition_Count'])
            if composition_count == 0:
                matched_node_score = scores[merged_info_index]
            else:
                matched_node_score = scores[merged_info_index] * math.log(composition_count)
            # matched_node_scores = int(matched_node['node']['Composition_Count'])

            list_of_matched_node_scores.append(matched_node_score)
            best_matched_merged_codes.add(matched_node_function_code)
            success_find_num += 1

        composition_count_indexs = np.argsort(list_of_matched_node_scores)[::-1]
        list_of_matched_nodes_after_ptSort = []
        for index in composition_count_indexs:
            list_of_matched_nodes_after_ptSort.append(list_of_matched_nodes[index])
        return list_of_matched_nodes_after_ptSort

    def get_pair_link_and_name(self, FEN):
        pair_link = []
        pair_link_name = []
        matched_nodes = list(self.configs.graph.run("match(pre_node{FEN:'%s'})-[relation:Cooccurrence]->(node) return node" % (FEN)))
        for matched_node in matched_nodes:
            id = matched_node['node'].identity
            FEN = matched_node['node']['FEN']
            blocknumber, sol_file, contract_name, function_name = get_infos_from_FEN(FEN)

            link = 'http://127.0.0.1:5000/{}detail'.format(id)
            link_name = function_name
            pair_link.append(link)
            pair_link_name.append(link_name)
        return pair_link, pair_link_name

    def get_pair_link_content(self, FEN):
        pair_link_content = []

        matched_nodes = list(self.configs.graph.run("match(pre_node{FEN:'%s'})-[relation:Cooccurrence]->(node) return node" % (FEN)))
        for matched_node in matched_nodes:

            matched_FEN = matched_node['node']['FEN']

            pair_node_FEN_blocknumber, pair_node_FEN_sol_file, pair_node_FEN_contract_name, pair_node_FEN_function_name = get_infos_from_FEN(matched_FEN)

            pair_node_composition_count = matched_node['node']['Composition_Count']
            pair_node_function_code = matched_node['node']['Function_Code'].replace('\\n','\n')

            content = 'blocknumber : {}\n' \
                      'sol file : {}\n' \
                      'contract : {}\n' \
                      'function : {}\n' \
                      'composition count : {}\n' \
                      'function code : \n {}'.format(pair_node_FEN_blocknumber, pair_node_FEN_sol_file,
                                                     pair_node_FEN_contract_name, pair_node_FEN_function_name,
                                                     pair_node_composition_count, pair_node_function_code)
            pair_link_content.append(content)

        return pair_link_content

    def get_a_recommendation_result(self, node):
        result = {}
        id = node['node'].identity
        FEN = node['node']['FEN']
        blocknumber, sol_file, contract_name, function_name = get_infos_from_FEN(FEN)
        composition_count = node['node']['Composition_Count']
        url1 = 'http://127.0.0.1:5000/{}detail'.format(id)
        url2 = 'http://127.0.0.1:5000/{}searchchat'.format(id)
        pair_link, pair_link_name = self.get_pair_link_and_name(FEN)
        pair_link_content = self.get_pair_link_content(FEN)
        function_code = node['node']['Function_Code'].replace('\\n', '\n')
        flow_chart = node['node']['Flow_Chart'].replace('\\n', '\n')

        graph = []
        flow_chart_nodes = get_flow_chart_nodes(flow_chart)
        flow_chart_rels = get_flow_chart_rels(flow_chart)
        for flow_chart_node_id, flow_chart_node_expression in flow_chart_nodes.items():
            dict_one_item = {}
            dict_one_item['key'] = flow_chart_node_expression.strip()
            color = 'lightblue'

            dict_one_item['color'] = color
            graph.append(dict_one_item)

        graph_index = []
        for flow_chart_rel in flow_chart_rels:
            dict_one_index_item = {}

            if type(flow_chart_rel) == str:
                pre_node_id = flow_chart_rel.split('->')[0]
                next_node_id = flow_chart_rel.split('->')[1]
                dict_one_index_item['from'] = flow_chart_nodes[pre_node_id].strip()
                dict_one_index_item['to'] = flow_chart_nodes[next_node_id].strip()
            else:
                pre_node_id = flow_chart_rel[0].split('->')[0]
                next_node_id = flow_chart_rel[0].split('->')[1]
                dict_one_index_item['from'] = flow_chart_nodes[pre_node_id].strip()
                dict_one_index_item['to'] = flow_chart_nodes[next_node_id].strip()
                dict_one_index_item['text'] = flow_chart_rel[1]
            graph_index.append(dict_one_index_item)

        result['blocknumber'] = blocknumber
        result['sol_file'] = sol_file
        result['contract'] = contract_name
        result['function'] = function_name
        result['composition_count'] = composition_count
        result['url1'] = url1
        result['url2'] = url2
        result['pair_link'] = pair_link
        result['pair_link_name'] = pair_link_name
        result['pair_link_content'] = pair_link_content
        result['function_code'] = function_code
        result['graph'] = graph
        result['graph_index'] = graph_index

        return result

    def get_a_result_by_entity_id(self, id):
        neo4j_command = "match(node) where id(node) = {} return node".format(id)
        matched_node = list(self.configs.graph.run(neo4j_command))[0]
        result = self.get_a_recommendation_result(matched_node)
        return result


    def search(self, query):
        # query = query.casefold()
        query = re.sub('[_().,{}\[\]]', ' ', query)
        self.recommendation_results = {'result': []}

        list_of_matched_nodes = self.find_nodes_by_query(query)
        for matched_node in tqdm.tqdm(list_of_matched_nodes):
            result = self.get_a_recommendation_result(matched_node)
            self.recommendation_results['result'].append(result)

        return self.recommendation_results
