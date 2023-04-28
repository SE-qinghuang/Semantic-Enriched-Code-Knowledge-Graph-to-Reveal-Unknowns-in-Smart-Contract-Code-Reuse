import re
from nltk.tokenize import word_tokenize
from gensim.models.word2vec import Word2Vec
import csv
import pandas as pd

from config import configs
import tqdm
import numpy as np

class normalize_and_get_vec():
    def __init__(self, configs):
        # normalize_and_get_vec.__init__(self, configs)
        self.configs = configs
        self.token2type_file = self.configs.token2type_file

    def get_dict_token_2_type(self):
        f = open(self.token2type_file, 'r')
        list_of_lines = f.readlines()
        f.close()
        pattern_get_token_type = re.compile('(.*)=(\d+)')
        dict_token_2_type = {}
        for line in list_of_lines:
            line = line.replace('\n','')
            token_name = pattern_get_token_type.match(line).group(1)
            token_name = token_name.replace("'",'')
            token_type = pattern_get_token_type.match(line).group(2)
            dict_token_2_type[token_name] = token_type
        return dict_token_2_type

    def normalize(self,token_list,token_type):


        token_list_normalized = []
        for i in range(len(token_list)):
            # print(i)
            # handle the comment
            if token_type[i] == "117" or token_type[i] == "118":
                pass
            # handle the punctuations
            elif token_type[i] == "2" or token_type[i] == "15" or token_type == '34':
                pass
                # handle the version
            elif token_type[i] == '95':
                token_list[i] = "VersionLiteral"
                token_list_normalized.append(token_list[i])
            # handle the string constant
            elif token_type[i] == "115":
                token_list[i] = "StringLiteral"
                token_list_normalized.append(token_list[i])
            # handle the DecimalNumber
            elif token_type[i] == "97":
                token_list[i] = "DecimalNumber"
                token_list_normalized.append(token_list[i])
            # handle the HexNumber
            elif token_type[i] == "98":
                token_list[i] = "HexNumber"
                token_list_normalized.append(token_list[i])
            # handle the HexLiteral
            elif token_type[i] == ",100":
                token_list[i] = "HexLiteral"
                token_list_normalized.append(token_list[i])
            # handle the identifier
            elif token_type[i] == "114":
                # token_list_normalized.append('%%%%' +token_list[i])

                identifier_candidates = []
                camel_case_candidates = []

                camel_case_exp = '([A-Z][a-z]+)'
                camel_case_reg = re.compile(camel_case_exp)
                camel_case_cut = camel_case_reg.findall(token_list[i])

                # print '113 Case:' + token_list[i]
                if not camel_case_cut:
                    camel_case_candidates.append(token_list[i])
                else:
                    token_list_normalized.append('%%%%' + token_list[i])
                    remain = token_list[i]
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
            # other situations : normal tokens
            else:
                token_list_normalized.append(token_list[i])

        normalized_tokens = []
        for e in token_list_normalized:
            if not e.startswith('%%%%'):
                e = e.lower()
            if len(e) == 1 and (e >= 'a' and e <= 'z'):
                e = e.replace(e, 'SimpleVar')
            normalized_tokens.append(e)
        # assert len(token_list_normalized) == len(normalized_tokens)
        return normalized_tokens

    def get_function_tokens(self,function_code):
        list_1 = ['+=', '-=', '*=', '/=', '>>=', '<<=', '==', '!=', ':=', '=:', '%=', '|=', '^=', '&=', '~', '[', ']', '->',
                  '++', '--', '**', '=>', '.', '||', '&&', '{', '}', '(', ')', ';', '?']

        list_2 = ['+', '>', '%', '<=', '<', '&', '>=', '-', ',', '|', '!', '/', '^', ':', '>>', '=', '<<', '*']

        function_code = self.first_split(function_code)
        token_list = re.split('\s+', function_code)
        function_tokens = []
        for token in token_list:
            if (self.judge_no_list1_element(list_1, token)):
                for element in list_2:
                    need_to_add = True
                    if element in token:
                        list_to_append = token.partition(element)
                        for little_token in list_to_append:
                            function_tokens.append(little_token)
                        need_to_add = False
                        break
                if need_to_add:
                    function_tokens.append(token)
            else:
                function_tokens.append(token)
        function_tokens = [i for i in function_tokens if (i != '')]

        return function_tokens

    def get_token_types(self,function_tokens, dict_token_2_type):
        token_types = []

        for token in function_tokens:
            if token in dict_token_2_type:
                token_types.append(dict_token_2_type[token])
            else:
                token_types.append('114')
        return token_types

    #del code annotation
    def del_code_annotation(self,function_code):
        function_code = re.sub('/[*][*][\s\S]*[*]/','',function_code)
        function_code = re.sub('//.*\\n','',function_code)
        return function_code

    def get_normalized_tokens(self, function_code):


        dict_token_2_type = self.get_dict_token_2_type()
        function_code = self.del_code_annotation(function_code)
        function_tokens = self.get_function_tokens(function_code)
        # function_tokens = ['modifier', 'onlyOwner', '{', 'if', '(', 'msg', '.', 'sender', '!=', 'owner', ')', 'revert', '(', ')', ';', 'day', '+=', '1', ';', '_', ';', '}']

        token_types = self.get_token_types(function_tokens, dict_token_2_type)
        normalized_tokens = self.normalize(function_tokens,token_types)
        return normalized_tokens

    # use re.sub to split the code
    def first_split(self,function_code):
        function_code = re.sub('\+=', ' += ', function_code)
        function_code = re.sub('-=', ' -= ', function_code)
        function_code = re.sub('\*=', ' *= ', function_code)
        function_code = re.sub('/=', ' /= ', function_code)
        function_code = re.sub('>>=', ' >>= ', function_code)
        function_code = re.sub('<<=', ' <<= ', function_code)
        function_code = re.sub('==', ' == ', function_code)
        function_code = re.sub('!=', ' != ', function_code)
        function_code = re.sub(':=', ' := ', function_code)
        function_code = re.sub('=:', ' =: ', function_code)
        function_code = re.sub('%=', ' %= ', function_code)
        function_code = re.sub('\|=', ' |= ', function_code)
        function_code = re.sub('\^=', ' ^= ', function_code)
        function_code = re.sub('&=', ' &= ', function_code)
        function_code = re.sub('~', ' ~ ', function_code)
        function_code = re.sub('\[', ' [ ', function_code)
        function_code = re.sub(']', ' ] ', function_code)
        function_code = re.sub('->', ' -> ', function_code)
        function_code = re.sub('\+\+', ' ++ ', function_code)
        function_code = re.sub('--', ' -- ', function_code)
        function_code = re.sub('\*\*', ' ** ', function_code)
        function_code = re.sub('=>', ' => ', function_code)
        function_code = re.sub('\.', ' . ', function_code)
        function_code = re.sub('\|\|', ' || ', function_code)
        function_code = re.sub('\&\&', ' && ', function_code)
        function_code = re.sub('\{', ' { ', function_code)
        function_code = re.sub('\}', ' } ', function_code)
        function_code = re.sub('\(', ' ( ', function_code)
        function_code = re.sub('\)', ' ) ', function_code)
        function_code = re.sub('\;', ' ; ', function_code)
        function_code = re.sub('\?', ' ? ', function_code)
        function_code = re.sub(',', ' , ', function_code)
        function_code = re.sub('\{', ' ', function_code)
        function_code = re.sub('}', ' ', function_code)
        function_code = re.sub('\[', ' ', function_code)
        function_code = re.sub(']', ' ', function_code)
        function_code = re.sub(',', ' ', function_code)
        function_code = re.sub('\(', ' ', function_code)
        function_code = re.sub('\)', ' ', function_code)
        function_code = re.sub(';', ' ', function_code)
        # del the modifier
        # influence the state of variable

        function_code = re.sub('\s+pure\s+', ' ', function_code)
        function_code = re.sub('\s+view\s+', ' ', function_code)
        function_code = re.sub('\s+constant\s+', ' ', function_code)
        function_code = re.sub('\s+private\s+', ' ', function_code)
        function_code = re.sub('\s+public\s+', ' ', function_code)
        function_code = re.sub('\s+internal\s+', ' ', function_code)
        function_code = re.sub('\s+external\s+', ' ', function_code)

        return function_code

    def judge_no_list1_element(self,list_1,token):
        for element in list_1:
            if element in token:
                return False
        return True

    def get_tokens(self):
        print('start to get tokens from functions')
        node_information = pd.read_csv(self.configs.node_file)
        tokens = []
        print('len : {}'.format(len(node_information)))
        for index, row in tqdm.tqdm(node_information.iterrows(),total=node_information.shape[0]):
            # print(index)
            list_of_row = row.tolist()

            node_type = list_of_row[1]
            function_code = list_of_row[4]


            # if ((node_type == 'Function') | (node_type == 'Abstract_Function' ) | (node_type == 'Constructor') | (node_type == 'Modifier')):
            if ((node_type == 'Function') | (node_type == 'Fallback' ) | (node_type == 'Constructor') | (node_type == 'Modifier')):


                function_normalized_token = self.get_normalized_tokens(function_code)
                tokens.append(function_normalized_token)

        tokens = np.array(tokens)
        np.save(self.configs.tokens_file, tokens)

    def train(self):
        print('start train word to vector')
        tokens = np.load(self.configs.tokens_file,allow_pickle=True)
        tokens = tokens.tolist()
        model = Word2Vec(min_count=1, size=self.configs.word_2vec_dim)
        model.build_vocab(tokens)
        model.train(tokens, total_examples=model.corpus_count, epochs=self.configs.epoch_num)
        model.wv.save_word2vec_format(self.configs.word_2vec_dict_model)
        model.save(self.configs.word_2vec_model)

    def update_model(self):
        """
        增量训练word2vec模型
        :param text: 经过清洗之后的新的语料数据
        :return: word2vec模型
        """

        print('start update the model')
        tokens = np.load(self.configs.tokens_file,allow_pickle=True)
        tokens = tokens.tolist()
        model = Word2Vec.load(self.configs.word_2vec_model)  # 加载旧模型
        model.build_vocab(tokens, update=True)  # 更新词汇表
        model.train(tokens, total_examples=model.corpus_count, epochs=self.configs.epoch_num)  # epoch=iter语料库的迭代次数；（默认为5）  total_examples:句子数。
        model.save(self.configs.word_2vec_model)
        model.wv.save_word2vec_format(self.configs.word_2vec_dict_model)

    def handle_the_model(self,):
        if self.configs.model == 'train':
            self.train()
        elif self.configs.model == 'update':
            self.update_model()
        elif self.configs.model == 'do nothing':
            pass
