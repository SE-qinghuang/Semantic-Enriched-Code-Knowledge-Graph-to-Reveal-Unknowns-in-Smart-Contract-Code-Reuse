from slither.slither import Slither
from now_tools import findAllFile, try_get_slither_object_from_sol_file, get_function_code, get_cfg, len_of_directory
from config import configs
import pandas as pd
from get_relation.Call_graph import get_Calls_relation
import tqdm


class Basic_node_and_relations():

    def __init__(self, configs):
        self.configs = configs
        self.list_of_file = findAllFile(self.configs.contracts_directory)
        self.length_of_contract_directory = len_of_directory(self.configs.contracts_directory)
        self.set_of_solidity_api = set()
        self.node_information = {'FEN:ID': [], ':LABEL': [], 'Data_Type': [],
                                 'Description': [], 'Function_Code': [],
                                 'Composition_Count': [],'Flow_Chart': [], 'CFG': []}

        # has relation
        self.dict_has_Variable = {':START_ID': [], ':END_ID': [], ':TYPE': []}
        self.dict_has_function = {':START_ID': [], ':END_ID': [], ':TYPE': []}
        self.dict_has_event = {':START_ID': [], ':END_ID': [], ':TYPE': []}

        self.dict_has_Struct = {':START_ID': [], ':END_ID': [], ':TYPE': []}
        self.dict_has_Enum = {':START_ID': [], ':END_ID': [], ':TYPE': []}
        self.dict_has_para = {':START_ID': [], ':END_ID': [], ':TYPE': []}
        self.dict_has_returns = {':START_ID': [], ':END_ID': [], ':TYPE': []}
        self.dict_has_element = {':START_ID': [], ':END_ID': [], ':TYPE': []}
        self.dict_calls = {':START_ID': [],':END_ID': [],':TYPE': []}

    # get the text between line1 and line2
    def get_string_between_line1_and_line2(self, list_of_lines, line1, line2):
        line1_index = line1 - 1
        line2_index = line2 - 1

        string_of_text = ''
        for line_index in range(line1_index, line2_index):
            string_of_text += list_of_lines[line_index]
        if len(string_of_text.strip()) == 0:
            string_of_text = 'no comment'
        if string_of_text == '':
            string_of_text = 'no comment'

        return string_of_text

    def get_function_type(self, function):

        if (len(function.nodes) == 0) | (len(function.nodes) == 1):
            node_type = 'Abstract_Function'
        else:
            node_type = 'Function'

        return node_type

    def get_list_of_items(self, contract):
        variable_list = contract.state_variables_declared
        enum_list = contract.enums_declared
        structure_list = contract.structures_declared
        event_list = contract.events_declared

        function_list = contract.functions_and_modifiers_declared

        list_of_items = variable_list + enum_list + structure_list + event_list + function_list
        return list_of_items

    def sort_by_line_number(self, list_of_items):
        item_and_first_line_number = []
        for item in list_of_items:
            item_lines = item.source_mapping['lines']
            item_first_line = item_lines[0]
            item_last_line = item_lines[-1]
            item_and_first_line_number.append(tuple([item, item_first_line, item_last_line]))

        sorted_items = sorted(item_and_first_line_number, key=lambda item: item[1])  # sorted by line number
        return sorted_items

    '''
    :param sorted_contract : the soreted contract
    :param i : the index of the contract
    :param list_of_lines : list of rows in the file

    :return comment : the comment of the contract
    '''
    def get_contract_comment(self, i, sorted_contract, list_of_lines):
        if i == 0:

            # first contract's comment
            line1 = 1
            line2 = sorted_contract[0][1]

            comment = self.get_string_between_line1_and_line2(list_of_lines, line1, line2)

        else:
            line1 = sorted_contract[i - 1][2] + 1
            line2 = sorted_contract[i][1]
            comment = self.get_string_between_line1_and_line2(list_of_lines, line1, line2)

        return comment

    def get_node_information(self,node_name,node_type,data_type,description_sentence,function_code,function_node_cfg):
        self.node_information['FEN:ID'].append(node_name)
        self.node_information[':LABEL'].append(node_type)
        self.node_information['Data_Type'].append(data_type)
        self.node_information['Description'].append(description_sentence)
        self.node_information['Function_Code'].append(function_code)
        self.node_information['CFG'].append(function_node_cfg)

        if (node_type == 'Function') | (node_type == 'Modifier') | (node_type == 'Constructor') | (node_type == 'Fallback'):
            self.node_information['Composition_Count'].append('get ' + node_type + "'s composition count")
            self.node_information['Flow_Chart'].append('get ' + node_type + "'s flow chart")

        else:
            self.node_information['Composition_Count'].append(node_type + " has no composition count")
            self.node_information['Flow_Chart'].append(node_type + " has no flow chart")


    def get_function_parameter_nodes(self,function):

        function_name = function.source_mapping['filename_absolute'] + ':' + function.canonical_name.replace('.',':')

        parameters = function.parameters
        i = 0
        for parameter in parameters:
            # parameter's node information
            if parameter.name == '':
                node_name = parameter.source_mapping['filename_absolute'] + ':' + parameter.canonical_name.replace('.',':') + 'parameter_' + str(i)
            else:
                node_name = parameter.source_mapping['filename_absolute'] + ':' + parameter.canonical_name.replace('.',':')
            node_type = 'Parameter_' + str(i)
            data_type = str(parameter.type)
            node_function_code = 'Parameter has no function code'
            node_description = 'wait for function to send description'
            node_cfg = "Parameter has no cfg"
            self.get_node_information(node_name, node_type, data_type, node_description, node_function_code,node_cfg)

            #has para relation
            self.dict_has_para[':START_ID'].append(function_name)
            self.dict_has_para[':END_ID'].append(node_name)
            self.dict_has_para[':TYPE'].append('has_parameter')
            i += 1

    def get_event_parameter_nodes(self,event):

        event_name = event.source_mapping['filename_absolute'] + ':' + str(event.contract) + ':' + event.full_name

        parameters = event.elems
        i = 0
        for parameter in parameters:
            # parameter's node information
            if parameter.name == '':
                node_name = event_name + ':' + 'parameter_' + str(i)
            else:

                node_name = event_name + ':' + parameter.name
            node_type = 'Parameter_' + str(i)
            data_type = str(parameter.type)
            node_function_code = 'Parameter has no function code'
            node_description = 'wait for event to send description'
            node_cfg = "Parameter has no cfg"

            self.get_node_information(node_name, node_type, data_type, node_description, node_function_code, node_cfg)


            # has para relation
            self.dict_has_para[':START_ID'].append(event_name)
            self.dict_has_para[':END_ID'].append(node_name)
            self.dict_has_para[':TYPE'].append('has_parameter')

            i += 1

    def get_struct_element(self,struct):

        struct_name = struct.source_mapping['filename_absolute'] + ':' + struct.canonical_name.replace('.',':')

        elements = struct.elems
        i = 0
        for key,value in elements.items():
            # parameter's node information
            node_name = struct_name + ':' + value.name
            node_type = 'Element_' + str(i)
            data_type = str(value.type)
            node_function_code = 'element has no function code'
            node_description = 'wait for struct to send description'
            node_cfg = "Element has no cfg"
            self.get_node_information(node_name, node_type, data_type, node_description, node_function_code, node_cfg)

            # has para relation
            self.dict_has_element[':START_ID'].append(struct_name)
            self.dict_has_element[':END_ID'].append(node_name)
            self.dict_has_element[':TYPE'].append('has_element')
            i += 1

    def get_enum_element(self,enum):
        enum_name = enum.source_mapping['filename_absolute'] + ':' + enum.canonical_name.replace('.',':')
        elements = enum.values
        i = 0
        for element in elements:

            # parameter's node information
            node_name = enum_name + ':' + element
            node_type = 'Element_' + str(i)
            data_type = "enum's element"
            node_function_code = 'element has no function code'
            node_description = 'wait for enum to send description'
            node_cfg = "Element has no cfg"
            self.get_node_information(node_name, node_type, data_type, node_description, node_function_code, node_cfg)

            # has para relation
            self.dict_has_element[':START_ID'].append(enum_name)
            self.dict_has_element[':END_ID'].append(node_name)
            self.dict_has_element[':TYPE'].append('has_element')

            i += 1

    def get_function_returns(self,function):
        function_name = function.source_mapping['filename_absolute'] + ':' + function.canonical_name.replace('.',':')
        i = 0
        returns = function.returns
        for return_element in returns:
            # parameter's node information
            node_name = function_name + ':' + 'returns_' + str(i)
            node_type = 'Returns_' + str(i)
            data_type = str(return_element.type)
            node_function_code = 'returns has no function code'
            node_description = 'wait for function to send description'
            node_cfg = "Returns has no cfg"
            self.get_node_information(node_name, node_type, data_type, node_description, node_function_code, node_cfg)

            # has para relation
            self.dict_has_returns[':START_ID'].append(function_name)
            self.dict_has_returns[':END_ID'].append(node_name)
            self.dict_has_returns[':TYPE'].append('has_returns')

            i += 1

    def handle_variable_item(self,now_item):

        node_name = now_item.source_mapping['filename_absolute'] + ':' + now_item.canonical_name.replace('.', ':')
        node_type = 'Variable'
        node_function_code = 'variable has no function code'
        node_cfg = "Variable has no cfg"

        if now_item.type.__class__.__name__ == 'ElementaryType':
            data_type = now_item.type.type
        elif now_item.type.__class__.__name__ == 'MappingType':
            data_type = 'mapping'
        elif now_item.type.__class__.__name__ == 'ArrayType':
            data_type = 'array'
        elif now_item.type.__class__.__name__ == 'UserDefinedType':
            if now_item.type.type.__class__.__name__ == 'Contract':
                this_contract = now_item.type.type
                data_type = this_contract.source_mapping['filename_absolute'] + ':' + str(this_contract)
            else:
                this_item = now_item.type.type
                data_type = this_item.source_mapping['filename_absolute'] + ':' + this_item.canonical_name.replace('.',
                                                                                                                   ':')
        else:
            data_type = 'unknow type'



        return node_name,node_type,data_type,node_function_code,node_cfg

    def handle_modifier_item(self,now_item):

        node_name = now_item.source_mapping['filename_absolute'] + ':' + now_item.canonical_name.replace('.', ':')
        file_path = now_item.source_mapping['filename_absolute']
        function_lines = now_item.source_mapping['lines']
        node_type = 'Modifier'
        data_type = 'modifier'

        node_function_code = get_function_code(file_path, function_lines)
        node_cfg = get_cfg(now_item.nodes)
        return node_name, node_type, data_type, node_function_code, node_cfg

    def handle_function_item(self, now_item):
        node_name = now_item.source_mapping['filename_absolute'] + ':' + now_item.canonical_name.replace('.', ':')
        file_path = now_item.source_mapping['filename_absolute']
        function_lines = now_item.source_mapping['lines']

        node_function_code = get_function_code(file_path, function_lines)

        if now_item.function_type.name == 'FALLBACK':
            node_type = 'Fallback'
        elif now_item.function_type.name == 'CONSTRUCTOR':
            node_type = 'Constructor'
        else:

            node_type = self.get_function_type(now_item)

        if node_type == 'Fallback':
            data_type = 'fallback'
        elif node_type == 'Constructor':
            data_type = 'constructor'
        elif node_type == 'Abstract_Function':
            data_type = 'abstract_function'
        elif node_type == 'Function':
            data_type = 'function'
        else:
            data_type = 'unknow type'

        if (node_type == 'Abstract_Function'):
            node_cfg = "Abstract_Function has no cfg"
        else:
            node_cfg = get_cfg(now_item.nodes)

        return node_name, node_type, data_type, node_function_code, node_cfg

    def handle_event_item(self,now_item):

        node_name = now_item.source_mapping['filename_absolute'] + ':' + str(
            now_item.contract) + ':' + now_item.full_name
        node_type = 'Event'
        data_type = 'event'
        node_function_code = 'Event has no function code'
        function_node_cfg = "Event has no cfg"
        return node_name, node_type, data_type, node_function_code, function_node_cfg

    def handle_struct_item(self,now_item):

        node_name = now_item.source_mapping['filename_absolute'] + ':' + now_item.canonical_name.replace('.', ':')
        node_type = 'Struct'
        data_type = now_item.name
        node_function_code = 'Struct has no function code'
        node_cfg = "Struct has no cfg"

        return node_name, node_type, data_type, node_function_code, node_cfg

    def handle_enum_item(self,now_item):

        node_name = now_item.source_mapping['filename_absolute'] + ':' + now_item.canonical_name.replace('.', ':')
        node_type = 'Enum'
        data_type = now_item.name
        node_function_code = 'Enum has no function code'
        node_cfg = "Enum has no cfg"

        return node_name, node_type, data_type, node_function_code, node_cfg

    def get_item_comment(self, i, contract_first_line, sorted_items, list_of_lines):
        if i == 0:

            # first item's comment
            line1 = contract_first_line + 1
            line2 = sorted_items[i][1]

            comment = self.get_string_between_line1_and_line2(list_of_lines, line1, line2)

        else:
            line1 = sorted_items[i - 1][2] + 1
            line2 = sorted_items[i][1]
            comment = self.get_string_between_line1_and_line2(list_of_lines, line1, line2)

        return comment

    def handle_contract(self, sorted_contract, list_of_lines):

        for i in range(len(sorted_contract)):

            now_contract = sorted_contract[i][0]
            node_name = now_contract.source_mapping['filename_absolute'] + ':' + str(now_contract)

            node_comment = self.get_contract_comment(i, sorted_contract, list_of_lines)

            # information :
            try:
                node_type = now_contract.kind
            except:
                node_type = 'contract'
            data_type = node_type

            if node_type == 'contract':
                node_type = 'Contract'
            elif node_type == 'library':
                node_type = 'Library'
            elif node_type == 'interface':
                node_type = 'Interface'
            else:
                node_type = 'Unknow Type'

            node_function_code = 'contract has no function code'
            node_description = node_comment
            node_cfg = node_type + " has no cfg"
            self.get_node_information(node_name, node_type, data_type, node_description, node_function_code, node_cfg)

    def handle_items(self, contract, list_of_lines):

        contract_lines = contract.source_mapping['lines']
        contract_first_line = contract_lines[0]
        list_of_items = self.get_list_of_items(contract)
        sorted_items = self.sort_by_line_number(list_of_items)
        contract_node_name = contract.source_mapping['filename_absolute'] + ':' + str(contract)

        for i in range(len(sorted_items)):
            now_item = sorted_items[i][0]
            # node_name, node_type,data_type,description_sentence,function_code

            if now_item.__class__.__name__ == 'StateVariable':
                node_name, node_type, data_type, node_function_code, node_cfg = self.handle_variable_item(now_item)

                # has variable relation
                self.dict_has_Variable[':START_ID'].append(contract_node_name)
                self.dict_has_Variable[':END_ID'].append(node_name)
                self.dict_has_Variable[':TYPE'].append('has_variable')

            elif now_item.__class__.__name__ == 'Modifier':
                node_name, node_type, data_type, node_function_code, node_cfg = self.handle_modifier_item(now_item)

                # has modifier relation
                self.dict_has_function[':START_ID'].append(contract_node_name)
                self.dict_has_function[':END_ID'].append(node_name)
                self.dict_has_function[':TYPE'].append('has_function')

                # has para relation
                # parameter node
                self.get_function_parameter_nodes(now_item)

            elif now_item.__class__.__name__ == 'FunctionContract':

                # useless
                if (now_item.function_type == 'CONSTRUCTOR_VARIABLES') | (
                        now_item.name == 'slitherConstructorConstantVariables') | (
                        now_item.name == 'slitherConstructorVariables'):
                    continue

                node_name, node_type, data_type, node_function_code, node_cfg = self.handle_function_item(now_item)

                self.dict_has_function[':START_ID'].append(contract_node_name)
                self.dict_has_function[':END_ID'].append(node_name)
                self.dict_has_function[':TYPE'].append('has_function')

                # has para relation
                # parameter node
                self.get_function_parameter_nodes(now_item)

                # has returns relation
                # returns node
                self.get_function_returns(now_item)

            elif now_item.__class__.__name__ == 'Event':

                node_name, node_type, data_type, node_function_code, node_cfg = self.handle_event_item(now_item)

                self.dict_has_event[':START_ID'].append(contract_node_name)
                self.dict_has_event[':END_ID'].append(node_name)
                self.dict_has_event[':TYPE'].append('has_event')

                # has para relation
                # parameter node
                self.get_event_parameter_nodes(now_item)

            elif now_item.__class__.__name__ == 'StructureContract':

                node_name, node_type, data_type, node_function_code, node_cfg = self.handle_struct_item(now_item)
                # the relation with element :
                self.dict_has_Struct[':START_ID'].append(contract_node_name)
                self.dict_has_Struct[':END_ID'].append(node_name)
                self.dict_has_Struct[':TYPE'].append('has_struct')

                # has para relation
                # parameter node
                self.get_struct_element(now_item)

            elif now_item.__class__.__name__ == 'EnumContract':

                node_name, node_type, data_type, node_function_code, node_cfg = self.handle_enum_item(now_item)

                self.dict_has_Enum[':START_ID'].append(contract_node_name)
                self.dict_has_Enum[':END_ID'].append(node_name)
                self.dict_has_Enum[':TYPE'].append('has_enum')

                # has element relation
                # element nodes
                self.get_enum_element(now_item)

            else:
                raise

            node_comment = self.get_item_comment(i, contract_first_line, sorted_items, list_of_lines)

            node_description = node_comment

            self.get_node_information(node_name, node_type, data_type, node_description, node_function_code, node_cfg)


    # get dict { node name : [] ,node comment : [] }
    # input : the slither object
    def nodes_information(self, sol, sol_file):
        f = open(sol_file, 'r')
        list_of_lines = f.readlines()
        f.close()

        contract_list = sol.contracts

        sorted_contract = self.sort_by_line_number(contract_list)
        #handle contracts
        self.handle_contract(sorted_contract, list_of_lines)

        for contract in sorted_contract:
            # contract : (contract,first line,end line)
            #handle items in contract

            now_contract = contract[0]
            self.handle_items(now_contract, list_of_lines)


    def make_information_to_csv(self):

        df_node_information = pd.DataFrame(self.node_information)
        df_node_information.to_csv(self.configs.node_file, index=0)

        df_has_function = pd.DataFrame(self.dict_has_function)
        df_has_function.to_csv(self.configs.has_function_relation_file, index=0)

        df_has_event = pd.DataFrame(self.dict_has_event)
        df_has_event.to_csv(self.configs.has_event_relation_file, index=0)

        df_has_Variable = pd.DataFrame(self.dict_has_Variable)
        df_has_Variable.to_csv(self.configs.has_variable_file, index=0)

        df_has_Struct = pd.DataFrame(self.dict_has_Struct)
        df_has_Struct.to_csv(self.configs.has_structure_file, index=0)

        df_has_Enum = pd.DataFrame(self.dict_has_Enum)
        df_has_Enum.to_csv(self.configs.has_enum_file, index=0)

        df_has_para = pd.DataFrame(self.dict_has_para)
        df_has_para.to_csv(self.configs.has_para_file, index=0)

        df_has_element = pd.DataFrame(self.dict_has_element)
        df_has_element.to_csv(self.configs.has_element_file, index=0)

        df_has_returns = pd.DataFrame(self.dict_has_returns)
        df_has_returns.to_csv(self.configs.has_returns_file, index=0)

        df_calls = pd.DataFrame(self.dict_calls)
        df_calls.to_csv(self.configs.calls_relation_file, index=0)

    def Calls_relation(self, list_of_calls_relations):
        for list_of_calls_ralation in list_of_calls_relations:
            name_pre = list_of_calls_ralation[0]
            name_next = list_of_calls_ralation[1]
            relation = list_of_calls_ralation[2]

            self.dict_calls[':START_ID'].append(name_pre)
            self.dict_calls[':END_ID'].append(name_next)
            self.dict_calls[':TYPE'].append(relation)

            if '/' not in name_next:
                self.set_of_solidity_api.add(name_next)

    def get_solidity_api(self):

        for solidity_api in self.set_of_solidity_api:
            node_name = solidity_api
            node_type = 'Solidity_Api'
            data_type = 'solidity_api'
            description_sentence = 'solidity description'
            function_code = 'solidtiy api has no function code'
            function_node_cfg = "Solidity api has no cfg"
            self.get_node_information(node_name,node_type,data_type,description_sentence,function_code,function_node_cfg)

    def get_Basic_node_and_relations(self):
        print("start to get node's information")
        list_of_file = findAllFile(self.configs.contracts_directory)

        for sol_file in tqdm.tqdm(list_of_file, total=self.length_of_contract_directory):

            try:
                if try_get_slither_object_from_sol_file(sol_file):
                    sol = Slither(sol_file)

                    # 1.handle the essential node information and relation
                    self.nodes_information(sol, sol_file)

                    #2.get solidity api,used it relation
                    list_of_calls_relations = get_Calls_relation(sol)
                    self.Calls_relation(list_of_calls_relations)

                else:
                    print('failed to get slither object')
            except:
                f = open('bug_file.txt','a')
                f.writelines(sol_file + '\n')
                f.close()

        self.get_solidity_api()
        self.make_information_to_csv()

        df_node_information = pd.DataFrame(self.node_information)
        df_node_information.to_csv(self.configs.saved_information_directory + 'node_after_node_information.csv', index=0)
        print('getting node information has done')


if __name__ == '__main__':

    get_class_object = Basic_node_and_relations(configs())
    get_class_object.get_Basic_KG()

