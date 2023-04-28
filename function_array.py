import numpy as np
from get_relation.function_clone import function_clone
import tqdm
from config import configs
from now_tools import get_vector
from gensim.models.word2vec import Word2VecKeyedVectors

class get_function_array(function_clone):

    def __init__(self, configs):
        function_clone.__init__(self, configs)
        self.configs = configs
        self.model = Word2VecKeyedVectors.load_word2vec_format('/home/auatac/liao_system/Recommendation_Baseline/deepAPI-master/pytorch/data/word2vec_model_for_deepapi.bin')

    def get_function_array(self):
        functions_df = self.get_functions_df()

        vec_array = np.zeros((len(functions_df), 150))
        list_of_FENs = []
        i = 0
        for _, row in tqdm.tqdm(functions_df.iterrows(), total=functions_df.shape[0]):
            FEN = row['FEN:ID']
            function_code = row['Function_Code'].replace('\\n', '\n')


            function_vec = get_vector(function_code, self.model)


            vec_array[i] = function_vec
            list_of_FENs.append(FEN)

            i += 1

        np.save('Model/function_array_for_deepAPI.npy', vec_array)
        np.save('Model/list_of_FENs.npy', np.array(list_of_FENs))

if __name__ == '__main__':
    get_function_array_object = get_function_array(configs())
    get_function_array_object.get_function_array()
