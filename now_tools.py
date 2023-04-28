import os
from slither.slither import Slither
import re
from get_relation.CFGNode import CFGnode
import numpy as np
from scipy.spatial.distance import cdist
from gensim.models.word2vec import Word2VecKeyedVectors
from get_relation.normalize_and_get_vec import normalize_and_get_vec
from config import configs
import json
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer


'''
del the prefix in node_name
such as :
/home/auatac/liao_system_7_21/little_contracts/0x0a0af8a0604ba0c40d81e6b766a0f44aa6616431/ERC20Token.sol:ERC20Token
change to 0x0a0af8a0604ba0c40d81e6b766a0f44aa6616431/ERC20Token.sol:ERC20Token
'''
def del_the_useless_preifx(node_name):

    return '0x' + node_name.split('/0x')[-1]

'''
get a string between a and b in s
'''
def get_str_btw_a_b(s, a, b):
    par = s.partition(a)
    return (par[2].partition(b))[0][:]

'''
input : file_directory
return : list of files
'''
def findAllFile(base):
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            yield fullname


def try_get_slither_object_from_sol_file(sol_file):
    version_list_4 = ['0.4.25','0.4.24', '0.4.23', '0.4.22', '0.4.21', '0.4.20', '0.4.19', '0.4.18', '0.4.17', '0.4.16',
                      '0.4.15', '0.4.14', '0.4.13', '0.4.12', '0.4.11', '0.4.10']
    success_get = False
    # os.system('solc-select use 0.4.25')
    try:
        sol = Slither(sol_file)
        success_get = True
        return success_get
    except:
        for version in version_list_4:
            os.system('solc-select use ' + version)
            try:
                sol = Slither(sol_file)
                success_get = True
                return success_get
            except:
                pass
    return success_get

'''
input :(the path of sol file,the list of fuction lines in file)
return :(string) the function_code
'''
def get_function_code(sol_file_path,function_lines):
    f = open(sol_file_path,'r')
    lines_in_file = f.readlines()
    f.close()
    function_code = ''

    for line_idx in function_lines:
        function_code += lines_in_file[line_idx - 1]
    return function_code


def get_flow_chart_nodes(flow_chart):
    dict_flow_chart_nodes = {}

    flow_chart_nodes = re.findall('(\d+)\[label = "([\s\S]*?)"\];', flow_chart)
    for flow_chart_node in flow_chart_nodes:
        node_id = flow_chart_node[0]
        node_expression = flow_chart_node[1]
        dict_flow_chart_nodes[node_id] = node_expression
    return dict_flow_chart_nodes


def get_flow_chart_rels(flow_chart):
    result1 = re.findall('(\d+->\d+);', flow_chart)
    result2 = re.findall('(\d+->\d+)\[label = "(.*)"\];', flow_chart)
    result = result1 + result2
    return result

#input : nodes of slither object function
#return(string) : the cfg of this function
def get_cfg(nodes):

    cfg = 'digraph{\n'
    cfg_nodes_rels_list = []
    for node in nodes:
        # node_expression = format_node_expression(str(node.expression))
        # cfg += '{}[label = "{}"];\n'.format(node.node_id, node_expression)

        if node.expression == None:
            node_expression = str(node)
        else:
            node_expression = str(node.expression)
        cfg += '{}[label = "{}"];\n'.format(node.node_id, node_expression)
        cfg_node = CFGnode(node)
        if len(cfg_node.cfgnode_rel) > 0:
            cfg_nodes_rels_list.append(cfg_node.cfgnode_rel)

    for cfg_node_rels in cfg_nodes_rels_list:
        for node_rel in cfg_node_rels:
            node_pre = node_rel[0]
            node_next = node_rel[1]
            rel_label = node_rel[2]
            if rel_label == 'son_true':
                label = '{}->{}[label = "true"];\n'.format(node_pre.node_id, node_next.node_id)
            elif rel_label == 'son_false':
                label = '{}->{}[label = "false"];\n'.format(node_pre.node_id, node_next.node_id)
            else:
                label = '{}->{};\n'.format(node_pre.node_id, node_next.node_id)
            cfg += label
    cfg += '}\n'
    return cfg



