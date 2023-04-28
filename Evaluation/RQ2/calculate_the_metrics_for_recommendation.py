import pandas as pd
import math
class metrics:

    def __init__(self, result_file, saved_metrics_file):

        self.saved_metrics_file = saved_metrics_file
        self.relax_result_list, self.strict_result_list = self.handle_the_result_file(result_file)
        self.metrics = {}


    def handle_the_result_file(self, result_file):

        relax_result_list = []
        f = open(result_file)
        list_of_lines = f.readlines()
        for line in list_of_lines:
            line = line.strip()
            relax_result_list.append(eval(line))


        strict_result_list = []
        for relax_result in relax_result_list:
            strict_result = [0 if i == 1 else i for i in relax_result]
            strict_result_list.append(strict_result)

        return relax_result_list, strict_result_list

    def Precision(self, result_list, Hit_type):

        precision_socres = []
        for result in result_list:
            irrelevant_num = result.count(0)
            relevant_num = len(result) - irrelevant_num
            precision_socre = relevant_num / len(result)
            precision_socres.append(precision_socre)

        self.metrics[Hit_type] = precision_socres

    def DCG_score(self, DCG_list):
        DCGScore = 0
        i = 1
        for rel_score in DCG_list:
            i_score = rel_score / math.log2(i + 1)
            DCGScore += i_score
            i += 1
        return DCGScore

    def NDCG_score(self, result):
        best_DCG_list = sorted(result, reverse=True)
        DCGScore = self.DCG_score(result)
        iDCGScore = self.DCG_score(best_DCG_list)
        NDCGScore = DCGScore / iDCGScore
        return NDCGScore

    def NDCG_scores(self, result_list, NDCG_type):
        NDCG_scores = []
        for result in result_list:
            try:
                NDCG_score = self.NDCG_score(result)
            except:
                NDCG_score = 0
            NDCG_scores.append(NDCG_score)
        self.metrics[NDCG_type] = NDCG_scores


    def get_metrics(self):
        self.Precision(self.relax_result_list, 'Hit 5 Relaxed')
        self.Precision(self.strict_result_list, 'Hit 5 Strict')
        self.NDCG_scores(self.relax_result_list, 'NDCG Relaxed')
        self.NDCG_scores(self.strict_result_list, 'NDCG Strict')

        df_metrics = pd.DataFrame(self.metrics)
        df_metrics.to_csv(self.saved_metrics_file, index=0)

if __name__ == '__main__':

    # result_file = 'CodeBert/recommendation_results/CodeBert_Incremented_Of_Solidity_BaselineKG'
    # saved_metrics_file = 'CodeBert/recommendation_metrics/CodeBert_Incremented_Of_Solidity_BaselineKG_metrics.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()
    #
    # result_file = 'CodeBert/recommendation_results/CodeBert_Enriched_Comment'
    # saved_metrics_file = 'CodeBert/recommendation_metrics/CodeBert_Enriched_Comment_metrics.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()
    #
    # result_file = 'CodeBert/recommendation_results/CodeBert_Enriched_Comment_Clone'
    # saved_metrics_file = 'CodeBert/recommendation_metrics/CodeBert_Enriched_Comment_Clone_metrics.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()
    #
    # result_file = 'CodeBert/recommendation_results/CodeBert_Enriched_Comment_Composition_Count'
    # saved_metrics_file = 'CodeBert/recommendation_metrics/CodeBert_Enriched_Comment_Composition_Count_metrics.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()

    # result_file = 'BM25/recommendation_results/BM25_basic_comment'
    # saved_metrics_file = 'BM25/recommendation_metrics/BM25_basic_comment.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()
    #
    # result_file = 'BM25/recommendation_results/BM25_AD_FC'
    # saved_metrics_file = 'BM25/recommendation_metrics/BM25_AD_FC.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()
    #
    # result_file = 'BM25/recommendation_results/BM25_AD_FC_Clone'
    # saved_metrics_file = 'BM25/recommendation_metrics/BM25_AD_FC_Clone.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()
    #
    # result_file = 'BM25/recommendation_results/BM25_AD_FC_Clone_CC'
    # saved_metrics_file = 'BM25/recommendation_metrics/BM25_AD_FC_Clone_CC.csv'
    # metrics_object = metrics(result_file, saved_metrics_file)
    # metrics_object.get_metrics()

    result_file = 'DeepCodeSearch/recommendation_results/DCS_Solidity_BaselineKG'
    saved_metrics_file = 'DeepCodeSearch/recommendation_metrics/DCS_Solidity_BaselineKG_metrics.csv'
    metrics_object = metrics(result_file, saved_metrics_file)
    metrics_object.get_metrics()

    result_file = 'DeepCodeSearch/recommendation_results/DCS_Enriched_Comment'
    saved_metrics_file = 'DeepCodeSearch/recommendation_metrics/DCS_Enriched_Comment_metrics.csv'
    metrics_object = metrics(result_file, saved_metrics_file)
    metrics_object.get_metrics()

    result_file = 'DeepCodeSearch/recommendation_results/DCS_Enriched_Comment_Clone'
    saved_metrics_file = 'DeepCodeSearch/recommendation_metrics/DCS_Enriched_Comment_Clone_metrics.csv'
    metrics_object = metrics(result_file, saved_metrics_file)
    metrics_object.get_metrics()

    result_file = 'DeepCodeSearch/recommendation_results/DCS_Enriched_Comment_Clone_CC'
    saved_metrics_file = 'DeepCodeSearch/recommendation_metrics/DCS_Enriched_Comment_Clone_CC_metrics.csv'
    metrics_object = metrics(result_file, saved_metrics_file)
    metrics_object.get_metrics()
