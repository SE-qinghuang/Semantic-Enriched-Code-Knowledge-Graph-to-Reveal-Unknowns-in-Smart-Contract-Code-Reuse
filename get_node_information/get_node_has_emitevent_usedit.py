from slither.slither import Slither
from get_relation.Flow_Chart import get_dic_function_to_order_sequence_and_emit_event
from get_relation.Call_graph import get_usedit_relation
from now_tools import findAllFile,try_get_slither_object_from_sol_file,get_function_code
import pandas as pd
import re
from config import configs
from get_comment import get_dict_function_to_comment_and_description

class get_node_information():

    def __init__(self,configs):
        self.configs = configs
        self.list_of_file = findAllFile(configs.contracts_directory)

        #node information
        self.dict_node_to_type = {'name': [], 'type': []}
        self.dict_node_to_comment = {'name': [], 'comment': []}
        self.dict_node_to_description_sentence = {'name': [], 'description sentence': []}
        self.dict_node_to_function_code = {'name': [], 'function code': []}
        self.dict_node_to_order_sequence = {'name': [], 'order sequence': []}
        self.dict_node_to_composition_count = {'name': [], 'Times of participating in combination': []}
        # self.dict_keywords = {'name': [], 'keywords': []}
        self.description_and_source_of_specific_variables = {'name': [], 'description and source of specific variables': []}

        #relation
        self.dict_emit_event = {'name pre': [],'name next': [],'relation': []}
        self.dict_calls = {'name pre': [],'name next': [],'relation': []}
        self.dict_has_function = {'name pre': [],'name next': [],'relation': []}
        self.dict_has_event = {'name pre': [],'name next': [],'relation': []}

        #function patterns
        # end is {}
        self.abstract_function_pattern1 = re.compile("[\s\S]*\{\s+\}")
        self.abstract_function_pattern2 = re.compile("[\s\S]*\{\}")

        # end is ;
        self.abstract_function_pattern3 = re.compile("[\s\S]*\([\s\S]*\)\s*;$")
        self.abstract_function_pattern4 = re.compile("[\s\S]*\([\s\S]*\)\s*;\s+$")

    def get_contract_information(self,contract):

        file_path = contract.source_mapping['filename_absolute']

        # contract node information
        node_name = file_path + ':' + str(contract)
        node_type = contract.kind
        # node_comment = get_comment()
        node_comment = 'contract comment'
        node_description = ''
        node_function_code = 'contract has no function code'
        node_function_order_sequence = 'contract has no order sequence'
        node_composition_count = 'contract has no combination'
        node_Description_and_source_of_specific_variables = ''

        #node to type
        self.dict_node_to_type['name'].append(node_name)
        self.dict_node_to_type['type'].append(node_type)

        #node to comment
        self.dict_node_to_comment['name'].append(node_name)
        self.dict_node_to_comment['comment'].append(node_comment)

        #node to description sentence
        self.dict_node_to_description_sentence['name'].append(node_name)
        self.dict_node_to_description_sentence['description sentence'].append(node_description)

        #node to function code
        self.dict_node_to_function_code['name'].append(node_name)
        self.dict_node_to_function_code['function code'].append(node_function_code)

        #node to function order sequence
        self.dict_node_to_order_sequence['name'].append(node_name)
        self.dict_node_to_order_sequence['order sequence'].append(node_function_order_sequence)

        #node to node_composition_count
        self.dict_node_to_composition_count['name'].append(node_name)
        self.dict_node_to_composition_count['Times of participating in combination'].append(node_composition_count)


        #node to Description and source of specific variables
        self.description_and_source_of_specific_variables['name'].append(node_name)
        self.description_and_source_of_specific_variables['description and source of specific variables'].append(node_Description_and_source_of_specific_variables)

    def get_function_type(self,function_code):
        if self.abstract_function_pattern1.match(function_code):
            node_type = 'abstract function'
        elif self.abstract_function_pattern2.match(function_code):
            node_type = 'abstract function'
        elif self.abstract_function_pattern3.match(function_code):
            node_type = 'abstract function'
        elif self.abstract_function_pattern4.match(function_code):
            node_type = 'abstract function'
        else:
            node_type = 'function'

        return node_type

    def get_function_inforamtion(self,function,dic_function_to_order_sequence,dict_function_to_comment,dict_function_to_description):

        file_path = function.source_mapping['filename_absolute']
        if (function.function_type == 'CONSTRUCTOR_VARIABLES') | (
                function.name == 'slitherConstructorConstantVariables') | (
                function.name == 'slitherConstructorVariables'):
            pass
        else:
            mapping_dict = function.source_mapping
            function_lines = mapping_dict["lines"]

            node_function_code = get_function_code(file_path, function_lines)
            node_type = self.get_function_type(node_function_code)
            node_name = file_path + ':' + function.canonical_name.replace('.', ':')

            node_description = dict_function_to_description[node_name]
            node_comment = dict_function_to_comment[node_name]
            node_Description_and_source_of_specific_variables = ''

            if node_type == 'abstract function':
                node_composition_count = 'abstract function has no combination'
            else:
                node_composition_count = ''



            # node_function_order_sequence = get_order_sequence()
            if node_name in dic_function_to_order_sequence:
                node_function_order_sequence = dic_function_to_order_sequence[node_name]
            else:
                node_function_order_sequence = 'error_when_get_function_order_sequence'

            # node to type
            self.dict_node_to_type['name'].append(node_name)
            self.dict_node_to_type['type'].append(node_type)

            # node to comment
            self.dict_node_to_comment['name'].append(node_name)
            self.dict_node_to_comment['comment'].append(node_comment)

            # node to description sentence
            self.dict_node_to_description_sentence['name'].append(node_name)
            self.dict_node_to_description_sentence['description sentence'].append(node_description)

            # node to function code
            self.dict_node_to_function_code['name'].append(node_name)
            self.dict_node_to_function_code['function code'].append(node_function_code)

            # node to function order sequence
            self.dict_node_to_order_sequence['name'].append(node_name)
            self.dict_node_to_order_sequence['order sequence'].append(node_function_order_sequence)

            # node to node_composition_count
            self.dict_node_to_composition_count['name'].append(node_name)
            self.dict_node_to_composition_count['Times of participating in combination'].append(
                node_composition_count)

            # node to Description and source of specific variables
            self.description_and_source_of_specific_variables['name'].append(node_name)
            self.description_and_source_of_specific_variables['description and source of specific variables'].append(
                node_Description_and_source_of_specific_variables)

    def get_event_information(self,event):

        file_path = event.source_mapping['filename_absolute']

        # node information
        node_type = 'event'
        # node_name = file_path + ':' + str(contract_name) + ':' + event.full_name
        node_name = file_path + ':' + event.canonical_name.replace('.', ':')
        node_comment = 'event comment'
        node_description = ''
        node_composition_count = 'event has no combination'
        node_Description_and_source_of_specific_variables = ''
        node_function_code = 'event has no function code'
        node_function_order_sequence = 'event has no function order sequence'

        # node to type
        self.dict_node_to_type['name'].append(node_name)
        self.dict_node_to_type['type'].append(node_type)

        # node to comment
        self.dict_node_to_comment['name'].append(node_name)
        self.dict_node_to_comment['comment'].append(node_comment)

        # node to description sentence
        self.dict_node_to_description_sentence['name'].append(node_name)
        self.dict_node_to_description_sentence['description sentence'].append(node_description)

        # node to function code
        self.dict_node_to_function_code['name'].append(node_name)
        self.dict_node_to_function_code['function code'].append(node_function_code)

        # node to function order sequence
        self.dict_node_to_order_sequence['name'].append(node_name)
        self.dict_node_to_order_sequence['order sequence'].append(node_function_order_sequence)

        # node to node_composition_count
        self.dict_node_to_composition_count['name'].append(node_name)
        self.dict_node_to_composition_count['Times of participating in combination'].append(
            node_composition_count)

        # node to Description and source of specific variables
        self.description_and_source_of_specific_variables['name'].append(node_name)
        self.description_and_source_of_specific_variables['description and source of specific variables'].append(
            node_Description_and_source_of_specific_variables)

    def make_information_into_csv_file(self):

        df_node_to_type = pd.DataFrame(self.dict_node_to_type)
        df_node_to_type.to_csv(self.configs.node_to_type_file, index=0)

        df_node_to_comment = pd.DataFrame(self.dict_node_to_comment)
        df_node_to_comment.to_csv(self.configs.node_to_comment_file, index=0)

        df_node_to_description_sentence = pd.DataFrame(self.dict_node_to_description_sentence)
        df_node_to_description_sentence.to_csv(self.configs.node_to_description_file, index=0)

        df_node_to_function_code = pd.DataFrame(self.dict_node_to_function_code)
        df_node_to_function_code.to_csv(self.configs.node_to_function_code_file, index=0)

        df_node_to_order_sequence = pd.DataFrame(self.dict_node_to_order_sequence)
        df_node_to_order_sequence.to_csv(self.configs.node_to_order_sequence, index=0)

        df_node_to_composition_count = pd.DataFrame(self.dict_node_to_composition_count)
        df_node_to_composition_count.to_csv(self.configs.node_to_composition_count_file, index=0)

        # df_keywords = pd.DataFrame(self.dict_keywords)
        # df_keywords.to_csv(self.configs.keywords_file, index=0)

        df_description_and_source_of_specific_variables = pd.DataFrame(self.description_and_source_of_specific_variables)
        df_description_and_source_of_specific_variables.to_csv(self.configs.description_and_source_of_specific_variables_file, index=0)

        df_emit_event = pd.DataFrame(self.dict_emit_event)
        df_emit_event.to_csv(self.configs.emit_event_relation_file, index=0)

        df_calls = pd.DataFrame(self.dict_calls)
        df_calls.to_csv(self.configs.calls_relation_file, index=0)

        df_has_function = pd.DataFrame(self.dict_has_function)
        df_has_function.to_csv(self.configs.has_function_relation_file, index=0)

        df_has_event = pd.DataFrame(self.dict_has_event)
        df_has_event.to_csv(self.configs.has_event_relation_file, index=0)

    def get_emit_event_relation(self,function_emit_event_relation):
        # get emit event relation
        relation = 'Emit Event'
        for function_name in function_emit_event_relation:
            events_set = function_emit_event_relation[function_name]
            if len(events_set) > 0:
                for event in events_set:
                    self.dict_emit_event['name pre'].append(function_name)
                    self.dict_emit_event['name next'].append(event)
                    self.dict_emit_event['relation'].append(relation)

    def get_calls_relation(self,list_of_calls_relations):
        for list_of_calls_ralation in list_of_calls_relations:
            name_pre = list_of_calls_ralation[0]
            name_next = list_of_calls_ralation[1]
            relation = list_of_calls_ralation[2]

            self.dict_calls['name pre'].append(name_pre)
            self.dict_calls['name next'].append(name_next)
            self.dict_calls['relation'].append(relation)

    def get_has_function_relation(self,contract,function):
        contract_file_path = contract.source_mapping['filename_absolute']
        function_file_path = function.source_mapping['filename_absolute']

        contract_name = contract_file_path + ':' + str(contract)

        function_name = function_file_path + ':' + str(contract)
        self.dict_has_function['name pre'].append(contract_name)
        self.dict_has_function['name next'].append(function_name)
        self.dict_has_function['relation'].append('has function')

    def get_has_event_relation(self,contract,event):

        contract_file_path = contract.source_mapping['filename_absolute']
        event_file_path = event.source_mapping['filename_absolute']

        contract_name = contract_file_path + ':' + str(contract)

        event_name = event_file_path + ':' + str(contract)
        self.dict_has_event['name pre'].append(contract_name)
        self.dict_has_event['name next'].append(event_name)
        self.dict_has_event['relation'].append('has event')

    def get_informations(self):

        i = 0

        for file in self.list_of_file:
            print(file)
            print('now handling the no.{} file'.format(i))
            i += 1
            # success to get a slither object
            if try_get_slither_object_from_sol_file(file):
                # try:
                    slither = Slither(file)
                    print('success to get slither object')

                    dict_function_to_comment,dict_function_to_description = get_dict_function_to_comment_and_description(slither,file)


                    # get the dict {function:order_sequence} in sol file
                    dic_function_to_order_sequence, function_emit_event_relation = get_dic_function_to_order_sequence_and_emit_event(slither,dict_function_to_description)

                    #emit event relation
                    self.get_emit_event_relation(function_emit_event_relation)

                    #used it relation
                    list_of_calls_relations = get_usedit_relation(file)
                    self.get_calls_relation(list_of_calls_relations)



                    contracts_list = slither.contracts
                    for contract in contracts_list:

                        self.get_contract_information(contract)

                        for function in contract.functions_and_modifiers_declared:

                            self.get_has_function_relation(contract,function)
                            self.get_function_inforamtion(function,dic_function_to_order_sequence,dict_function_to_comment,dict_function_to_description)

                        for event in contract.events_declared:
                            self.get_has_event_relation(contract,event)
                            self.get_event_information(event)

                # except:
                #     f = open(self.configs.bug_file,'a')
                #     f.writelines(file + '\n')
                #     f.close()
            else:
                print('failed to get slither object')

        self.make_information_into_csv_file()


if __name__ == '__main__':
    information_class = get_node_information(configs())
    information_class.get_informations()

