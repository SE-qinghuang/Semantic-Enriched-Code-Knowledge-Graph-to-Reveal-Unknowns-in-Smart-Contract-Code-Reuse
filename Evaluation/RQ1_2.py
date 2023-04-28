from configs_of_evaluation import configs_RQ
import tqdm
import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score

class RQ1_2:

    def __init__(self, configs_RQ):
        self.configs_RQ = configs_RQ

        self.dict_metrics = {'threshold': [], 'TP': [], 'FP': [], 'TN': [], 'FN': [],
                    'Precision': [], 'Recall': [], 'F1 score': []}
        self.RQ1_2_benchmark = pd.read_csv(self.configs_RQ.RQ1_2_benchmark)
        self.RQ1_2_samples = pd.read_csv(self.configs_RQ.RQ1_2_samples)

    def count_PRF1(self, threshold):
        TP = 0
        FP = 0
        TN = 0
        FN = 0
        for _, row in self.RQ1_2_benchmark.iterrows():
            rate = row['rate']
            if rate >= threshold:
                predict_label = 1
            else:
                predict_label = 0

            label = row['label']
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

        Precision = TP / (TP + FP)
        Recall = TP / (TP + FN)
        F1_scores = 2 * (Precision * Recall) / (Precision + Recall)

        return TP, FP, TN, FN, Precision, Recall, F1_scores


    def RQ1_2_get_metrics_on_benchmarks(self):
        for i in tqdm.tqdm(range(101)):
            threshold = i/100
            TP, FP, TN, FN, Precision, Recall, F1_scores = self.count_PRF1(threshold)
            self.dict_metrics['threshold'].append(threshold)
            self.dict_metrics['TP'].append(TP)
            self.dict_metrics['FP'].append(FP)
            self.dict_metrics['TN'].append(TN)
            self.dict_metrics['FN'].append(FN)
            self.dict_metrics['Precision'].append(Precision)
            self.dict_metrics['Recall'].append(Recall)
            self.dict_metrics['F1 score'].append(F1_scores)
        df_dict_metrics = pd.DataFrame(self.dict_metrics)

        df_dict_metrics.to_csv(self.configs_RQ.RQ1_2_PRF1_on_benchmark, index=0)

    def RQ1_2_kappa_on_benchmark(self):
        label1 = self.RQ1_2_benchmark['label1'].tolist()
        label2 = self.RQ1_2_benchmark['label2'].tolist()
        kappa_score = cohen_kappa_score(label1, label2)


        print('RQ 1.2 kappa on the benchmark: {}'.format(kappa_score))

    def RQ1_2_kappa_on_samples(self):
        label1 = self.RQ1_2_samples['label1'].tolist()
        label2 = self.RQ1_2_samples['label2'].tolist()
        kappa_score = cohen_kappa_score(label1, label2)

        print('RQ 1.2 kappa on the samples : {}'.format(kappa_score))

    def RQ1_2_get_accuracy_on_samples(self):

        accuracy = self.RQ1_2_samples['label'].value_counts()[1]/len(self.RQ1_2_samples)

        print('RQ 1.2 accuracy on the samples : {}'.format(accuracy))


if __name__ == '__main__':
    RQ1_2_object = RQ1_2(configs_RQ())
    RQ1_2_object.RQ1_2_kappa_on_benchmark()
    RQ1_2_object.RQ1_2_get_metrics_on_benchmarks()
    RQ1_2_object.RQ1_2_kappa_on_samples()
    RQ1_2_object.RQ1_2_get_accuracy_on_samples()