def get_infos_from_FEN(FEN):
    list_of_items = FEN.split(':',2)
    blocknumber = list_of_items[0].split('/')[-2]
    sol_file = list_of_items[0].split('/')[-1]
    contract_name = list_of_items[1]
    function_name = list_of_items[2]
    return blocknumber, sol_file, contract_name, function_name


def format_node_expression(node_expression):
    node_expression = node_expression.replace('require(bool)', 'require')
    node_expression = node_expression.replace('assert(bool)', 'assert')
    return node_expression


def get_entity_attributes(entity):
    FEN = entity['node']['FEN']
    cfg = entity['node']['CFG'].replace('\\n', '\n')
    function_code = entity['node']['Function_Code'].replace('\\n', '\n')
    flow_chart = entity['node']['Flow_Chart'].replace('\\n', '\n')
    data_type = entity['node']['Data_Type']
    description = entity['node']['Description']
    participating_times = entity['node']['Participating_Times']
    return FEN, cfg, function_code, flow_chart, data_type, description, participating_times

def similarity_matrix(vector_1, vector_2):
    numerator = cdist(vector_1, vector_2, 'euclidean')
    vec_norm = np.linalg.norm(vector_2, axis=1)
    vec_tile = np.tile(vec_norm, (vector_1.shape[0], 1))
    emb_norm = np.linalg.norm(vector_1, axis=1)

    emb_tile = np.tile(emb_norm, (vector_2.shape[0], 1)).transpose()
    denominator = np.add(vec_tile, emb_tile)
    similarity_matrix = 1 - np.divide(numerator, denominator)
    return similarity_matrix


#cfg : string
#cfg node : dict {node id : node expression}
def get_cfg_nodes_from_cfg(cfg):
    cfg_nodes = {}
    tuple_cfgNodes = re.findall('\n(\d+)\[label = "(.*)"\];', cfg)
    for tuple_cfgNode in tuple_cfgNodes:
        node_id = tuple_cfgNode[0]
        node_expression = tuple_cfgNode[1]
        cfg_nodes[node_id] = node_expression
    return cfg_nodes


#cfg(string) : a function's cfg
#cfg_rels(list) : the rels of the cfg, node id -> node id
def get_cfg_rels_from_cfg(cfg):
    result1 = re.findall('(\d+->\d+);', cfg)
    result2 = re.findall('(\d+->\d+\[label = ".*"\]);', cfg)
    cfg_rels = result1 + result2
    return cfg_rels


def get_para_and_returns_of_a_function(function):
    list_of_parameter = []
    for parameter in function.parameters:
        list_of_parameter.append(parameter)

    list_of_returns = []
    for returns in function.returns:
        list_of_returns.append(returns)
    return list_of_parameter, list_of_returns


#function : the function object in slither
def get_function_type(function):
    if function.function_type.name == 'FALLBACK':
        function_type = 'Fallback'
    elif function.function_type.name == 'CONSTRUCTOR':
        function_type = 'Constructor'
    elif function.__class__.__name__ == 'FunctionContract':
        if (len(function.nodes) == 0) | (len(function.nodes) == 1):
            function_type = 'Abstract_Function'
        else:
            function_type = 'Function'
    elif function.__class__.__name__ == 'Modifier':
        function_type = 'Modifier'
    else:
        function_type = 'Abstract_Function'

    return function_type

def get_vector(function_code,model):
    normalize_and_get_vec_object = normalize_and_get_vec(configs())

    function_normalized_token = normalize_and_get_vec_object.get_normalized_tokens(function_code)

    function_vec = np.zeros(150, )
    for normalized_token in function_normalized_token:
        try:
            function_vec += model[normalized_token]
        except:
            function_vec += model['unk']

    return function_vec

