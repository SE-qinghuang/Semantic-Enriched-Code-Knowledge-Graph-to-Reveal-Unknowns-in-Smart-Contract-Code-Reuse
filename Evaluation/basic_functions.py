import numpy as np
import pandas as pd

def count_precision_recall_f1(test_data, threshold):
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for _, row in test_data.iterrows():
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


def del_the_FENs(df_datas):
    datas_after_deling_the_FENs = {'function1 code': [], 'function2 code': [], 'function1 FEN': [], 'function2 FEN': [],
                        'label1': [], 'label2': [], 'label': []}
    for _, row in df_datas.iterrows():
        a = 1
        function1_FEN = row['function1 FEN'].replace('/home/auatac/liao_system/contracts/','')
        function2_FEN = row['function2 FEN'].replace('/home/auatac/liao_system/contracts/','')

        datas_after_deling_the_FENs['function1 FEN'].append(function1_FEN)
        datas_after_deling_the_FENs['function2 FEN'].append(function2_FEN)
        datas_after_deling_the_FENs['function1 code'].append(row['function1 code'])
        datas_after_deling_the_FENs['function2 code'].append(row['function2 code'])
        datas_after_deling_the_FENs['label1'].append(row['label1'])
        datas_after_deling_the_FENs['label2'].append(row['label2'])
        datas_after_deling_the_FENs['label'].append(row['label'])

    df_datas_after_deling_the_FENs = pd.DataFrame(datas_after_deling_the_FENs)
    return df_datas_after_deling_the_FENs


# def kappa(confusion_matrix):
#     """计算kappa值系数"""
#     pe_rows = np.sum(confusion_matrix, axis=0)
#     pe_cols = np.sum(confusion_matrix, axis=1)
#     sum_total = sum(pe_cols)
#     pe = np.dot(pe_rows, pe_cols) / float(sum_total ** 2)
#     po = np.trace(confusion_matrix) / float(sum_total)
#     return (po - pe) / (1 - pe)
#
# def get_kappa(df_datas):
#     matrix = np.array([[0, 0],
#                        [0, 0]])
#
#     for _, row in df_datas.iterrows():
#
#         label1 = int(row['label1'])
#         label2 = int(row['label2'])
#         matrix[label1][label2] += 1
#
#     kappa_score = kappa(matrix)
#     print('kappa : {}'.format(kappa_score))