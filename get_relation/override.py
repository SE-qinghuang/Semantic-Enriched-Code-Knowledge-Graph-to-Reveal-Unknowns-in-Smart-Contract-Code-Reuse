from slither import Slither
import pandas as pd
from config import configs
from now_tools import findAllFile,try_get_slither_object_from_sol_file,len_of_directory
import tqdm

class Override:
    def __init__(self,configs):
        self.configs = configs
        self.node_information = pd.read_csv(self.configs.node_file)
        self.length_of_contract_directory = len_of_directory(self.configs.contracts_directory)
        self.dict_override_relation = {':START_ID': [], ':END_ID': [], ':TYPE': []}

    def get_node_type_from_node_name(self,node_name):
        return self.node_information[self.node_information['FEN:ID'] == node_name][':LABEL'].tolist()[0]

    def get_override_relation(self,sol):

        for contract in sol.contracts:
            dict_fullName_to_functions_and_modifiers_inherited = {}
            for function in contract.functions_and_modifiers_inherited:
                dict_fullName_to_functions_and_modifiers_inherited[function.full_name] = function

            for function in contract.functions_and_modifiers_declared:

                if function.full_name in dict_fullName_to_functions_and_modifiers_inherited:

                    inherited_node = dict_fullName_to_functions_and_modifiers_inherited[function.full_name]
                    inherited_node_name = inherited_node.source_mapping['filename_absolute'] + ':' + inherited_node.canonical_name.replace('.',':')
                    inherited_node_type = self.get_node_type_from_node_name(inherited_node_name)
                    if inherited_node_type == 'Abstract_Function':
                        this_node_name = function.source_mapping['filename_absolute'] + ':' + function.canonical_name.replace('.',':')
                        self.dict_override_relation[':START_ID'].append(this_node_name)
                        self.dict_override_relation[':END_ID'].append(inherited_node_name)
                        self.dict_override_relation[':TYPE'].append('override')

    def make_relation_to_csv(self):
        print('start to make override relations into csv')
        df_override = pd.DataFrame(self.dict_override_relation)
        df_override.to_csv(self.configs.override_file, index=0)


    def get_override_relations(self):
        print("start to get override relations...")
        list_of_file = findAllFile(self.configs.contracts_directory)

        for sol_file in tqdm.tqdm(list_of_file,total=self.length_of_contract_directory):
            try:
                if try_get_slither_object_from_sol_file(sol_file):
                    sol = Slither(sol_file)

                    self.get_override_relation(sol)

                else:
                    print('failed to get slither object')
            except:
                f = open('bug_when_get_override_relations.txt', 'a')
                f.writelines(sol_file + '\n')
                f.close()



        self.make_relation_to_csv()

        print('overriding has done')