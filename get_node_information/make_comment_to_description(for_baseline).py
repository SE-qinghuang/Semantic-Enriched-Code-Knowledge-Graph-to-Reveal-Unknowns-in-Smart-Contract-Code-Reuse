import re
from config import configs
import pandas as pd

class comment_to_description():

    def __init__(self,configs):
        self.configs = configs

    def split_the_name(self,name):
        token_list_normalized = []

        identifier_candidates = []
        camel_case_candidates = []

        camel_case_exp = '([A-Z][a-z]+)'
        camel_case_reg = re.compile(camel_case_exp)
        camel_case_cut = camel_case_reg.findall(name)

        if not camel_case_cut:
            camel_case_candidates.append(name)
        else:

            remain = name
            for e in camel_case_cut:
                remain = remain.replace(e, '')
            if remain:
                camel_case_candidates.append(remain)
            for e in camel_case_cut:
                camel_case_candidates.append(e)

        for candidate in camel_case_candidates:
            if '_' not in candidate:
                identifier_candidates.append(candidate)
            else:
                under_line_cut = candidate.split('_')
                for e in under_line_cut:
                    if e:
                        identifier_candidates.append(e)

        token_list_normalized.extend(identifier_candidates)

        return token_list_normalized

    def get_simple_name(self,node_name):
        return node_name.split(':')[-1]

    def get_function_event_simple_name(self,node_name):
        name = node_name.split(':')[-1]
        simple_name = name.split('(')[0]
        return simple_name

    def format_function_event_comment(self,comment):
        out = self.format_the_comment(comment)
        if '@' in out:
            out = re.sub('@param (.*)\n', '', out)
            out = re.sub('@return (.*)\n', '', out)
            if out == '':
                out = 'no comment'

        return out

    def del_the_comment_function_event_dont_need(self,comment):
        out = re.sub('-+\.\n', '', comment)
        out = re.sub('/{2,}\.\n', '', out)
        out = re.sub('/{2,}', '', out)
        out = re.sub('={2,}','',out)
        out = re.sub('-{3,}', '', out)
        out = re.sub('\n[\s]*\*[\s]*\n','\n',out)



        return out

    def del_the_comment_dont_need(self,comment):
        out = re.sub('-+\.\n', '', comment)
        out = re.sub('/{2,}\.\n', '', out)
        out = re.sub('/{2,}', '', out)
        out = re.sub('={2,}','',out)
        out = re.sub('-{3,}', '', out)

        return out

    # if there is comment with the pattern of '/* ...*/
    def get_format_comment_with_pattern1(self,comment):
        # avoid the web string like : https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
        comment = comment.replace('/*', '')
        comment = comment.replace('*/', '')
        comment = comment.replace('*', '')

        list_of_comment = comment.split('\n')
        # comment = get_format_comment(list_of_comment)
        format_have_done = False

        while (format_have_done == False):
            # a = len(list_of_comment)

            list_have_changed = False

            for i in range(len(list_of_comment)):
                now_comment = list_of_comment[i].strip()
                if len(now_comment) == 0:
                    list_of_comment.pop(i)
                    list_have_changed = True
                    break

                # if the end is .,the sentence is end.
                if now_comment[-1] == '.':
                    list_of_comment[i] = now_comment + '\n'
                    continue

                elif now_comment[-1] == ':':
                    if (i + 1) >= len(list_of_comment):
                        list_of_comment[i] = now_comment
                    else:
                        next_comment = list_of_comment[i + 1].strip()
                        list_of_comment[i] = now_comment + ' ' + next_comment
                        list_of_comment.pop(i + 1)
                        list_have_changed = True
                        break
                else:
                    # if there is no '.' at the end,but no element exist in i+1 index
                    if (i + 1) >= len(list_of_comment):
                        list_of_comment[i] = now_comment + '.\n'

                    else:

                        # If the next word starts in lowercase
                        next_comment = list_of_comment[i + 1].strip()
                        if len(next_comment) == 0:
                            list_of_comment.pop(i + 1)
                            list_have_changed = True
                            break
                        if next_comment[0].islower():
                            list_of_comment[i] = now_comment + ' ' + next_comment
                            list_of_comment.pop(i + 1)
                            list_have_changed = True
                            break
                        else:
                            list_of_comment[i] = now_comment + '.\n'
            if list_have_changed:
                continue
            else:
                if len(list_of_comment) == 0:
                    break
                if i == len(list_of_comment) - 1:
                    format_have_done = True

        format_comment = ''
        for element in list_of_comment:
            format_comment += element
        return format_comment

    # if there is comment with the pattern of '//' or '///'
    def get_format_comment_with_pattern2(self,comment):

        comment = re.sub('/{2,}', '', comment)
        comment_list = comment.split('\n')
        format_have_done = False
        while (format_have_done == False):
            for i in range(len(comment_list)):
                now_comment = comment_list[i].strip()
                if len(now_comment) == 0:
                    comment_list.pop(i)
                    break

                if now_comment[-1] == '.':
                    comment_list[i] = now_comment + '\n'
                    continue
                else:
                    comment_list[i] = now_comment + '.\n'
            if i == len(comment_list) - 1:
                format_have_done = True
        format_comment = ''
        for element in comment_list:
            format_comment += element
        return format_comment

    def format_the_comment(self,comment):
        if ('/*' in comment) & ('*/' in comment):

            format_comment = self.get_format_comment_with_pattern1(comment)
        elif ('//' in comment) | ('///' in comment):
            format_comment = self.get_format_comment_with_pattern2(comment)
        else:
            if len(comment.strip()) == 0:
                format_comment = 'no comment'

            else:
                format_comment = comment

        return format_comment

    #need
    #handle Parameter and returns
    def convert_para_returns_comment_to_description(self,node_name,node_type,node_comment):
        if node_type == 'Parameter':
            simple_node_name = self.get_simple_name(node_name)
            if node_comment == 'no comment':
                node_description = ''
                node_description_list = self.split_the_name(simple_node_name)
                for description in node_description_list:
                    node_description += description + ' '
                node_description = node_description.strip()

            else:
                if re.match('@param\s*'+ simple_node_name +'\s*-\s*(.*)\n',node_comment):
                    node_description = re.match('@param\s*'+ simple_node_name +'\s*-\s*(.*)\n',node_comment).group(1)
                elif re.match('@param\s*'+ simple_node_name +'(.*)\n',node_comment):
                    node_description = re.match('@param\s*'+ simple_node_name +'(.*)\n',node_comment).group(1)
                else:
                    node_description = ''
                    # raise

        elif 'Returns' in node_type:
            if node_comment == 'no comment':
                node_description = "can't get returns's description"
            elif "fail to get returns" in node_comment:
                node_description = "can't get returns's description"
            elif node_comment == "can't get return's comment":
                node_description = "can't get returns's description"
            else:
                try:
                    node_description = re.match('@return (.*)\n', node_comment).group(1)
                except:
                    a = 1

        else:
            node_description = 'error when get para or returns description'
        try:
            if node_description == '':
                node_description = "can't get description"

            elif node_description[-1] == '.':
                node_description = node_description[:-1]
        except:
            node_description = ''

        return node_description


    #need
    #handle function and event
    def convert_function_event_comment_to_description(self,node_name,node_type,node_comment):
        if (node_type == 'Function') | (node_type == 'Abstract_Function') | (node_type == 'Constructor') |\
           (node_type == 'Fallback') | (node_type == 'Modifier') | (node_type == 'Event'):

            # 1.del the useless comment
            node_description = self.del_the_comment_function_event_dont_need(node_comment)
            #2.format the comment
            node_description = self.format_function_event_comment(node_description)

            simple_node_name = self.get_function_event_simple_name(node_name)
            if node_description == 'no comment':
                node_description = ''
                node_description_list = self.split_the_name(simple_node_name)
                for description in node_description_list:
                    node_description += description + ' '
                node_description = node_description.strip()

            else:


                if '@dev' in node_description:
                    try:
                        if re.match('[\s\S]*@dev (.*)\n',node_description):
                            node_description = re.match('[\s\S]*@dev (.*)\n',node_description).group(1)
                        elif re.match('[\s\S]*@dev (.*):',node_description):
                            node_description = re.match('[\s\S]*@dev (.*):', node_description).group(1)
                    except:
                        node_description = re.match('[\s\S]*@dev (.*) ', node_description).group(1)
                if '@notice' in node_description:
                    try:
                        node_description = re.match('[\s\S]*@notice (.*)\n',node_description).group(1)
                    except:
                        try:
                            node_description = re.match('[\s\S]*@notice (.*) ',node_description).group(1)
                        except:
                            node_description = re.match('[\s\S]*@notice (.*)',node_description).group(1)
        else:

            node_description = "error when get Variable's description"

        node_description = node_description.replace('\n','')
        node_description = node_description.strip()
        if node_description == '':
            simple_node_name = self.get_function_event_simple_name(node_name)
            node_description_list = self.split_the_name(simple_node_name)
            for description in node_description_list:
                node_description += description + ' '
            node_description = node_description.strip()

        return node_description

    #need
    #handle function and event
    def convert_contract_comment_to_description(self,node_name,node_type,node_comment):

        if (node_type == 'Contract') | (node_type == 'Library') | (node_type == 'Interface'):

            # 1.del the useless comment
            node_description = self.del_the_comment_function_event_dont_need(node_comment)
            #2.format the comment
            node_description = self.format_function_event_comment(node_description)

            simple_node_name = self.get_function_event_simple_name(node_name)
            if node_description == 'no comment':
                node_description = ''
                node_description_list = self.split_the_name(simple_node_name)
                for description in node_description_list:
                    node_description += description + ' '
                node_description = node_description.strip()

            else:

                if '@dev' in node_description:

                    node_description = re.sub('@dev', 'dev:', node_description)

                if '@title' in node_description:
                    node_description = re.sub('@title', 'title:', node_description)

        else:

            node_description = "error when get Variable's description"

        node_description = node_description.strip()

        return node_description


    #need
    #handle function and event
    def convert_element_comment_to_description(self,node_name,node_type,node_comment):

        if (node_type == 'Element'):

            # 1.del the useless comment
            node_description = self.del_the_comment_dont_need(node_comment)
            #2.format the comment
            node_description = self.format_the_comment(node_description)

            simple_node_name = self.get_simple_name(node_name)
            if node_description == 'no comment':
                node_description = ''
                node_description_list = self.split_the_name(simple_node_name)
                for description in node_description_list:
                    node_description += description + ' '
                node_description = node_description.strip()

            else:


                if simple_node_name in node_description:

                    node_description = re.sub(simple_node_name + '[\S\s]*:', '', node_description)

        else:

            node_description = "error when get element's description"

        node_description = node_description.strip()

        return node_description

    #need
    #handle Parameter and returns
    def convert_Variable_Struct_Enum_comment_to_description(self,node_name,node_type,node_comment):


        if (node_type == 'Variable') | (node_type == 'Struct') | (node_type == 'Enum'):

            # 1.del the useless comment
            node_comment = self.del_the_comment_dont_need(node_comment)
            #2.format the comment
            node_comment = self.format_the_comment(node_comment)

            simple_node_name = self.get_simple_name(node_name)
            if node_comment == 'no comment':
                node_description = ''
                node_description_list = self.split_the_name(simple_node_name)
                for description in node_description_list:
                    node_description += description + ' '
                node_description = node_description.strip()

            else:

                if '@dev' in node_comment:
                    try:
                        node_description = re.match('[\s\S]*@dev (.*)\n',node_comment).group(1)
                    except:
                        node_description = re.match('[\s\S]*@dev (.*) ', node_comment).group(1)
                else:
                    node_description = node_comment
        else:

            node_description = "error when get Variable's description"

        node_description = node_description.strip()
        if node_description[-1] == '.':
            node_description = node_description[:-1]

        return node_description

    def make_description(self,node_name, node_type:str,description_sentence:str)->str:
        try:
            description_sentence = re.sub('using\s+.*\s+for\s+.*?;', '', description_sentence)
        except:
            description_sentence = ''
        if '_' in node_type:
            if node_type =='Abstract_Function':
                pass
            else:
                node_type = node_type.split('_')[0]

        if (node_type == 'Parameter') | ('Returns' in node_type):
            node_description = self.convert_para_returns_comment_to_description(node_name,node_type,description_sentence)
        elif (node_type == 'Function') | (node_type == 'Abstract_Function') | (node_type == 'Constructor') | \
                (node_type == 'Fallback') | (node_type == 'Modifier') | (node_type == 'Event'):

            node_description = self.convert_function_event_comment_to_description(node_name,node_type,description_sentence)

        elif (node_type == 'Contract') | (node_type == 'Library') | (node_type == 'Interface'):
            node_description = self.convert_contract_comment_to_description(node_name,node_type,description_sentence)

        elif (node_type == 'Element'):
            node_description = self.convert_element_comment_to_description(node_name,node_type,description_sentence)

        elif (node_type == 'Variable') | (node_type == 'Struct') | (node_type == 'Enum'):
            node_description = self.convert_Variable_Struct_Enum_comment_to_description(node_name,node_type,description_sentence)
        elif node_type == 'Solidity Api':
            node_description = 'solidity api'
        else:
            node_description = 'error when converting comment to description'
        return node_description

    def make_comment_to_description(self):
        print('start to convert comment to description...')
        node_information = pd.read_csv(self.configs.node_file)

        node_information['Description'] = node_information.apply(
            lambda x: self.make_description(x['FEN:ID'], x[':LABEL'], x['Description']),axis=1)
        node_information.to_csv(self.configs.node_file, index=0)
        node_information.to_csv(self.configs.saved_information_directory + 'node_information_after_make_comment_to_description.csv',index=0)
        print('converting has done')


if __name__ == '__main__':

    comment_to_description_object = comment_to_description(configs())
    comment_to_description_object.make_comment_to_description()
