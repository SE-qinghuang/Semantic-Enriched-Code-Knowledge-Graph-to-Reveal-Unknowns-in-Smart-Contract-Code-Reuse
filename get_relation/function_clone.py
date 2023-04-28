import numpy as np
from gensim.models.word2vec import Word2VecKeyedVectors
import tqdm
from scipy.spatial.distance import cdist
import pandas as pd
from config import configs
from get_relation.normalize_and_get_vec import normalize_and_get_vec
from now_tools import similarity_matrix
import sys
import datetime

class function_clone(normalize_and_get_vec):

    def __init__(self, configs):
        normalize_and_get_vec.__init__(self, configs)
        self.configs = configs
        self.dic_function_clone_relation = {':START_ID': [], ':END_ID': [], ':TYPE': [], 'score': []}
        self.model = Word2VecKeyedVectors.load_word2vec_format(self.configs.word_2vec_dict_model)

    def get_list_of_names_and_vec_list(self):
        list_of_names = np.load('list_of_names.npy',allow_pickle=True)
        list_of_names = list_of_names.tolist()
        vec_array = np.load('vec_array.npy')
        return list_of_names,vec_array

    def get_functions_df(self):
        node_information = pd.read_csv(self.configs.node_file)
        functions_df = node_information[(node_information[':LABEL'] == 'Function')
                                        | (node_information[':LABEL'] == 'Constructor')
                                        | (node_information[':LABEL'] == 'Modifier')
                                        | (node_information[':LABEL'] == 'Fallback')]
        return functions_df

    def get_Function_df(self):
        node_information = pd.read_csv(self.configs.node_file)
        functions_df = node_information[(node_information[':LABEL'] == 'Function')]
        return functions_df

    def get_Constructor_df(self):
        node_information = pd.read_csv(self.configs.node_file)
        functions_df = node_information[(node_information[':LABEL'] == 'Constructor')]
        return functions_df

    def get_Modifier_df(self):
        node_information = pd.read_csv(self.configs.node_file)
        functions_df = node_information[(node_information[':LABEL'] == 'Modifier')]
        return functions_df

    def get_Fallback_df(self):
        node_information = pd.read_csv(self.configs.node_file)
        functions_df = node_information[(node_information[':LABEL'] == 'Fallback')]
        return functions_df

    def get_function_clone_from_df(self, df):
        print('get function to vec')
        vec_array = np.zeros((len(df), self.configs.word_2vec_dim))
        list_of_names = []
        i = 0
        for _, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
            list_of_row = row.tolist()
            name = list_of_row[0]
            function_code = list_of_row[4]

            function_normalized_token = self.get_normalized_tokens(function_code)

            function_vec = np.zeros(self.configs.word_2vec_dim, )
            for normalized_token in function_normalized_token:
                function_vec += self.model[normalized_token]
            vec_array[i] = function_vec
            list_of_names.append(name)

            i += 1

        for i in tqdm.tqdm(range(len(vec_array))):  # print('now handling the no.{} function'.format(i))

            vec_pre = vec_array[i].reshape(1,self.configs.word_2vec_dim)
            similar_scores = similarity_matrix(vec_pre,vec_array)[0]
            list_indexs_greater_than_threshold = np.where(similar_scores >= self.configs.threshold)[0].tolist()

            name_pre = list_of_names[i]

            for index_greater_than_threshold in list_indexs_greater_than_threshold:
                name_next = list_of_names[index_greater_than_threshold]
                if name_next == name_pre:
                    pass
                else:
                    self.dic_function_clone_relation[':START_ID'].append(name_pre)
                    self.dic_function_clone_relation[':END_ID'].append(name_next)
                    self.dic_function_clone_relation[':TYPE'].append('function_clone')
                    self.dic_function_clone_relation['score'].append(similar_scores[index_greater_than_threshold])

    def get_function_clone_within_Function(self):

        functions_df = self.get_Function_df()
        self.get_function_clone_from_df(functions_df)

    def get_function_clone_within_Constructor(self):
        constructor_df = self.get_Constructor_df()
        self.get_function_clone_from_df(constructor_df)

    def get_function_clone_within_Modifier(self):

        modifier_df = self.get_Modifier_df()
        self.get_function_clone_from_df(modifier_df)

    def get_function_clone_within_Fallback(self):
        modifier_df = self.get_Fallback_df()
        self.get_function_clone_from_df(modifier_df)

    def get_function_clone_relation(self):
        self.get_function_clone_within_Constructor()
        self.get_function_clone_within_Modifier()
        self.get_function_clone_within_Function()
        #if error, delete self.get_function_clone_within_Fallback()
        self.get_function_clone_within_Fallback()
        df = pd.DataFrame(self.dic_function_clone_relation)
        df.to_csv(self.configs.function_clone_file, index=0)
