from slither.slither import Slither
from now_tools import findAllFile, try_get_slither_object_from_sol_file, get_function_code
from config import configs
import re
import pandas as pd
import tqdm

class enrich_description():

    def __init__(self,configs):
        self.configs = configs
        self.node_information = pd.read_csv(self.configs.node_file)
        self.override_relation = pd.read_csv(self.configs.override_file)

    def get_simple_name(self,node_name):
        return node_name.split(':')[-1]

    def get_the_node_description(self,node_name):
        node_description = self.node_information[self.node_information['FEN:ID'] == node_name]['Description'].tolist()[0]

        return node_description

    def get_para_comment(self,name_pre_comment,para_name,name_pre,name_next):

        if name_pre_comment == 'no comment':
            para_comment = 'no comment'
        elif '@param' in name_pre_comment:

            # get the pattern of the description
            para_comments = re.findall('@param\\s+' + para_name + '\\s+.*\n', name_pre_comment)
            if len(para_comments) == 0:
                para_comment = 'no comment'
            else:
                para_comment = ''
                for comment in para_comments:
                    para_comment += comment
                # now_name_pre_comment = name_pre_comment.replace(para_comment,'')
                # self.node_information.loc[
                #     self.node_information['FEN:ID'] == name_pre, ('Description')] = now_name_pre_comment
        else:
            para_comment = 'no comment'

        self.node_information.loc[
            self.node_information['FEN:ID'] == name_next, ('Description')] = para_comment

    def get_returns_comment(self,name_pre_comment,returns_name,name_pre,name_next):
        if name_pre_comment == 'no comment':
            returns_comment = 'no comment'
        elif '@return' in name_pre_comment:

            # get the pattern of the description
            returns_comments = re.findall('@return\\s+.*\n',name_pre_comment)

            if len(returns_comments) == 0:
                returns_comment = 'no comment'
            else:
                index = int(returns_name.split('_')[-1])
                try:
                    returns_comment = returns_comments[index]
                except:
                    returns_comment = "can't get return's comment"

        else:
            returns_comment = 'no comment'

        self.node_information.loc[
            self.node_information['FEN:ID'] == name_next, ('Description')] = returns_comment

    def get_element_comment(self,name_pre_comment,element_name,name_pre,name_next):
        if name_pre_comment == 'no comment':
            element_comment = 'no comment'

        elif element_name in name_pre_comment:

            # get the pattern of the description
            element_comments = re.findall(element_name + '[\s\S]*?:.*\n',name_pre_comment)
            if len(element_comments) == 0:
                element_comment = 'no comment'
            else:
                element_comment = ''
                for comment in element_comments:
                    element_comment += comment
                # now_name_pre_comment = name_pre_comment.replace(para_comment,'')
                # self.node_information.loc[
                #     self.node_information['FEN:ID'] == name_pre, ('Description')] = now_name_pre_comment
        else:
            element_comment = 'no comment'

        self.node_information.loc[
            self.node_information['FEN:ID'] == name_next, ('Description')] = element_comment

    def add_comment_by_using_has_para(self,has_para_file):
        has_para_relation = pd.read_csv(has_para_file)
        for index, row in tqdm.tqdm(has_para_relation.iterrows(),total=has_para_relation.shape[0]):
            list_of_row = row.tolist()

            name_pre = list_of_row[0]
            name_next = list_of_row[1]
            name_pre_comment = self.get_the_node_description(name_pre)

            para_name = self.get_simple_name(name_next)

            self.get_para_comment(name_pre_comment,para_name,name_pre,name_next)

    def add_comment_by_using_has_returns(self,has_returns_file):
        has_returns_relation = pd.read_csv(has_returns_file)
        for index, row in tqdm.tqdm(has_returns_relation.iterrows(),total=has_returns_relation.shape[0]):
            list_of_row = row.tolist()
            name_pre = list_of_row[0]
            name_next = list_of_row[1]
            name_pre_comment = self.get_the_node_description(name_pre)

            returns_name = self.get_simple_name(name_next)

            self.get_returns_comment(name_pre_comment,returns_name,name_pre,name_next)

    def add_comment_by_using_has_element(self,has_element_file):
        has_element_relation = pd.read_csv(has_element_file)
        for index, row in tqdm.tqdm(has_element_relation.iterrows(),total=has_element_relation.shape[0]):
            list_of_row = row.tolist()
            name_pre = list_of_row[0]
            name_next = list_of_row[1]
            name_pre_comment = self.get_the_node_description(name_pre)

            element_name = self.get_simple_name(name_next)

            self.get_element_comment(name_pre_comment, element_name, name_pre, name_next)

    def add_comment_by_using_has_relation(self):
        self.add_comment_by_using_has_para(self.configs.has_para_file)
        self.add_comment_by_using_has_returns(self.configs.has_returns_file)
        self.add_comment_by_using_has_element(self.configs.has_element_file)

    def add_fucntion_comment_by_using_function_clone_relation(self):


        function_clone_relation = pd.read_csv(self.configs.function_clone_file)
        functions_with_no_comment = self.node_information.loc[((self.node_information[':LABEL'] == 'Constructor') |
                                                         (self.node_information[':LABEL'] == 'Function') |
                                                         (self.node_information[':LABEL'] == 'Modifier') |
                                                         (self.node_information[':LABEL'] == 'Fallbackc')) &
                                                         (self.node_information['Description'] == 'no comment')]
        df_functions_names = pd.DataFrame(functions_with_no_comment['FEN:ID'])
        df_functions_names = df_functions_names.rename(columns={'FEN:ID':':START_ID'})
        function_clone_relation = pd.merge(function_clone_relation,df_functions_names,on=[':START_ID'],how='inner')
        for _, function_node_row in tqdm.tqdm(functions_with_no_comment.iterrows(),total=functions_with_no_comment.shape[0]):
            list_of_function_info = function_node_row.tolist()
            name_pre = list_of_function_info[0]

            simple_name_pre = self.get_simple_name(name_pre)

            name_pre_clones = function_clone_relation.loc[function_clone_relation[':START_ID'] == name_pre]

            function_comment = 'no comment'


            for index, row in name_pre_clones.iterrows():
                # print(index)
                list_of_row = row.tolist()
                name_next = list_of_row[1]
                simple_name_next = self.get_simple_name(name_next)

                name_next_comment = self.node_information.loc[self.node_information['FEN:ID'] == name_next][
                    'Description'].tolist()[0]
                if name_next_comment == 'no comment':
                    pass
                else:
                    if simple_name_pre == simple_name_next:
                        function_comment = name_next_comment

                        break
                    else:
                        pass

            self.node_information.loc[
                self.node_information['FEN:ID'] == name_pre, ('Description')] = function_comment

    def judge_Function_node_in_override_relations(self,node_name):
        if len(self.override_relation[self.override_relation[':START_ID'] == node_name]) == 1:
            return True
        elif len(self.override_relation[self.override_relation[':START_ID'] == node_name]) == 0:
            return False
        else:
            raise

    def judge_Abstract_Function_node_in_override_relations(self,node_name):
        if len(self.override_relation[self.override_relation[':END_ID'] == node_name]) > 0:
            return True
        else:
            return False

    def enrich_Function_comment_with_override_relation(self,node_name, node_type: str, description_sentence: str) -> str:
        node_description = description_sentence

        if (node_type == 'Function') | (node_type == 'Constructor') | (node_type == 'Fallback') | (
                node_type == 'Modifier'):

            if description_sentence == 'no comment':
                if self.judge_Function_node_in_override_relations(node_name):

                    override_relation = self.override_relation[self.override_relation[':START_ID'] == node_name]
                    next_node_name = override_relation[':END_ID'].to_list()[0]
                    next_node_description = \
                    self.node_information[self.node_information['FEN:ID'] == next_node_name]['Description'].to_list()[0]
                    node_description = next_node_description

        return node_description

    def enrich_Abstract_Function_comment_with_override_relation(self,node_name, node_type: str,
                                                                description_sentence: str) -> str:
        node_description = description_sentence
        if (node_type == 'Abstract_Function'):

            if description_sentence == 'no comment':
                if self.judge_Abstract_Function_node_in_override_relations(node_name):
                    override_relation = self.override_relation[self.override_relation[':END_ID'] == node_name]
                    pre_node_name = override_relation[':START_ID'].to_list()[0]
                    pre_node_description = \
                    self.node_information[self.node_information['FEN:ID'] == pre_node_name]['Description'].to_list()[0]
                    node_description = pre_node_description

        return node_description

    def spread_comment_by_using_override_relation(self):

        self.node_information['Description'] = self.node_information.apply(
            lambda x: self.enrich_Abstract_Function_comment_with_override_relation(x['FEN:ID'], x[':LABEL'],
                                                                              x['Description']), axis=1)
        self.node_information['Description'] = self.node_information.apply(
            lambda x: self.enrich_Function_comment_with_override_relation(x['FEN:ID'], x[':LABEL'],
                                                                     x['Description']), axis=1)

    def make_info_to_csv(self):
        df_node_information = pd.DataFrame(self.node_information)
        df_node_information.to_csv(self.configs.node_file, index=0)

    def enrich_comment(self):
        print('start to enrich comment')
        self.spread_comment_by_using_override_relation()
        self.node_information.to_csv(self.configs.saved_information_directory + 'node_information_after_spread_comment_by_using_override.csv', index=0)
        self.add_fucntion_comment_by_using_function_clone_relation()
        self.node_information.to_csv(
            self.configs.saved_information_directory + 'node_information_after_add_fucntion_comment_by_using_function_clone_relation.csv', index=0)
        self.add_comment_by_using_has_relation()
        self.node_information.to_csv(
            self.configs.saved_information_directory + 'node_information_after_add_comment_by_using_has_relation.csv', index=0)
        self.make_info_to_csv()



if __name__ == '__main__':

    enrich_description_object = enrich_description(configs())
    enrich_description_object.enrich_comment()
