import pandas as pd
from config import configs
import tqdm

class Cooccurrence:
    def __init__(self,configs):
        self.configs = configs
        self.function_clone = pd.read_csv(self.configs.function_clone_file)
        self.function_clone = self.function_clone[[':START_ID', ':END_ID']]
        self.has_function = pd.read_csv(self.configs.has_function_relation_file)
        self.node_information = pd.read_csv(self.configs.node_file)
        self.dict_cooccurrence = {':START_ID': [], ':END_ID': [], ':TYPE': [], 'rate': []}

    def get_contract_entity_by_hasFunction_relation(self,function_FEN):
        contract_FEN = self.has_function[self.has_function[':END_ID'] == function_FEN][':START_ID'].tolist()[0]
        return contract_FEN

    def get_clones_entities_by_similarClone_relation(self,function_FEN):

        list_of_clones = self.function_clone[self.function_clone[':START_ID'] == function_FEN][':END_ID'].to_list()
        return list_of_clones

    def get_function_entities_of_contract(self,contract_FEN):
        list_of_functions_of_contract = []
        functions_of_this_contract = self.has_function[self.has_function[':START_ID'] == contract_FEN]
        for _,row in functions_of_this_contract.iterrows():
            list_or_row = row.tolist()
            function_full_entity_name = list_or_row[1]
            list_of_functions_of_contract.append(function_full_entity_name)

        return list_of_functions_of_contract

    def get_contract_entities_from_clones(self,list_of_clones):

        contract_entities = set()
        for clone in list_of_clones:
            contract_entity = clone.split(':')[0] + ':' + clone.split(':')[1]
            contract_entities.add(contract_entity)
        return contract_entities


    def get_cooccurrence_relations(self):
        print("start to get co-occurrence relations")
        contract_entities = self.node_information[(self.node_information[':LABEL'] == 'Contract')
                                                            | (self.node_information[':LABEL'] == 'Library')]['FEN:ID'].tolist()
        for contract_entity in tqdm.tqdm(contract_entities):
            # print(contract_entity)
            # print(self.dict_pair)
            functions_of_contract = self.get_function_entities_of_contract(contract_entity)
            dict_function_to_contracts = {}

            for function in functions_of_contract:
                function_type = self.node_information[self.node_information['FEN:ID'] == function][':LABEL'].tolist()[0]
                if function_type == 'Abstract_Function':
                    continue
                clones_of_function = self.get_clones_entities_by_similarClone_relation(function)
                if len(clones_of_function) == 0:
                    continue
                set_of_contracts = self.get_contract_entities_from_clones(clones_of_function)
                dict_function_to_contracts[function] = set_of_contracts

            for function in dict_function_to_contracts:
                for other_function in dict_function_to_contracts:
                    if function == other_function:
                        continue

                    set_of_contracts = dict_function_to_contracts[function]
                    set_of_other_contracts = dict_function_to_contracts[other_function]
                    intersection_of_contracts = set_of_contracts & set_of_other_contracts
                    rate = len(intersection_of_contracts) / len(set_of_contracts)
                    # print('function : {}, other function : {}, rate : {}'.format(function,other_function,rate))

                    if rate >= 0.93:
                        self.dict_cooccurrence[':START_ID'].append(function)
                        self.dict_cooccurrence[':END_ID'].append(other_function)
                        self.dict_cooccurrence[':TYPE'].append('Cooccurrence')
                        self.dict_cooccurrence['rate'].append(rate)

                    # #count num
                    # self.dict_pair[':START_ID'].append(function)
                    # self.dict_pair[':END_ID'].append(other_function)
                    # self.dict_pair[':TYPE'].append('Pair')
                    # self.dict_pair['rate'].append(rate)

        df_has_function = pd.DataFrame(self.dict_cooccurrence)
        df_has_function.to_csv(self.configs.cooccurrence_relation, index=0)


if __name__ == '__main__':

    cooccurrence_object = Cooccurrence(configs())
    cooccurrence_object.get_cooccurrence_relations()