def count_diversity(matched_functions_list, top_k, model):
    matched_functions_list = list(matched_functions_list)
    num = 0
    total_similarity = 0
    for i in range(top_k):
        for j in range(i + 1, top_k):
            function_i = matched_functions_list[i]
            function_j = matched_functions_list[j]
            vector_i = get_vector(function_i, model).reshape(1, 150)
            vector_j = get_vector(function_j, model).reshape(1, 150)
            similarity_score = similarity_matrix(vector_i, vector_j)[0][0]
            total_similarity += similarity_score
            num += 1
    ave_similarity = total_similarity/num
    return ave_similarity

def judge_whether_the_function_is_clone(best_matched_merged_codes, function_code, model):
    # model = Word2VecKeyedVectors.load_word2vec_format('Model/dim_200_dic.bin')
    isClone = False
    for matched_code in best_matched_merged_codes:
        vector_i = get_vector(matched_code, model).reshape(1, 150)
        vector_j = get_vector(function_code, model).reshape(1, 150)
        similarity_score = similarity_matrix(vector_i, vector_j)[0][0]
        if similarity_score >= 0.96:
            isClone = True
            break
    return isClone

def judge_the_clone(code_vector, best_matched_codes_array, clone_threshold):
    is_Clone = False
    if len(best_matched_codes_array) == 0:
        return is_Clone
    matched_codes_array = np.array(best_matched_codes_array)
    similarity_scores = similarity_matrix(code_vector, matched_codes_array)[0]
    if (similarity_scores < clone_threshold).all():
        is_Clone = False
    else:
        is_Clone = True
    return is_Clone

def len_of_directory(directory):
    list_of_files = findAllFile(directory)
    length = 0
    for file in list_of_files:
        length += 1

    return length

def load_json(json_file):
    with open(json_file, 'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict

def save_dict_to_json_file(the_dict, json_file):
    with open(json_file, 'w') as json_save:
        json.dump(the_dict, json_save)

def simple_tok(sent: str):
    return sent.split()


#node_information : the DataFrame of node.csv
def get_functions_df(node_information):
    functions_df = node_information[(node_information[':LABEL'] == 'Function')
                                    | (node_information[':LABEL'] == 'Constructor')
                                    | (node_information[':LABEL'] == 'Modifier')
                                    | (node_information[':LABEL'] == 'Fallback')]
    return functions_df

#
def cosine_similarity_score(query_vector, embeddings_array):
    # similarity_score = array_a.dot(array_b) / (np.linalg.norm(array_a, axis=1) * np.linalg.norm(array_b))

    similarity_score = embeddings_array.dot(query_vector) / (np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_vector))
    return similarity_score

def function_name_of_camel_case(simple_name):

    camel_case_candidates = []

    camel_case_exp = '([A-Z][a-z]+)'
    camel_case_reg = re.compile(camel_case_exp)
    camel_case_cut = camel_case_reg.findall(simple_name)

    if not camel_case_cut:
        camel_case_candidates.append(simple_name)
    else:
        remain = simple_name
        for e in camel_case_cut:
            remain = remain.replace(e, '')
        if remain:
            camel_case_candidates.append(remain)
        for e in camel_case_cut:
            camel_case_candidates.append(e)

    return camel_case_candidates


def get_tfidf_scores(query):
    query = [query]
    vectorizer=CountVectorizer()
    transformer=TfidfTransformer()
    tfidf=transformer.fit_transform(vectorizer.fit_transform(query))
    word=vectorizer.get_feature_names()
    weight=tfidf.toarray()
    dict_word_to_tfidf = {}

    for i in range(len(weight)):
        for j in range(len(word)):
            dict_word_to_tfidf[word[j]] = weight[i][j]
    return dict_word_to_tfidf
