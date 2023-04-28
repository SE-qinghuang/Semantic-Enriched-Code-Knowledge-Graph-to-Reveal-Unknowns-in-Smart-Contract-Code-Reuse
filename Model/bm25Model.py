from gensim.summarization.bm25 import BM25
import pickle
import re
import tqdm

class bm25_for_search:

    def __init__(self,configs):
        self.configs = configs

    def simple_tok(self,sent:str):
        return sent.split()

    def bm25_load(self):
        f = open(self.configs.bm25_model_path, 'rb')
        bm25_Model = pickle.load(f)
        f.close()
        corpus = self.load_corpus()
        dict_corpusid_FEN = self.load_dict_corpusid_FEN()

        return bm25_Model, corpus, dict_corpusid_FEN

    def get_function_entities(self):
        neo4j_command = 'match (node:Modifier) return node\
                         union\
                         match (node:Constructor) return node\
                         union\
                         match (node:Fallback) return node\
                         union\
                         match (node:Function) return node'
        function_entities = self.configs.graph.run(neo4j_command)
        return function_entities

    def function_name_of_camel_case(self, function_FEN):
        simple_function_name = function_FEN.split(':')[-1].split('(')[0]

        camel_case_candidates = []

        camel_case_exp = '([A-Z][a-z]+)'
        camel_case_reg = re.compile(camel_case_exp)
        camel_case_cut = camel_case_reg.findall(simple_function_name)

        if not camel_case_cut:
            camel_case_candidates.append(simple_function_name)
        else:
            remain = simple_function_name
            for e in camel_case_cut:
                remain = remain.replace(e, '')
            if remain:
                camel_case_candidates.append(remain)
            for e in camel_case_cut:
                camel_case_candidates.append(e)

        return camel_case_candidates

    def get_execution_tokens(self,execution):
        execution_tokens = re.findall('\d\[label = "(.*)\s*"\];', execution)
        return execution_tokens

    def make_list_element_to_string(self, list_with_string_element, string):
        for element in list_with_string_element:
            string += element + ' '
        return string

    def make_corpus(self, function_entities):
        corpus = []

        dict_corpusid_FEN = {}

        index = 0
        for function_entity in tqdm.tqdm(function_entities):
            merged_tokens = ''
            function_FEN = function_entity['node']['FEN']


            # #baseline
            # function_description = function_entity['node']['Description']
            # simple_function_name = self.function_name_of_camel_case(function_FEN)
            # merged_tokens = self.make_list_element_to_string(simple_function_name, merged_tokens)
            # if type(function_description) != str:
            #     function_description = ''
            # # if (function_description == 'no comment') & (simple_function_name!= ''):
            # #     function_description = ''
            # merged_tokens += function_description

            # our KG
            function_description = function_entity['node']['Description'].replace('\\n','\n')
            function_execution = function_entity['node']['Flow_Chart'].replace('\\n','\n')

            simple_function_name = self.function_name_of_camel_case(function_FEN)
            function_execution_tokens = self.get_execution_tokens(function_execution)
            merged_tokens = self.make_list_element_to_string(simple_function_name, merged_tokens)
            merged_tokens = self.make_list_element_to_string(function_execution_tokens, merged_tokens)
            merged_tokens += function_description

            merged_tokens = re.sub('[_().,{}\[\]]', ' ', merged_tokens)
            # merged_tokens = merged_tokens.casefold()
            corpus.append(merged_tokens)

            dict_corpusid_FEN[index] = function_FEN
            index += 1

        return corpus, dict_corpusid_FEN

    def train_bm25(self):
        print('start to train bm25 model...')
        function_entities = list(self.get_function_entities())

        corpus, dict_corpusid_FEN = self.make_corpus(function_entities)


        tok_corpus = [self.simple_tok(s) for s in corpus]
        bm25_Model = BM25(tok_corpus)
        f = open(self.configs.bm25_model_path, 'wb')
        pickle.dump(bm25_Model, f)
        f.close()

        f = open(self.configs.corpus_fpath, 'w')
        f.write(str(corpus))
        f.close()

        f = open(self.configs.dict_corpusid_FEN, 'w')
        f.write(str(dict_corpusid_FEN))
        f.close()



    def load_corpus(self):
        f = open(self.configs.corpus_fpath, 'r')
        corpus = f.read()
        f.close()
        return list(eval(corpus))

    def load_dict_merged_tokens_to_FEN(self):
        f = open(self.configs.dict_merged_tokens_to_FEN, 'r')
        dict_merged_tokens_to_FEN = f.read()
        f.close()
        return dict(eval(dict_merged_tokens_to_FEN))

    def load_dict_corpusid_FEN(self):
        f = open(self.configs.dict_corpusid_FEN, 'r')
        dict_corpusid_FEN = f.read()
        f.close()
        return dict(eval(dict_corpusid_FEN))

    def load_dict_corpusid_pt(self):
        f = open(self.configs.dict_corpusid_pt, 'r')
        dict_corpusid_pt = f.read()
        f.close()
        return dict(eval(dict_corpusid_pt))


