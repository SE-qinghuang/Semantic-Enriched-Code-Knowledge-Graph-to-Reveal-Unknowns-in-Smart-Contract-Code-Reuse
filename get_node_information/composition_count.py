import pandas as pd
import tqdm
from config import configs

class composition_count():
    def __init__(self,configs):
        self.configs = configs

    def get_composition_count_from_calls_relation(self,node_file,calls_relation_file):
        node_information = pd.read_csv(node_file)
        functions = node_information[(node_information[':LABEL'] == 'Function')
                                     | (node_information[':LABEL'] == 'Constructor')
                                     | (node_information[':LABEL'] == 'Modifier')
                                     | (node_information[':LABEL'] == 'Fallback')]

        node_name_and_participating_times = functions[['FEN:ID','Composition_Count']]
        node_name_and_participating_times['Composition_Count'] = 0
        node_name_and_participating_times.set_index('FEN:ID', inplace=True)
        dic_function_to_times_of_participating = node_name_and_participating_times.to_dict()['Composition_Count']
        calls_relation = pd.read_csv(calls_relation_file)

        for index, row in tqdm.tqdm(calls_relation.iterrows(),total=calls_relation.shape[0]):
            list_of_row = row.tolist()
            name_pre = list_of_row[0]
            name_next = list_of_row[1]
            #check node is not solidity api
            if '/' in name_next:
                try:
                    dic_function_to_times_of_participating[name_next] += 1
                except:
                    node_type = node_information[node_information['FEN:ID'] == name_next][':LABEL'].tolist()[0]
                    f = open('error_when_getting_Composition_Count.txt','a')
                    f.writelines('{}\t{}\n'.format(name_next, node_type))
                    f.close()
        for function_name, participating_times in tqdm.tqdm(dic_function_to_times_of_participating.items()):
            node_information.loc[
                                node_information['FEN:ID'] == function_name, ('Composition_Count')] = participating_times

        return node_information

    def get_composition_count_from_function_clone(self,node_information):
        functions = node_information[(node_information[':LABEL'] == 'Function')
                                     | (node_information[':LABEL'] == 'Constructor')
                                     | (node_information[':LABEL'] == 'Modifier')
                                     | (node_information[':LABEL'] == 'Fallback')]

        node_name_and_participating_times = functions[['FEN:ID', 'Composition_Count']]
        node_name_and_participating_times.set_index('FEN:ID',inplace=True)
        dic_function_to_times_of_participating = node_name_and_participating_times.to_dict()['Composition_Count']

        dict_node_name_to_participating_times = node_name_and_participating_times.to_dict()['Composition_Count']
        function_clone_relation = pd.read_csv(self.configs.function_clone_file)

        for _, row in tqdm.tqdm(function_clone_relation.iterrows(),total=function_clone_relation.shape[0]):
            list_of_row = row.tolist()
            name_pre = list_of_row[0]
            name_next = list_of_row[1]
            next_node_participating_times = dic_function_to_times_of_participating[name_next]
            dict_node_name_to_participating_times[name_pre] += next_node_participating_times


        return dict_node_name_to_participating_times

    def get_composition_count(self):
        print('start to get times of participating times')
        node_information = self.get_composition_count_from_calls_relation(self.configs.node_file,self.configs.calls_relation_file)
        node_information.to_csv('saved_datas/node_information_after_get_composition_count_from_calls_relation.csv',index=0)
        dict_node_name_to_participating_times = self.get_composition_count_from_function_clone(node_information)

        for node_name, participating_times in tqdm.tqdm(dict_node_name_to_participating_times.items()):
            node_information.loc[
                        node_information['FEN:ID'] == node_name, ('Composition_Count')] = participating_times
        node_information.to_csv(self.configs.node_file, index=0)

        node_information.to_csv(self.configs.saved_information_directory + 'node_information_after_getting_Composition_Count.csv',index=0)


if __name__ == '__main__':

    times_of_participatig_in_combination_object = composition_count(configs())
    times_of_participatig_in_combination_object.get_composition_count()
