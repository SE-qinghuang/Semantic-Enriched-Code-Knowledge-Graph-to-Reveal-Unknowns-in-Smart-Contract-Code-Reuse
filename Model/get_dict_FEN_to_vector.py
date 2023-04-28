import numpy as np
import tqdm
import pandas as pd
from now_tools import get_functions_df
from get_relation.normalize_and_get_vec import normalize_and_get_vec
import json
from gensim.models.word2vec import Word2VecKeyedVectors
from Recommendation_Baseline.CodeBert.test_clone_metric import Clone_Detection_based_on_CodeBert
from transformers import RobertaTokenizer, RobertaConfig, RobertaModel

class Dict_FEN_to_Vector(normalize_and_get_vec):
    def __init__(self, node_file, word2vec_dict_model, codebert_model_file):
        self.node_information = pd.read_csv(node_file)
        self.functions = get_functions_df(self.node_information)
        # self.FEN_to_vectors_file = FEN_to_vectors_file
        self.token2type_file = '/home/auatac/liao_system/token2type'
        # self.dict_FEN_to_vectors = {'FEN': [], 'W2v_Vector': [], 'Codebert_Vector': []}
        self.list_of_FENs = self.functions['FEN:ID'].tolist()

        self.word2vec_model = Word2VecKeyedVectors.load_word2vec_format(word2vec_dict_model)
        self.codebert_model = RobertaModel.from_pretrained(codebert_model_file)
        self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        self.Clone_Detection_based_on_CodeBert_object = Clone_Detection_based_on_CodeBert()
        self.word2vec_dim = 150
        self.codebert_dim = 768

    def get_dict_FEN_to_W2C_vector(self):
        # dict_FEN_to_word2vec_vector = {}
        word2vec_array = np.zeros((len(self.list_of_FENs), self.word2vec_dim))
        i = 0
        for _, row in tqdm.tqdm(self.functions.iterrows(), total=self.functions.shape[0]):
            # FEN = row['FEN:ID']
            function_code = row['Function_Code'].replace('\\n', '\n')
            function_normalized_token = self.get_normalized_tokens(function_code)
            function_vec = np.zeros(self.word2vec_dim)
            for normalized_token in function_normalized_token:
                try:
                    function_vec += self.word2vec_model[normalized_token]
                except:
                    print(normalized_token)

            word2vec_array[i] = function_vec
            i += 1
        return word2vec_array


    def get_dict_FEN_to_CodeBert_vector(self):
        # dict_FEN_to_codebert_vector = {}
        codebert_array = np.zeros((len(self.list_of_FENs), self.codebert_dim))

        i = 0
        for _, row in tqdm.tqdm(self.functions.iterrows(), total=self.functions.shape[0]):
            # FEN = row['FEN:ID']
            function_code = row['Function_Code'].replace('\\n', '\n')
            function_vec = self.Clone_Detection_based_on_CodeBert_object.get_vector_of_code(function_code, self.codebert_model, self.tokenizer)
            codebert_array[i] = function_vec
            i += 1
        return codebert_array



    def FENs_and_embeddings_array(self, FENs_list_file, w2c_array_file, codebert_array_file):
        word2vec_array = self.get_dict_FEN_to_W2C_vector()
        codebert_array = self.get_dict_FEN_to_CodeBert_vector()

        np.save(FENs_list_file, self.list_of_FENs)
        np.save(w2c_array_file, word2vec_array)
        np.save(codebert_array_file, codebert_array)


if __name__ == '__main__':
    word2vec_dict_model = '/home/auatac/liao_system/Model/dim_150_dic.bin'
    codebert_model = '/home/auatac/liao_system/Recommendation_Baseline/CodeBert/demo/checkpoint-best-mrr-solidityKG'
    node_file = '/home/auatac/liao_system/node/node.csv'
    FENs_list_file = '/home/auatac/liao_system/Model/list_of_FENs.npy'
    w2c_array_file = '/home/auatac/liao_system/Model/word2vec_array.npy'
    codebert_array_file = '/home/auatac/liao_system/Model/codebert_array.npy'


    Dict_FEN_to_Vector_object = Dict_FEN_to_Vector(node_file, word2vec_dict_model, codebert_model)
    Dict_FEN_to_Vector_object.FENs_and_embeddings_array(FENs_list_file, w2c_array_file, codebert_array_file)

    #
    # FEN_to_W2C_vector = pd.read_csv('/home/auatac/liao_system/Model/FEN_to_vectors.csv')
    # FEN_list = FEN_to_W2C_vector['FEN'].tolist()
    # word2vec_list = FEN_to_W2C_vector['W2v_Vector'].tolist()
    # codebert_list = FEN_to_W2C_vector['Codebert_Vector'].tolist()
    # word2vec_array = np.zeros((len(word2vec_list), 150))
    # codebert_array = np.zeros((len(codebert_list), 768))
    # for i in tqdm.tqdm(range(len(word2vec_list))):
    #     word2vec_array[i] = np.array(eval(word2vec_list[i]))
    #
    # for i in tqdm.tqdm(range(len(codebert_list))):
    #     codebert_array[i] = np.array(eval(codebert_list[i]))
    # np.save('list_of_FENs.npy', FEN_list)
    # np.save('word2vec_array.npy', word2vec_array)
    # np.save('codebert_array.npy', codebert_array)
    #
