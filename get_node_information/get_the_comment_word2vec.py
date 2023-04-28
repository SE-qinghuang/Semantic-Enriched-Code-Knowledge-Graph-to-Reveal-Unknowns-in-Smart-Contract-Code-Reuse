import gensim, logging
import numpy as np
import re
import pandas as pd
from gensim.models.keyedvectors import load_word2vec_format
from scipy.spatial.distance import cdist
from config import configs
import json
class comment_word2vec():
    def __init__(self,configs):
        self.configs = configs
        self.function_type_nodes = self.find_function_type_nodes()

        print('start load description embedding model...')
        self.model = gensim.models.KeyedVectors.load_word2vec_format(self.configs.description_embedding_path, binary=False)
        print('embedding model is loaded...')

        if self.configs.description_data == 'handle':

            self.vec_array, self.dict_function_index_2_node_name = self.get_description_vecs_and_dic_function_index_2_node_name()
            self.save_vec_array_and_dict_function_index_2_node_name()

        elif self.configs.description_data == 'load':
            self.vec_array, self.dict_function_index_2_node_name = self.load_description_data()
        else:
            raise

    def description_vecs_dic_function_index_2_node_name(self):
        return self.vec_array, self.dict_function_index_2_node_name

    def find_function_type_nodes(self):
        df = pd.read_csv(self.configs.node_file)
        nodes = df[df['type'] == 'function']
        nodes = nodes.reindex(columns=['name','type','description sentence'])
        return nodes

    def get_wordvector(self,word):#获取词向量
        try:
            return self.model[word]
        except:
            return np.zeros(self.configs.description_embedding_dim)

    def get_sentence_vector(self,description):
        description = description.translate(str.maketrans('[].,()', '      '))  # depart expression
        description = re.sub('[0-9’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~]+', '',
                                      description)  # remove characters
        vector = np.zeros(self.configs.description_embedding_dim)
        for word in description.split():
            wordvector = self.get_wordvector(word)
            vector += wordvector
        # vector = vector/len(description.split())
        vector = vector.reshape(1, self.configs.description_embedding_dim)
        return vector

    #nlp word2vec model,the nodes of function type
    def get_description_vecs_and_dic_function_index_2_node_name(self):
        print('start handle description vector and get dict of function index to node_name..')
        dict_function_index_2_node_name = {}

        function_index = 0

        for node_index, row in self.function_type_nodes.iterrows():


            list_of_row = row.tolist()
            function_name = list_of_row[0]
            function_description = list_of_row[2]

            dict_function_index_2_node_name[function_index] = function_name
            vector = self.get_sentence_vector(function_description)
            vector = vector.reshape(1, self.configs.description_embedding_dim)

            if function_index == 0:
                vec_array = np.array(vector).reshape(1, self.configs.description_embedding_dim)
            else:
                vec_array = np.concatenate((vec_array, vector), axis=0)
            function_index += 1

        print('handling is done...')
        return vec_array, dict_function_index_2_node_name

    def save_vec_array_and_dict_function_index_2_node_name(self):
        print('start save array and dict...')
        np.save(self.configs.description_array,self.vec_array)
        with open(self.configs.dict_function_index_2_node_name_json, 'w') as f:
            json.dump(self.dict_function_index_2_node_name, f)
        f.close()
        print('has done...')

    def load_description_data(self):
        print('start load')
        with open(self.configs.dict_function_index_2_node_name_json, 'r') as f:
            dict_function_index_2_node_name = json.load(f)
        f.close()
        vec_array = np.load(self.configs.description_array, allow_pickle=True)

        return vec_array,dict_function_index_2_node_name


    def similarity_matrix(self, vector_1, vector_2):
        numerator = cdist(vector_1, vector_2, 'euclidean')  # alculate the distance
        vec_norm = np.linalg.norm(vector_2, axis=1)  # rm by line,vec_norm : (22718,)
        vec_tile = np.tile(vec_norm, (vector_1.shape[0], 1))  # vec_title:(0,22178)
        emb_norm = np.linalg.norm(vector_1, axis=1)  # (1,)
        emb_tile = np.tile(emb_norm, (vector_2.shape[0], 1)).transpose()  # (1,22718)
        denominator = np.add(vec_tile, emb_tile)  # (1,22178)
        similarity_matrix = 1 - np.divide(numerator,denominator)  # (1,22718),The similarity between the contract and each contract
        return similarity_matrix




