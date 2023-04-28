from configs_of_evaluation import configs_RQ
from now_tools import similarity_matrix
import numpy as np
from gensim.models.word2vec import Word2VecKeyedVectors
import tqdm
import pandas as pd
from get_relation.normalize_and_get_vec import normalize_and_get_vec
from sklearn.metrics import cohen_kappa_score


class RQ1_1(normalize_and_get_vec):

    def __init__(self, configs_RQ):
        super().__init__(configs_RQ)
        self.configs_RQ = configs_RQ
        self.RQ1_1_benchmark = pd.read_csv(self.configs_RQ.RQ1_1_benchmark)
        print('benchmark : clone pairs : {}, non-clone pairs : {}'.
              format(self.RQ1_1_benchmark['label'].value_counts()[1], self.RQ1_1_benchmark['label'].value_counts()[0]))

        self.RQ1_1_samples = pd.read_csv(self.configs_RQ.RQ1_1_samples)
        self.W2V_model = Word2VecKeyedVectors.load_word2vec_format(self.configs_RQ.word_2vec_dict_model)
        #RQ1.1
        self.dict_clone_result = {'threshold': [], 'TP': [], 'TN': [], 'FN': [], 'FP': [],
                                  'Recall': [], 'Precision': [], 'F1_Score': []}

    def get_vector(self, function_code):
        function_normalized_token = self.get_normalized_tokens(function_code)
        function_vec = np.zeros(self.configs.word_2vec_dim, )
        for normalized_token in function_normalized_token:
            function_vec += self.W2V_model[normalized_token]

        return function_vec

    def RQ1_1_result(self, threshold):
        TP = 0
        FP = 0
        TN = 0
        FN = 0

        for _, row in self.RQ1_1_benchmark.iterrows():
            function1_code = row['function1 code']
            function2_code = row['function2 code']
            label = row['label']

            function1_vec = self.get_vector(function1_code).reshape(1, self.configs_RQ.word_2vec_dim)
            function2_vec = self.get_vector(function2_code).reshape(1, self.configs_RQ.word_2vec_dim)
            similar_scores = similarity_matrix(function1_vec, function2_vec)[0]
            predict = similar_scores[0]
            if float(predict) >= threshold:
                predict_label = 1
            else:
                predict_label = 0

            if predict_label == 1:
                # predict_label=1,label=1
                if label == 1:
                    TP += 1
                # predict_label=1,label=0
                else:
                    FP += 1
            else:
                # predict_label=0,label=1
                if label == 1:
                    FN += 1
                # predict_label=0,label=0
                else:
                    TN += 1

        Precision = TP/(TP+FP)
        Recall = TP/(TP+FN)
        F1_scores = 2*(Precision*Recall)/(Precision+Recall)
        self.dict_clone_result['threshold'].append(threshold)
        self.dict_clone_result['TP'].append(TP)
        self.dict_clone_result['TN'].append(TN)
        self.dict_clone_result['FN'].append(FN)
        self.dict_clone_result['FP'].append(FP)
        self.dict_clone_result['Precision'].append(Precision)
        self.dict_clone_result['Recall'].append(Recall)
        self.dict_clone_result['F1_Score'].append(F1_scores)

    def RQ_1_1_get_metrics_on_benchmark(self):
        for threshold in tqdm.tqdm(range(0, 100)):
            threshold = threshold/100
            self.RQ1_1_result(threshold)

        df_clone_result = pd.DataFrame(self.dict_clone_result)
        df_clone_result.to_csv(self.configs_RQ.RQ1_1_PRF1_on_benchmark, index=0)

    def RQ_1_1_get_accuracy_on_samples(self):
        accuracy = self.RQ1_1_samples['label'].value_counts()[1]/len(self.RQ1_1_samples)
        print('RQ 1.1 accuracy on the samples : {}'.format(accuracy))


    def RQ1_1_kappa_on_benchmark(self):
        label1 = self.RQ1_1_benchmark['label1'].tolist()
        label2 = self.RQ1_1_benchmark['label2'].tolist()
        kappa_score = cohen_kappa_score(label1, label2)


        print('RQ 1.1 kappa on the benchmark: {}'.format(kappa_score))

    def RQ1_1_kappa_on_samples(self):

        label1 = self.RQ1_1_samples['label1'].tolist()
        label2 = self.RQ1_1_samples['label2'].tolist()
        kappa_score = cohen_kappa_score(label1, label2)

        print('RQ 1.1 kappa on the samples : {}'.format(kappa_score))

if __name__ == '__main__':
    RQ1_1_object = RQ1_1(configs_RQ())
    RQ1_1_object.RQ1_1_kappa_on_benchmark()
    # RQ1_1_object.RQ_1_1_get_metrics_on_benchmark()

    RQ1_1_object.RQ1_1_kappa_on_samples()
    RQ1_1_object.RQ_1_1_get_accuracy_on_samples()
