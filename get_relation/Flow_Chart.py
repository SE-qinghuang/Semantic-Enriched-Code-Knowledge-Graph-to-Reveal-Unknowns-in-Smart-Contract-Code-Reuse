import re
import os
from get_relation.CFGNode import*
from slither.slither import Slither
from config import configs
from now_tools import findAllFile,try_get_slither_object_from_sol_file,len_of_directory
import pandas as pd
import csv
import tqdm

class get_Flow_Chart:
    def __init__(self,configs):
        self.configs = configs
        self.emit_event = {'pre_node': [], 'next_node': [], 'relation': []}
        self.node_information = pd.read_csv(self.configs.node_file)
        self.length_of_contract_directory = len_of_directory(self.configs.contracts_directory)
        self.using_library = False
        self.library_list = ''
        self.dict_expression_nums = {}


    def get_node_desctiption(self,node_name):
        return self.node_information[self.node_information['FEN:ID'] == node_name]['Description']

    def get_all_nodes(self,nodes_rels_list):
        all_nodes = set()
        for node_rels in nodes_rels_list:
            for node_rel in node_rels:
                node_pre = node_rel[0]
                node_next = node_rel[1]
                all_nodes.add(node_pre)
                all_nodes.add(node_next)
        return all_nodes

    def change_node_type_to_nlp(self,node_type):
        if node_type == 'ENTRY_POINT':
            return 'START'
        else:
            return node_type

    #!!!!!!! the most important step
    #get the node we need from cfg node
    def get_label_and_events_from_cfgnode(self,node):
        useful_node_type_list = ['ENTRY_POINT','IF','IF_LOOP','RETURN','END_LOOP','THROW','BEGIN_LOOP']

        # #only cfg
        # if str(node.expression) == 'None':
        #     label = str(node)
        # else:
        #     label = str(node.expression)

        label = ''
        node_label = self.get_label(node)

        label += '{}\n'.format(node_label)
        return label

    def order_list_to_str_and_get_events(self,nodes_rels_list):
        """
        Export the CFG to a DOT format. The nodes includes the Solidity expressions and the IRs
        :return: the DOT content
        :rtype: str
        """
        emited_events = set()
        nodes = self.get_all_nodes(nodes_rels_list)
        content = ""
        content += "digraph{\n"

        #handle the details for one node
        for node in nodes:

            label = self.get_label_and_events_from_cfgnode(node)
            # emited_events = events_set

            # label = "Node Type: {} {}".format(str(node.type),node.node_id)
            content += '{}[label = "{}"];\n'.format(node.node_id,label)

        for node_rels in nodes_rels_list:
            for node_rel in node_rels:

                node_pre = node_rel[0]
                node_next = node_rel[1]
                rel_label = node_rel[2]

                if rel_label == 'son_true':
                    label = '{}->{}[label = "true"];\n'.format(node_pre.node_id,node_next.node_id)
                elif rel_label == 'son_false':
                    label = '{}->{}[label = "false"];\n'.format(node_pre.node_id,node_next.node_id)
                else:
                    label = '{}->{};\n'.format(node_pre.node_id,node_next.node_id)
                content += label
        content += "}\n"

        return content

    def write_content_to_dot(self,function_name,content):
        pattern = re.compile('(.*):(.*):(.*)')
        if pattern.match(function_name):
            file_absolute_path = pattern.match(function_name).group(1)
            file_absolute_path = file_absolute_path.replace('/','-')
            contract = pattern.match(function_name).group(2)
            function = pattern.match(function_name).group(3)
            f = open('dot_file/{}_{}_{}.dot'.format(file_absolute_path,contract,function) ,'w')
            f.writelines(content)
            f.close()
        else:
            f = open('dot_file/bug_when_write_content_to_dot','w')
            f.writelines(function_name + '\n')
            f.close()

    def get_dict_using_for(self,contract):
        dict_using_for = {}
        using_for = contract.using_for
        for data_type,library_list in using_for.items():
            if data_type.__class__.__name__ == 'UserDefinedType':
                data_type_name = data_type.type.source_mapping['filename_absolute'] + ':' + str(data_type.type)
            elif data_type.__class__.__name__ == 'ElementaryType':
                data_type_name = data_type.name
            else:
                data_type_name = str(data_type)

            for library in library_list:
                dict_using_for[data_type_name] = []
                if library.__class__.__name__ == 'UserDefinedType':
                    library_node_name = library.type.source_mapping['filename_absolute'] + ':' + str(library.type)
                    dict_using_for[data_type_name].append(library_node_name)
                else:
                    dict_using_for[data_type_name].append(str(library))
        return dict_using_for

    #dict_function_to_description : node_name : node_description
    #sol : slither object
    def get_dic_function_to_order_sequence_and_emit_event(self,sol):
        dic_function_to_order_sequence = {}

        # self.dict_using_for = {'uint256': 'SafeMath'}
        for contract in sol.contracts:
            self.dict_using_for = self.get_dict_using_for(contract)
            sol_path = contract.source_mapping['filename_absolute']

            for function in contract.functions_and_modifiers_declared:
                # useless
                if (function.function_type == 'CONSTRUCTOR_VARIABLES') | (
                        function.name == 'slitherConstructorConstantVariables') | (
                        function.name == 'slitherConstructorVariables'):
                    continue
                nodes_rels_list = []
                function_name = sol_path + ':' + function.canonical_name.replace('.', ':')
                if self.node_information[self.node_information['FEN:ID'] == function_name][':LABEL'].tolist()[0] == 'Abstract_Function':
                    continue
                if function.nodes:
                    #all node there is cfgnode(include : node,cfg_node)
                    for node in function.nodes:
                        cfg_node = CFGnode(node)
                        if len(cfg_node.cfgnode_rel) > 0:
                            nodes_rels_list.append(cfg_node.cfgnode_rel)


                content = self.order_list_to_str_and_get_events(nodes_rels_list)

                # dic_function_to_order_sequence[function_name] = content
                self.node_information.loc[
                    self.node_information['FEN:ID'] == function_name, (
                        'Flow_Chart')] = content
                # function_emit_event_relation[function_name] = emited_events
        #     self.dict_using_for = {}
        # return dic_function_to_order_sequence

    #function_emit_event_relation : dict{function : event}
    #relation_file : the file to save
    def get_emit_event_relation(self,function_emit_event_relation,relation_file):

        f = open(relation_file, 'a')
        csv_writer = csv.writer(f)
        relation = 'Emit Event'
        for function_name in function_emit_event_relation:
            events_set = function_emit_event_relation[function_name]
            if len(events_set) > 0:
                for event in events_set:
                    relation_lits = [function_name, event, relation]
                    csv_writer.writerow(relation_lits)
        f.close()

    def get_label(self,node):

        if str(node) == 'ENTRY_POINT':
            return 'start'
        elif str(node) == 'END_IF':
            return 'END_IF'
        elif str(node) == '_':
            return '_'
        elif str(node) == 'BEGIN_LOOP':
            return 'BEGIN_LOOP'
        elif str(node) == 'END_LOOP':
            return 'END_LOOP'
        # elif str(node.type) == 'NEW VARIABLE':
        #     return 'new variable : {}'.format(node.variable_declaration.canonical_name.replace('.',':'))
        elif str(node) == 'THROW':
            return 'THROW'
        label = ''
        node_expression = node.expression
        # node_expression_type = get_expression_type(node_expression)

        label = self.handle_expression(node_expression,label)

        if str(node.type) == 'RETURN':
            label = 'return ' + label
        return label

    def handle_expression(self, expression, label):
        expression_type = self.get_expression_type(expression)
        if expression_type == 'BinaryOperation':
            label = label + self.handle_BinaryOperation_expression(expression,label)
        elif expression_type == 'MemberAccess':
            label = label + self.handle_MemberAccess_expression(expression,label)
        elif expression_type == 'IndexAccess':
            label = label + self.handle_IndexAccess_expression(expression,label)
        elif expression_type == 'Identifier':
            label = label + self.handle_Identifier_expression(expression,label)
        elif expression_type == 'CallExpression':
            label = label + self.handle_CallExpression_expression(expression,label)
        elif expression_type == 'AssignmentOperation':
            label = label + self.handle_AssignmentOperation_expression(expression,label)
        elif expression_type == 'TypeConversion':
            label = label + self.handle_TypeConversion_expression(expression,label)
        elif expression_type == 'Literal':
            label = label + self.handle_Literal_expression(expression,label)
        elif expression_type == 'UnaryOperation':
            label = label + self.handle_UnaryOperation_expression(expression,label)
        elif expression_type == 'TupleExpression':
            label = label + self.handle_TupleExpression_expression(expression,label)
        # elif expression_type == 'ElemantaryTypeNameExpression':
        #     f = open('files of elemantary type name expression.txt', 'a')
        #     f.writelines(expression.source_mapping['filename_absolute'] + '\n')
        #     f.close()
        else:
            label = 'error when handle expression'

        if expression_type in self.dict_expression_nums:
            self.dict_expression_nums[expression_type] += 1
        else:
            self.dict_expression_nums[expression_type] = 1

        return label

    def handle_TupleExpression_expression(self,expression,label):
        now_content = ''
        for expression_now in expression.expressions:
            now_content = now_content + self.handle_expression(expression_now,label) + ','

        label = label + now_content[:-1]
        return label

    def handle_UnaryOperation_expression(self,expression,label):
        label = label + str(expression.type) + self.handle_expression(expression.expression,label)
        return label

    def handle_Literal_expression(self,expression,label):
        return label + str(expression)

    def handle_TypeConversion_expression(self,expression,label):
        return label + str(expression)

    def handle_CallExpression_expression(self,expression,label):
        #handle value + arguments
        if expression.called.__class__.__name__ == 'NewContract':
            label = label + expression.called.contract_name
            if len(expression.arguments) > 0:
                label = label + '('
                body = ''
                for argument in expression.arguments:
                    body = body + self.handle_expression(argument,'') + ','
                label = label + body[:-1]
                label = label + ')'
        elif expression.called.__class__.__name__ == 'Identifier':
            label = label + self.handle_Identifier_expression(expression.called,label)
            if len(expression.arguments) > 0:
                label = label + '('
                body = ''
                for argument in expression.arguments:
                    body = body + self.handle_expression(argument,'') + ','
                label = label + body[:-1]
                label = label + ')'
        elif expression.called.__class__.__name__ == 'MemberAccess':
            type_call = expression.type_call
            #find the function
            if type_call in self.dict_using_for:

                self.library_list = self.dict_using_for[type_call]
                self.using_library = True
            label = label + self.handle_MemberAccess_expression(expression.called,label)
            #get the arguments
            if len(expression.arguments) > 0:
                label = label + '('
                body = ''
                if self.library_function_be_found == True:
                    # if expression.called.expression.__class__.__name__ == 'IndexAccess':
                    #     first_argument_node_description = str(expression.called.expression)
                    # else:
                    #     first_argument = expression.called.expression.value
                    #     first_argument_node_name = first_argument.source_mapping['filename_absolute'] + ':' + first_argument.canonical_name.replace('.',':')
                    #     first_argument_node_description = self.node_information[self.node_information['FEN:ID'] == first_argument_node_name]['Description'].tolist()[0]
                    first_argument = expression.called.expression
                    body = body + self.handle_expression(first_argument,'') + ','
                self.library_function_be_found = False
                for argument in expression.arguments:
                    body = body + self.handle_expression(argument,'') + ','
                label = label + body[:-1]
                label = label + ')'
        elif expression.called.__class__.__name__ == 'SuperIdentifier':
            label = label + expression.called.value.canonical_name.replace('.',':')
            if len(expression.arguments) > 0:
                label = label + '('
                body = ''

                self.library_function_be_found = False
                for argument in expression.arguments:
                    body = body + self.handle_expression(argument,'') + ','
                label = label + body[:-1]
                label = label + ')'
        elif expression.called.__class__.__name__ == 'CallExpression':
            label = label + self.handle_expression(expression.called,label)
            if len(expression.arguments) > 0:
                label = label + '('
                body = ''
                for argument in expression.arguments:
                    body = body + self.handle_expression(argument, '') + ','
                label = label + body[:-1]
                label = label + ')'

        return label

    def handle_solidity_api(self,value):
        if (value.name == 'assert(bool)') | (value.name == 'require(bool)'):
            return 'check'
        elif (value.name == 'selfdestruct(address)'):
            return 'destroy the current contract, sending its funds to the given address'
        else:
            return str(value)

    def handle_solidity_variable(self,value):
        if (value.name == 'msg.sender'):
            return 'sender of the message (current call)'
        else:
            return str(value)

    def handle_Identifier_expression(self,expression,label):
        if hasattr(expression,'value'):
            value = expression.value
            if value.__class__.__name__ == 'SolidityFunction':
                label = label + self.handle_solidity_api(value)

            elif value.__class__.__name__ == 'Event':

                #here to get node description
                node_name = value.source_mapping['filename_absolute'] + ':' + str(value.contract) + ':' + value.full_name
                node_description = self.node_information[self.node_information['FEN:ID'] == node_name]['Description'].tolist()[0]
                label = label + 'Emit Event\n' + node_description

            elif value.__class__.__name__ == 'Modifier':
                node_name = value.source_mapping['filename_absolute'] + ':' + value.canonical_name.replace('.', ':')
                # here to get node description
                node_description = self.node_information[self.node_information['FEN:ID'] == node_name]['Description'].tolist()[0]
                label = label + 'Modifier\n' + node_description
            #no idea to handle
            elif value.__class__.__name__ == 'LocalVariable':

                node_name = value.source_mapping['filename_absolute'] + ':' + value.canonical_name.replace('.',':')

                #judge whether the node in dataframe,if in : the node is parameter
                try:
                    node_description = \
                    self.node_information[self.node_information['FEN:ID'] == node_name]['Description'].tolist()[0]
                except:
                    node_description = str(value)
                label = label + node_description
            elif value.__class__.__name__ == 'StateVariable':

                #here to get node description
                node_name = value.source_mapping['filename_absolute'] + ':' + value.canonical_name.replace('.',':')
                node_description = \
                    self.node_information[self.node_information['FEN:ID'] == node_name]['Description'].tolist()[
                        0]
                label = label + node_description
            elif value.__class__.__name__ == 'SolidityVariableComposed':

                label = label + self.handle_solidity_variable(value)
            elif value.__class__.__name__ == 'LocalVariable':
                try:
                    node_name = value.source_mapping['filename_absolute'] + ':' + value.canonical_name.replace('.',':')
                    node_description = self.node_information[self.node_information['FEN:ID'] == node_name]['Description'].tolist()[
                            0]
                    label = label + node_description
                except:
                    label = label + str(expression)
            else:
                label = label + str(expression)
        else:
            label = 'error when handle identifier expression'
        return label

    def handle_IndexAccess_expression(self,expression,label):
        if hasattr(expression,'expression_left') & hasattr(expression,'expression_right'):
            expression_left = expression.expression_left
            expression_right = expression.expression_right
            # label = label + self.handle_expression(expression_left,label) + "'s" + self.handle_expression(expression_right,label)
            label = label + str(expression_left) + '[' + self.handle_expression(expression_right, label) + ']'
            return label
        else:
            return 'error when handle binary operation expression'
        # label = label + str(expression)
        # return label

    def handle_MemberAccess_expression(self,expression,label):

        self.library_function_be_found = False
        if self.using_library == True:
            for library_name in self.library_list:

                #exist
                try:
                    library_function_name = library_name + ':' + expression.member_name + re.search('[(].*?[)]',
                                                                                                    expression.type).group()
                    library_function_description = self.node_information[self.node_information['FEN:ID'] == library_function_name]['Description'].tolist()[0]
                    self.library_function_be_found = True
                    break
                except:
                    pass
        if self.library_function_be_found == False:
            label = label + self.handle_expression(expression.expression,label) + '.' + expression.member_name
            # label = label + str(expression)
        else:
            label = label + library_function_description


        #
        # if hasattr(expression.expression,'expression_left') & hasattr(expression.expression,'expression_right'):
        #     expression_left = expression.expression.expression_left
        #     expression_right = expression.expression.expression_right
        #     if self.using_library == True:
        #         if re.search('[(].*?[)]',expression.type):
        #
        #             member_node_name = self.library_node_type + ':' + expression.member_name + re.search('[(].*?[)]',expression.type).group()
        #             label = label + self.handle_expression(expression_left,label) + "'s " + self.handle_expression(expression_right,label) + ':' + member_node_name
        #         else:
        #             label = label + self.handle_expression(expression.expression,label) + "'s " + expression.member_name
        #     else:
        #         label = label + self.handle_expression(expression_left,label) + ' ' + str(expression.type) + ' '  + self.handle_expression(expression_right,label)
        #     return label
        # elif hasattr(expression.expression,'expression_left'):
        #
        #     member_node_type = expression.expression.expression_left.value.type.type.type
        #     member_node_name = member_node_type.source_mapping['filename_absolute'] + ':' + member_node_type.canonical_name.replace('.',':') + ':' + expression.member_name
        #     member_node_description = self.node_information[self.node_information['FEN:ID'] == member_node_name]['Description'].tolist()[0]
        #     a = 1
        #     label = label + str(expression.expression) + "'s " + member_node_description
        #     return label
        # elif hasattr(expression.expression,'value'):
        #     if expression.expression.value.__class__.__name__ == 'EnumContract':
        #         node_name = expression.expression.value.canonical_name.replace('.',':') + ':' + expression.member_name
        #         label = label + node_name
        #     elif hasattr(expression.expression.value,'type'):
        #
        #         if expression.expression.value.type.__class__.__name__ == 'ElementaryType':
        #
        #             if expression.expression.value.__class__.__name__ == 'SolidityVariableComposed':
        #                 try:
        #                     parameter_types = re.search('[(].*?[)]', expression.type).group()
        #                     node_name = expression.expression.value.name + ':' + self.library_node_type + ':' + expression.member_name + parameter_types
        #                 except:
        #                     node_name = str(expression)
        #             elif expression.expression.value.__class__.__name__ == 'SolidityVariable':
        #                 node_name = str(expression)
        #             else:
        #                 try:
        #                     parameter_types = re.search('[(].*?[)]', expression.type).group()
        #                     node_name = expression.expression.value.canonical_name.replace('.',':') + ':' + self.library_node_type + ':' + expression.member_name+ parameter_types
        #                 except:
        #                     node_name = str(expression)
        #         elif expression.expression.value.type.__class__.__name__ == 'ArrayType':
        #
        #             node_name = expression.expression.value.canonical_name.replace('.',':') + "'s" + expression.member_name
        #         else:
        #             if expression.expression.type.__class__.__name__ == 'NoneType':
        #                 node_name = expression.expression.value.canonical_name.replace('.',':') + expression.member_name
        #             else:
        #                 parameter_types = re.search('[(].*?[)]', expression.type).group()
        #                 node_name = str(expression.expression.value.type.type) + ':' + expression.member_name + parameter_types
        #
        #         label = label + node_name
        #     return label
        # elif hasattr(expression.expression,'called'):
        #     if re.search('[(].*?[)]',expression.type):
        #
        #         member_node_name = self.library_node_type + ':' + expression.member_name + re.search('[(].*?[)]',expression.type).group()
        #         label = label + self.handle_expression(expression.expression,label) + ':' + member_node_name
        #     else:
        #         label = label + self.handle_expression(expression.expression,label) + "'s" + expression.member_name
        #     return label
        # else:
        #     return 'error when handle member access expression'

        return label

    def handle_BinaryOperation_expression(self,expression,label):

        if hasattr(expression,'expression_left') & hasattr(expression,'expression_right'):
            expression_left = expression.expression_left
            expression_right = expression.expression_right
            label = label + self.handle_expression(expression_left,label) + ' ' + str(expression.type) + ' '  + self.handle_expression(expression_right,label)
            return label
        else:
            return 'error when handle binary operation expression'

    def handle_AssignmentOperation_expression(self,expression,label):
        if hasattr(expression,'expression_left') & hasattr(expression,'expression_right'):
            expression_left = expression.expression_left
            expression_right = expression.expression_right
            label = label + self.handle_expression(expression_left,label) + ' ' + str(expression.type) + ' '  + self.handle_expression(expression_right,label)
            return label
        else:
            return 'error when handle assignment operation expression'

    def get_expression_type(self,expression):
        return expression.__class__.__name__

    def get_all_flow_chart(self):
        list_of_sol_files = findAllFile(self.configs.contracts_directory)
        print('start to get function flow chart...')

        for sol_file in tqdm.tqdm(list_of_sol_files, total=self.length_of_contract_directory):
            print(sol_file)

            if try_get_slither_object_from_sol_file(sol_file):
                sol = Slither(sol_file)
                self.get_dic_function_to_order_sequence_and_emit_event(sol)
            else:
                print('error')



        self.node_information.to_csv(self.configs.node_file,index=0)
        self.node_information.to_csv(self.configs.saved_information_directory + 'node_information_after_get_flow_chart.csv',index=0)

        f = open('expression_to_num.txt', 'w')
        for key, value in self.dict_expression_nums.items():
            f.writelines('{},{}\n'.format(key, value))
        f.close()