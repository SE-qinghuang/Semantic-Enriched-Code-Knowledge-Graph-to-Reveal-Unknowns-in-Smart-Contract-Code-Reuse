from configs_of_evaluation import configs_RQ
import pandas as pd
import tqdm


class RQ1_3:

    def __init__(self, configs_RQ):
        self.configs_RQ = configs_RQ

    def get_functions(self, df):
        functions = df[(df[':LABEL'] == 'Function')
                       | (df[':LABEL'] == 'Constructor')
                       | (df[':LABEL'] == 'Modifier')
                       | (df[':LABEL'] == 'Fallback')]
        return functions

    def simplify_FEN(self, FEN):
        FEN = '0x' + FEN.split('/0x')[-1]
        return FEN

    def functions_with_composition_count_before_and_after_accumulation(self):
        # CC : composition count
        CC_before_accumulation = self.get_functions(pd.read_csv(self.configs_RQ.RQ1_3_CC_before_accumulation))
        CC_after_accumulation = self.get_functions(pd.read_csv(self.configs_RQ.RQ1_3_CC_after_accumulation))
        merged_functions = pd.merge(CC_before_accumulation, CC_after_accumulation, on=['FEN:ID'])
        functions = {'FEN:ID': [], 'function code': [], 'composition count before accumulation': [],
                     'composition count after accumulation': []}

        for _, row in tqdm.tqdm(merged_functions.iterrows(), total=merged_functions.shape[0]):
            FEN = self.simplify_FEN(row['FEN:ID'])
            function_code = row['Function_Code_x']
            composition_count_before_accumulation = row['Composition_Count_x']
            composition_count_after_accumulation = row['Composition_Count_y']
            functions['FEN:ID'].append(FEN)
            functions['function code'].append(function_code)
            functions['composition count before accumulation'].append(
                composition_count_before_accumulation)
            functions['composition count after accumulation'].append(
                composition_count_after_accumulation)

        df_functions = pd.DataFrame(functions)
        df_functions.to_csv(self.configs_RQ.RQ1_3_CC_before_and_after_accumulation, index=0)

    def get_CC_to_arange_times(self, dict_function_CC):
        dict_CC_to_times = {'[0,10)': 0, '[10,20)': 0, '[20,30)': 0, '[30,40)': 0, '[40,50)': 0, '[50,60)': 0,
                        '[60,70)': 0, '[70,100)': 0, '[100,1000)': 0, '[1000,2000)': 0, '[2000,3000)': 0,
                        '[3000,4000)': 0, '[4000,5000)': 0, '[5000,6000)': 0, '[6000, 6000+': 0}

        for CC in dict_function_CC:

            if (int(CC) >= 0) & (int(CC) < 10):
                dict_CC_to_times['[0,10)'] += dict_function_CC[CC]
            elif (int(CC) >= 10) & (int(CC) < 20):
                dict_CC_to_times['[10,20)'] += dict_function_CC[CC]
            elif (int(CC) >= 20) & (int(CC) < 30):
                dict_CC_to_times['[20,30)'] += dict_function_CC[CC]
            elif (int(CC) >= 30) & (int(CC) < 40):
                dict_CC_to_times['[30,40)'] += dict_function_CC[CC]
            elif (int(CC) >= 40) & (int(CC) < 50):
                dict_CC_to_times['[40,50)'] += dict_function_CC[CC]
            elif (int(CC) >= 50) & (int(CC) < 60):
                dict_CC_to_times['[50,60)'] += dict_function_CC[CC]
            elif (int(CC) >= 60) & (int(CC) < 70):
                dict_CC_to_times['[60,70)'] += dict_function_CC[CC]
            elif (int(CC) >= 70) & (int(CC) < 100):
                dict_CC_to_times['[70,100)'] += dict_function_CC[CC]
            elif (int(CC) >= 100) & (int(CC) < 1000):
                dict_CC_to_times['[100,1000)'] += dict_function_CC[CC]
            elif (int(CC) >= 1000) & (int(CC) < 2000):
                dict_CC_to_times['[1000,2000)'] += dict_function_CC[CC]
            elif (int(CC) >= 2000) & (int(CC) < 3000):
                dict_CC_to_times['[2000,3000)'] += dict_function_CC[CC]
            elif (int(CC) >= 3000) & (int(CC) < 4000):
                dict_CC_to_times['[3000,4000)'] += dict_function_CC[CC]
            elif (int(CC) >= 4000) & (int(CC) < 5000):
                dict_CC_to_times['[4000,5000)'] += dict_function_CC[CC]
            elif (int(CC) >= 5000) & (int(CC) < 6000):
                dict_CC_to_times['[5000,6000)'] += dict_function_CC[CC]
            elif (int(CC) >= 6000):
                dict_CC_to_times['[6000, 6000+'] += dict_function_CC[CC]
        return dict_CC_to_times
        
    def count_CC_in_different_ranges(self):
        CC_before_and_after_accumulation = pd.read_csv(self.configs_RQ.RQ1_3_CC_before_and_after_accumulation)
        CC_before_accumulation = CC_before_and_after_accumulation['composition count before accumulation'].value_counts().to_dict()
        CC_after_accumulation = CC_before_and_after_accumulation['composition count after accumulation'].value_counts().to_dict()
        
        dict_CC_to_times_before_accumulation = self.get_CC_to_arange_times(CC_before_accumulation)
        dict_CC_to_times_after_accumulation = self.get_CC_to_arange_times(CC_after_accumulation)
        
        dict_CC_to_times_before_and_after_accumulation = {'compisition count': [], 'calls': [], 'percentage1': [],
                                                          'calls + function clone': [], 'percentage2': []}
        num_of_functions = len(CC_before_and_after_accumulation)
        for key, value in dict_CC_to_times_before_accumulation.items():
            CC_times_before_accumulation= dict_CC_to_times_before_accumulation[key]
            CC_times_after_accumulation = dict_CC_to_times_after_accumulation[key]
            percentage1 = CC_times_before_accumulation/num_of_functions
            percentage2 = CC_times_after_accumulation/num_of_functions
            dict_CC_to_times_before_and_after_accumulation['compisition count'].append(key)
            dict_CC_to_times_before_and_after_accumulation['calls'].append(CC_times_before_accumulation)
            dict_CC_to_times_before_and_after_accumulation['percentage1'].append(percentage1)
            dict_CC_to_times_before_and_after_accumulation['percentage2'].append(percentage2)
            dict_CC_to_times_before_and_after_accumulation['calls + function clone'].append(CC_times_after_accumulation)
        df_CC_to_times_before_and_after_accumulation = pd.DataFrame(dict_CC_to_times_before_and_after_accumulation)
        df_CC_to_times_before_and_after_accumulation.to_csv(self.configs_RQ.RQ1_3_CC_changes_in_different_ranges, index=0)

    def count_nums_of_function_increased_with_composition_count(self):
        CC_before_and_after_accumulation = pd.read_csv(self.configs_RQ.RQ1_3_CC_before_and_after_accumulation)
        functions_are_increased_with_CC = CC_before_and_after_accumulation[CC_before_and_after_accumulation['composition count before accumulation']
                                                                           < CC_before_and_after_accumulation['composition count after accumulation']]

        print('increased nums : {}'.format(len(functions_are_increased_with_CC)))
        print('the percentage of increased composition count : {}'.format(len(functions_are_increased_with_CC)/len(CC_before_and_after_accumulation)))
        functions_are_increased_with_CC.to_csv(self.configs_RQ.RQ1_3_functions_are_increased_with_CC, index=0)


if __name__ == '__main__':
    RQ1_3_object = RQ1_3(configs_RQ())
    RQ1_3_object.functions_with_composition_count_before_and_after_accumulation()
    RQ1_3_object.count_CC_in_different_ranges()
    RQ1_3_object.count_nums_of_function_increased_with_composition_count()