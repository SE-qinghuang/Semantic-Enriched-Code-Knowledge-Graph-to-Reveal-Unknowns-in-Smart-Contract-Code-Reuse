import numpy as np
from slither import Slither
from get_relation.normalize_and_get_vec import normalize_and_get_vec
from gensim.models.word2vec import Word2VecKeyedVectors
from now_tools import get_function_code, get_flow_chart_nodes, get_flow_chart_rels, get_cfg, get_infos_from_FEN, \
    format_node_expression, get_entity_attributes, similarity_matrix, get_cfg_nodes_from_cfg, get_cfg_rels_from_cfg, \
    get_para_and_returns_of_a_function, get_function_type, judge_the_clone
from tools.neo4j_commands import Neo4jCommands
import tqdm
import json
import pandas as pd
from transformers import RobertaTokenizer, RobertaConfig, RobertaModel
from Recommendation_Baseline.CodeBert.test_clone_metric import Clone_Detection_based_on_CodeBert

class code_cheching(normalize_and_get_vec, Neo4jCommands):
    def __init__(self, configs):
        normalize_and_get_vec.__init__(self, configs)
        self.configs = configs
        self.normalize_and_get_vec = normalize_and_get_vec
        # self.FEN_to_vectors = pd.read_csv(self.configs.FEN_to_vectors)
        self.list_of_FENs = np.load(self.configs.list_of_FENs, allow_pickle=True).tolist()
        self.isCodeBert = False
        # self.isCodeBert = True

        # # Code Bert
        if self.isCodeBert == True:
            self.embedding_dim = self.configs.codebert_dim
            self.threshold = self.configs.threshold_for_codebert
            self.model = RobertaModel.from_pretrained(self.configs.codeBertModel)
            self.Clone_Detection_based_on_CodeBert_object = Clone_Detection_based_on_CodeBert()
            self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
            self.codebert_array = np.load(self.configs.codebert_array, allow_pickle=True)


        # Word2vec
        else:

            self.embedding_dim = self.configs.word_2vec_dim
            self.threshold = self.configs.threshold_for_word2vec
            self.model = Word2VecKeyedVectors.load_word2vec_format(self.configs.word_2vec_dict_model)
            self.word2vec_array = np.load(self.configs.word_2vec_array, allow_pickle=True)

        self.checking_result_index = 0
        self.checking_result = {'result': []}

    def get_function_vec(self, function_code):
        if self.isCodeBert == True:
            function_vec = self.Clone_Detection_based_on_CodeBert_object.get_vector_of_code(function_code, self.model, self.tokenizer)
        else:
            function_normalized_token = self.get_normalized_tokens(function_code)
            function_vec = np.zeros(self.configs.word_2vec_dim)
            for normalized_token in function_normalized_token:
                try:
                    function_vec += self.model[normalized_token]
                except:
                    pass

        return function_vec

    def vec_array_of_function_nodes(self, function_nodes):

        vec_array = np.zeros((len(function_nodes), self.embedding_dim))
        i = 0
        for node in tqdm.tqdm(function_nodes):
            function_FEN = node['node']['FEN']
            idx_of_FEN = self.list_of_FENs.index(function_FEN)

            if self.isCodeBert == True:

                function_vec = self.codebert_array[idx_of_FEN]
            else:
                function_vec = self.word2vec_array[idx_of_FEN]

            vec_array[i] = function_vec
            i += 1

        return vec_array

    def get_input_function_vec(self, function):
        file_path = function.source_mapping['filename_absolute']
        function_lines = function.source_mapping['lines']
        function_code = get_function_code(file_path, function_lines)
        function_vec = self.get_function_vec(function_code)
        function_vec = function_vec.reshape(1, self.embedding_dim)
        return function_vec

    def count_difference(self, all_different_nodes_of_matched_cfgs):
        difference_node_to_num = {}
        for different_nodes in all_different_nodes_of_matched_cfgs:
            set_different_nodes = set(different_nodes)
            for node_expression in set_different_nodes:
                if node_expression in difference_node_to_num:
                    difference_node_to_num[node_expression] += 1
                else:
                    difference_node_to_num[node_expression] = 1
        return difference_node_to_num

    '''
    return
        same_nodes_pairs(dict) : {node id of cfg1 : node id of cfg 2}
        different_nodes_in_cfg1_nodes(list) : [node id]
        different_nodes_in_cfg2_nodes(list) : [node id]
    '''
    def check_nodes(self, cfg1_nodes, cfg2_nodes):
        same_nodes_pairs = {}

        different_nodes_in_cfg1_nodes = []
        different_nodes_in_cfg2_nodes = []

        for node_id in cfg1_nodes:
            different_nodes_in_cfg1_nodes.append(node_id)

        for node_id in cfg2_nodes:
            different_nodes_in_cfg2_nodes.append(node_id)

        for cfg1_node_id, cfg1_node_expression in cfg1_nodes.items():

            for cfg2_node_id in different_nodes_in_cfg2_nodes:

                cfg2_node_expression = cfg2_nodes[cfg2_node_id]
                if cfg1_node_expression == cfg2_node_expression:
                    same_nodes_pairs[cfg1_node_id] = cfg2_node_id

                    different_nodes_in_cfg1_nodes.remove(cfg1_node_id)
                    different_nodes_in_cfg2_nodes.remove(cfg2_node_id)

                    break

        return same_nodes_pairs, different_nodes_in_cfg1_nodes, different_nodes_in_cfg2_nodes

    def get_cfgNodeID_to_preNodeIDs(self, cfg_rels, same_nodeIDs_in_cfg):
        final_cfgNodeID_to_preNodeIDs = {}
        dict_cfgNode_to_preNodes = {}
        set_of_nodeIDs = set()
        #entry point
        dict_cfgNode_to_preNodes['0'] = []
        for cfg_rel in cfg_rels:
            pre_cfgNodeID = cfg_rel.split('->')[0].split('[')[0]
            next_cfgNodeID = cfg_rel.split('->')[1].split('[')[0]

            set_of_nodeIDs.add(pre_cfgNodeID)
            set_of_nodeIDs.add(next_cfgNodeID)

            if next_cfgNodeID in dict_cfgNode_to_preNodes:
                dict_cfgNode_to_preNodes[next_cfgNodeID].append(pre_cfgNodeID)
            else:
                dict_cfgNode_to_preNodes[next_cfgNodeID] = [pre_cfgNodeID]

        for cfgNodeID in set_of_nodeIDs:
            try:
                pre_NodeIDs = dict_cfgNode_to_preNodes[cfgNodeID]
                self.NodeIDs_been_found = set()
                all_pre_NodeIDs = self.find_all_pre_NodeIDs(dict_cfgNode_to_preNodes, pre_NodeIDs, [])

                #get the IDs of same nodeIDs
                final_cfgNodeID_to_preNodeIDs[cfgNodeID] = set(all_pre_NodeIDs) & set(same_nodeIDs_in_cfg)
            except:
                pass
        return final_cfgNodeID_to_preNodeIDs

    def find_all_pre_NodeIDs(self, dict_cfgNode_to_preNodes, pre_NodeIDs, all_pre_NodeIDs):

        if pre_NodeIDs == []:

            return all_pre_NodeIDs
        else:
            all_pre_NodeIDs += pre_NodeIDs
            for pre_NodeID in pre_NodeIDs:

                pre_pre_NodeIDs = dict_cfgNode_to_preNodes[pre_NodeID]
                if pre_NodeID in self.NodeIDs_been_found:
                    pass
                else:
                    self.NodeIDs_been_found.add(pre_NodeID)
                    all_pre_NodeIDs = self.find_all_pre_NodeIDs(dict_cfgNode_to_preNodes, pre_pre_NodeIDs, all_pre_NodeIDs)

            return all_pre_NodeIDs

    def map_cfg1NodeIDs_to_2(self, cfg1NodeIDs, same_nodes_pairs):
        mapped_cfg1NodeIDs = set()
        for cfg1NodeID in cfg1NodeIDs:
            cfg2NodeID = same_nodes_pairs[cfg1NodeID]
            mapped_cfg1NodeIDs.add(cfg2NodeID)
        return mapped_cfg1NodeIDs

    '''
    input
        same_nodes_pairs(dict) : {node id of cfg1 : node id of cfg 2}
        cfg1_rels(list) : [cfg1 node id -> cfg1 node id]
        cfg2_rels(list) : [cfg2 node id -> cfg2 node id]
    return 
        different_nodes_in_seq1 : [cfg1 node id]
        different_nodes_in_seq2 : [cfg2 node id]
    '''
    def check_sequence(self, same_nodes_pairs, cfg1_rels, cfg2_rels):
        if (cfg1_rels == []) | (cfg2_rels == []):
            return [], []
        same_nodeIDs_in_cfg1 = []
        same_nodeIDs_in_cfg2 = []
        different_cfgNodeIDs_in_seq1 = []
        different_cfgNodeIDs_in_seq2 = []
        #get same node IDs of same nodes pairs
        for cfg1NodeId, cfg2NodeId in same_nodes_pairs.items():
            same_nodeIDs_in_cfg1.append(cfg1NodeId)
            same_nodeIDs_in_cfg2.append(cfg2NodeId)

        dict_cfg1NodeID_to_preNodeIDs = self.get_cfgNodeID_to_preNodeIDs(cfg1_rels, same_nodeIDs_in_cfg1)
        dict_cfg2NodeID_to_preNodeIDs = self.get_cfgNodeID_to_preNodeIDs(cfg2_rels, same_nodeIDs_in_cfg2)


        for index in range(len(same_nodeIDs_in_cfg1)):
            cfg1NodeId = same_nodeIDs_in_cfg1[index]
            cfg2NodeId = same_nodes_pairs[cfg1NodeId]

            cfg1_preNodeIDs = dict_cfg1NodeID_to_preNodeIDs[cfg1NodeId]

            mapped_cfg1_preNodeIDs = self.map_cfg1NodeIDs_to_2(cfg1_preNodeIDs, same_nodes_pairs)

            cfg2_preNodeIDs = dict_cfg2NodeID_to_preNodeIDs[cfg2NodeId]

            if mapped_cfg1_preNodeIDs != cfg2_preNodeIDs:
                different_cfgNodeIDs_in_seq1.append(cfg1NodeId)
                different_cfgNodeIDs_in_seq2.append(cfg2NodeId)

        return different_cfgNodeIDs_in_seq1, different_cfgNodeIDs_in_seq2

    def get_differences(self, input_cfg_nodes, input_cfg_rels, matched_cfg_nodes, matched_cfg_rels):

        same_nodes_pairs, different_nodes_of_input, different_nodes_of_matched_cfg = self.check_nodes(input_cfg_nodes,
                                                                                                      matched_cfg_nodes)

        different_sequence_of_input, different_sequence_of_matched_cfg = self.check_sequence(same_nodes_pairs,
                                                                                             input_cfg_rels,
                                                                                             matched_cfg_rels)
        differences_of_input = set(different_nodes_of_input + different_sequence_of_input)
        differences_of_matched = set(different_nodes_of_matched_cfg + different_sequence_of_matched_cfg)

        # differences_of_input = set(different_nodes_of_input)
        # differences_of_matched = set(different_nodes_of_matched_cfg)

        return differences_of_input, differences_of_matched

    def get_node_expressions(self, node_id_set, dict_node_id_to_expression):
        expressions = []

        for node_id in node_id_set:

            expression = dict_node_id_to_expression[node_id]
            expression = expression.replace('require(bool)', 'require')
            expressions.append(expression)

            # expressions.append(dict_node_id_to_expression[node_id])
        return expressions

    def get_flow_chart_graph_nodes(self, flow_chart_nodes, difference_of_matched_cfg):
        graph = []

        for flow_chart_node_id, flow_chart_node_expression in flow_chart_nodes.items():
            dict_one_item = {}
            dict_one_item['key'] = flow_chart_node_expression.strip()
            color = 'lightblue'
            for different_node in difference_of_matched_cfg:
                if flow_chart_node_id in different_node:
                    color = '#F5A9A9'
                    break
            dict_one_item['color'] = color
            graph.append(dict_one_item)
        return graph

    def get_flow_chart_graph_index(self, matched_node_flow_chart, flow_chart_nodes):
        graph_index = []
        flow_chart_rels = get_flow_chart_rels(matched_node_flow_chart)
        for flow_chart_rel in flow_chart_rels:
            dict_one_index_item = {}

            if type(flow_chart_rel) == str:
                pre_node_id = flow_chart_rel.split('->')[0].split('[')[0]
                next_node_id = flow_chart_rel.split('->')[1].split('[')[0]
                dict_one_index_item['from'] = flow_chart_nodes[pre_node_id].strip()
                dict_one_index_item['to'] = flow_chart_nodes[next_node_id].strip()
            else:
                pre_node_id = flow_chart_rel[0].split('->')[0].split('[')[0]
                next_node_id = flow_chart_rel[0].split('->')[1].split('[')[0]
                dict_one_index_item['from'] = flow_chart_nodes[pre_node_id].strip()
                dict_one_index_item['to'] = flow_chart_nodes[next_node_id].strip()
                dict_one_index_item['text'] = flow_chart_rel[1]
            graph_index.append(dict_one_index_item)
        return graph_index

    def get_flow_chart_graph(self, matched_node_flow_chart, difference_of_matched_cfg):

        flow_chart_nodes = get_flow_chart_nodes(matched_node_flow_chart)

        graph = self.get_flow_chart_graph_nodes(flow_chart_nodes, difference_of_matched_cfg)
        graph_index = self.get_flow_chart_graph_index(matched_node_flow_chart, flow_chart_nodes)

        return graph, graph_index

    def get_the_results_of_type_vulnerable(self, function, matched_nodes):

        input_function_type = get_function_type(function)

        input_code_cfg = get_cfg(function.nodes)
        input_code_cfg = input_code_cfg.replace('require(bool)', 'require')
        input_code_cfg = input_code_cfg.replace('assert(bool)', 'assert')
        input_code_cfg = input_code_cfg.replace('suicide(address)', 'suicide')
        input_code_cfg = input_code_cfg.replace('selfdestruct(address)', 'selfdestruct')
        input_code_cfg = input_code_cfg.replace('onlyowner()', 'onlyowner')
        input_code_cfg = input_code_cfg.replace('onlyOwner()', 'onlyOwner')
        input_code_cfg = input_code_cfg.replace('>', '&gt;')
        input_code_cfg = input_code_cfg.replace('<', '&lt;')

        input_cfg_nodes = get_cfg_nodes_from_cfg(input_code_cfg)
        input_cfg_rels = get_cfg_rels_from_cfg(input_code_cfg)


        dict_vulnerable_result = {}
        all_different_nodes_of_matched_cfgs = []
        #keshan
        all_different_nodes_of_input_cfgs = []

        dict_vulnerable_result['type'] = 1
        dict_vulnerable_result['url'] = 'http://127.0.0.1:5000/{}'.format(self.checking_result_index)
        dict_vulnerable_result['function'] = function.canonical_name

        results = []

        index = 0
        for matched_node in tqdm.tqdm(matched_nodes, total=len(matched_nodes), desc="get {}'s vulnerable results".format(function.canonical_name)):
            result = {}
            matched_FEN, matched_cfg, matched_node_code, matched_node_flow_chart, _, _, _ = get_entity_attributes(
                matched_node)

            matched_cfg = matched_cfg.replace('require(bool)', 'require')
            matched_cfg = matched_cfg.replace('assert(bool)', 'assert')
            matched_cfg = matched_cfg.replace('suicide(address)', 'suicide')
            matched_cfg = matched_cfg.replace('selfdestruct(address)', 'selfdestruct')
            matched_cfg = matched_cfg.replace('onlyowner()', 'onlyowner')
            matched_cfg = matched_cfg.replace('onlyOwner()', 'onlyOwner')
            matched_cfg = matched_cfg.replace('>', '&gt;')
            matched_cfg = matched_cfg.replace('<', '&lt;')


            matched_cfg_nodes = get_cfg_nodes_from_cfg(matched_cfg)
            matched_cfg_rels = get_cfg_rels_from_cfg(matched_cfg)
            blocknumber, sol_file, contract_name, function_name = get_infos_from_FEN(matched_FEN)
            file_path = function.source_mapping['filename_absolute']
            function_lines = function.source_mapping['lines']
            input_code = get_function_code(file_path, function_lines)

            differences_of_input_cfg, differences_of_matched_cfg = self.get_differences(input_cfg_nodes, input_cfg_rels,
                                                                                        matched_cfg_nodes,
                                                                                        matched_cfg_rels)

            different_expressions_of_input_cfg = self.get_node_expressions(differences_of_input_cfg, input_cfg_nodes)
            different_expressions_of_matched_cfg = self.get_node_expressions(differences_of_matched_cfg,
                                                                             matched_cfg_nodes)

            #keshan
            all_different_nodes_of_input_cfgs.append(different_expressions_of_input_cfg)
            all_different_nodes_of_matched_cfgs.append(different_expressions_of_matched_cfg)

            graph, graph_index = self.get_flow_chart_graph(matched_node_flow_chart, differences_of_matched_cfg)
            composition_count = matched_node['node']['Composition_Count']
            clones_num = len(list(self.find_nodes_of_function_clone(matched_FEN)))
            matched_function_type = str(matched_node['node'].labels).replace(':', '')
            result['blocknumber'] = blocknumber
            result['contract'] = contract_name
            result['function_name'] = function_name
            result['clones_num'] = clones_num
            result['composition_count'] = composition_count
            result['input_function_type'] = input_function_type
            result['matched_function_type'] = matched_function_type
            result['link'] = 'http://127.0.0.1:5000/{}result{}'.format(self.checking_result_index, index)
            result['codes'] = [input_code, matched_node_code]
            result['highlight1'] = different_expressions_of_input_cfg
            result['highlight2'] = different_expressions_of_matched_cfg
            result['graph'] = graph
            result['graph_index'] = graph_index

            results.append(result)
            index += 1

        self.checking_result_index += 1

        difference_node_to_num = self.count_difference(all_different_nodes_of_matched_cfgs)
        for result in results:
            percentages = []
            difference_of_matched_code = result['highlight2']
            for highLight in difference_of_matched_code:
                rate = str(int(difference_node_to_num[highLight] / len(matched_nodes) * 100)) + '%'
                percentages.append(rate)
                highLight = highLight.replace('&gt;', '>')
                highLight = highLight.replace('&lt;', '<')
                result['codes'][1] = result['codes'][1].replace(highLight, highLight + rate)
            result['percentage'] = percentages

        dict_vulnerable_result['results'] = results
        self.checking_result['result'].append(dict_vulnerable_result)


    def get_results_of_a_function(self, function):

        #1.get the paras and returns of input function
        list_of_parameter, list_of_returns = get_para_and_returns_of_a_function(function)
        #2.find the matched nodes
        nodes = list(self.nodes_with_same_para_and_returns(list_of_parameter, list_of_returns))
        #3.create the array of the matched nodes
        function_vec = self.get_input_function_vec(function)
        vec_array = self.vec_array_of_function_nodes(nodes)
        #4.calculate the similarities
        similar_scores = similarity_matrix(function_vec, vec_array)
        #5.rank
        sorted_node_idxs = np.argsort(similar_scores[0].tolist())[::-1]

        list_of_matched_nodes = []
        best_matched_codes_array = []
        successful_find_num = 0
        #6.del the clones and finally get the top 20
        for node_idx in sorted_node_idxs:

            if successful_find_num >= self.configs.checking_result_nums:
                break
            node = nodes[node_idx]
            code_vector = vec_array[node_idx]
            is_Clone = judge_the_clone(code_vector.reshape(1, self.embedding_dim), best_matched_codes_array,
                                       self.threshold)

            if is_Clone == True:
                continue
            list_of_matched_nodes.append(node)
            best_matched_codes_array.append(code_vector)
            successful_find_num += 1

        self.get_the_results_of_type_vulnerable(function, list_of_matched_nodes)


    def get_checking_code(self, code):
        f = open(self.configs.checked_code_file, 'w')
        f.write(code)
        f.close()

    def results(self):

        checked_code_sol = Slither(self.configs.checked_code_file)
        for contract in checked_code_sol.contracts:
            for function in contract.functions_and_modifiers_declared:
                # useless
                if (function.function_type == 'CONSTRUCTOR_VARIABLES') | (
                        function.name == 'slitherConstructorConstantVariables') | (
                        function.name == 'slitherConstructorVariables'):
                    continue
                function_type = get_function_type(function)
                if function_type == 'Abstract_Function':
                    continue
                self.get_results_of_a_function(function)

    def get_checking_results(self, code):
        self.get_checking_code(code)
        self.results()
        json_checking_result = json.dumps(self.checking_result)
        with open(self.configs.checking_result_file, 'w') as json_file:
            json_file.write(json_checking_result)
        return json_checking_result


