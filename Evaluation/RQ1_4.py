from configs_of_evaluation import configs_RQ
import pandas as pd
import tqdm

class RQ1_4:

    def __init__(self, configs_RQ):
        self.configs_RQ = configs_RQ

        self.dict_functions_with_comments_num = {'Augmented type': [], 'Abstract Function': [], 'Modifier': [],
                                            'Fallback': [], 'Constructor': [], 'Function': [], 'Sum': [],
                                            'Total Functions': [], 'Percentage': []}

    def theNumberOf_Functions_with_noComments(self, node_information, augmented_type):
        Functions = node_information[node_information[":LABEL"] == 'Function']
        Abstract_Function = node_information[node_information[':LABEL'] == 'Abstract_Function']
        Modifier = node_information[node_information[':LABEL'] == 'Modifier']
        Fallback = node_information[node_information[':LABEL'] == 'Fallback']
        Constructor = node_information[node_information[':LABEL'] == 'Constructor']

        Functions_with_Comment = len(Functions) - len(Functions[Functions['Description'] == 'no comment'])
        Abstract_Function_with_Comment = len(Abstract_Function) - len(
            Abstract_Function[Abstract_Function['Description'] == 'no comment'])
        Modifier_with_Comment = len(Modifier) - len(Modifier[Modifier['Description'] == 'no comment'])
        Fallback_with_Comment = len(Fallback) - len(Fallback[Fallback['Description'] == 'no comment'])
        Constructor_with_Comment = len(Constructor) - len(Constructor[Constructor['Description'] == 'no comment'])
        the_sum_numbers_of_all_functions_with_comment = Functions_with_Comment + Abstract_Function_with_Comment + Modifier_with_Comment + Fallback_with_Comment + Constructor_with_Comment

        sum_of_all_functions = len(Functions) + len(Abstract_Function) + len(Modifier) + len(Fallback) + len(Constructor)

        self.dict_functions_with_comments_num['Augmented type'].append(augmented_type)
        self.dict_functions_with_comments_num['Abstract Function'].append(Abstract_Function_with_Comment)
        self.dict_functions_with_comments_num['Modifier'].append(Modifier_with_Comment)
        self.dict_functions_with_comments_num['Fallback'].append(Fallback_with_Comment)
        self.dict_functions_with_comments_num['Constructor'].append(Constructor_with_Comment)
        self.dict_functions_with_comments_num['Function'].append(Functions_with_Comment)
        self.dict_functions_with_comments_num['Sum'].append(the_sum_numbers_of_all_functions_with_comment)
        self.dict_functions_with_comments_num['Total Functions'].append(sum_of_all_functions)
        self.dict_functions_with_comments_num['Percentage'].append(the_sum_numbers_of_all_functions_with_comment/sum_of_all_functions)

    def five_types_of_functions_augmented_with_different_types(self):
        not_augmented = pd.read_csv(self.configs_RQ.RQ1_4_functions_not_augmented_with_comments)
        augmented_by_override = pd.read_csv(self.configs_RQ.RQ1_4_functions_augmented_by_override)
        augmented_by_function_clone = pd.read_csv(self.configs_RQ.RQ1_4_functions_augmented_by_function_clone)
        augmented_by_override_functionClone = pd.read_csv(self.configs_RQ.RQ1_4_functions_augmented_by_override_functionClone)


        self.theNumberOf_Functions_with_noComments(not_augmented, 'not augmented')
        self.theNumberOf_Functions_with_noComments(augmented_by_override, 'augmented by override')
        self.theNumberOf_Functions_with_noComments(augmented_by_function_clone, 'augmented by function clone')
        self.theNumberOf_Functions_with_noComments(augmented_by_override_functionClone, 'augmented by override and function clone')

        DF_dict_functions_with_comments_num = pd.DataFrame(self.dict_functions_with_comments_num)
        DF_dict_functions_with_comments_num.to_csv(self.configs_RQ.RQ1_4_functions_augmented_with_different_types, index=0)

    def comments_of_para_returns_element(self):
        before_propagation = pd.read_csv(self.configs_RQ.RQ1_4_functions_augmented_by_override_functionClone)
        before_propagation_para = before_propagation[before_propagation[':LABEL'].str.contains('Parameter')]
        before_propagation_returns = before_propagation[before_propagation[':LABEL'].str.contains('Returns')]
        before_propagation_element = before_propagation[before_propagation[':LABEL'].str.contains('Element')]

        after_propagation = pd.read_csv(self.configs_RQ.RQ1_4_para_returns_element_augmented)
        after_propagation_para = after_propagation[after_propagation[':LABEL'].str.contains('Parameter')]
        after_propagation_returns = after_propagation[after_propagation[':LABEL'].str.contains('Returns')]
        after_propagation_element = after_propagation[after_propagation[':LABEL'].str.contains('Element')]

        dict_Parameter_Level_completion = {'type': ['Parameter', 'Returns'],
                                           'Nums': [len(before_propagation_para), len(before_propagation_returns)],
                                           'Nums with Comments(Before Propagation)': [],
                                           'Percentage1': [],
                                           'Nums with Comments(After Propagation)': [],
                                           'Percentage2': []}
        # para_nums_with_comment_before_augmentation = before_propagation_para

        #wait for completion

    def functions_are_propagated_with_comments(self):
        pass


if __name__ == '__main__':
    RQ1_4_object = RQ1_4(configs_RQ())
    RQ1_4_object.five_types_of_functions_augmented_with_different_types()
    RQ1_4_object.comments_of_para_returns_element() #wait for completion