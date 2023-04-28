from py2neo import Graph
class configs:

    def __init__(self):

        self.contracts_directory = 'contracts'
        self.token2type_file = 'token2type'
        self.bug_file = 'output_from_process/bug'

        #node information
        self.node_to_comment_file = 'node/node_to_comment.csv'
        self.node_to_function_code_file = 'node/node_to_function_code.csv'
        self.node_to_type_file = 'node/node_to_type.csv'
        self.node_to_composition_count_file = 'node/node_to_composition_count.csv'
        self.order_sequence_file = 'node/order_sequence.csv'
        self.description_sentence_file = 'node/description_sentense.csv'
        self.keywords_file = 'node/keywords.csv'
        self.description_and_source_of_specific_variables_file = 'node/description_and_source_of_specific_variables.csv'
        self.node_to_description_file = 'node/description.csv'
        self.node_to_order_sequence = 'node/order_sequence.csv'
        self.node_to_returns = 'node/returns.csv'

        self.node_file = 'node/node.csv'

        self.model = 'train'         #train,update,do nothing
        self.word_2vec_dim = 150
        self.codebert_dim = 768
        self.word_2vec_array = 'Model/word2vec_array.npy'
        self.codebert_array = 'Model/codebert_array.npy'
        self.word_2vec_dict_model = 'Model/dim_{}_dic.bin'.format(self.word_2vec_dim)
        self.word_2vec_model = 'Model/dim_{}'.format(self.word_2vec_dim)
        self.tokens_file = 'Model/tokens.npy'
        self.functions_vecs_similarity_file = 'output_from_process/functions_vecs_similarity_file.csv'
        self.codeBertModel = '/home/auatac/liao_system/Recommendation_Baseline/CodeBert/demo/checkpoint-best-mrr-solidityKG'
        self.threshold_for_word2vec = 0.96
        self.threshold_for_codebert = 0.93
        self.epoch_num = 1

        #relation
        self.emit_event_relation_file = 'relations/emit_event.csv'
        self.calls_relation_file = 'relations/calls.csv'
        self.function_clone_file = 'relations/function_clone.csv'
        self.has_function_relation_file = 'relations/has_function.csv'
        self.has_event_relation_file = 'relations/has_event.csv'
        self.has_variable_file = 'relations/has_variable.csv'
        self.has_structure_file = 'relations/has_structure.csv'
        self.has_enum_file = 'relations/has_enum.csv'
        self.has_para_file = 'relations/has_para.csv'
        self.has_element_file = 'relations/has_element.csv'
        self.has_returns_file = 'relations/has_returns.csv'
        self.override_file = 'relations/override.csv'
        self.cooccurrence_relation = 'relations/cooccurrence.csv'

        #searching by bm25
        self.corpus_fpath = 'Model/bm25Model/corpus.txt'
        self.bm25_model_path = 'Model/bm25Model/bm25.pkl'
        self.dict_merged_tokens_to_FEN = 'Model/bm25Model/dict_merged_tokens_to_FEN.txt'
        self.dict_corpusid_FEN = 'Model/bm25Model/dict_corpusid_FEN.txt'
        self.dict_corpusid_pt = 'Model/bm25Model/dict_corpusid_pt.txt'

        # relation
        self.input_code_emit_event_relation_file = 'input/emit_event.csv'
        self.input_code_calls_relation_file = 'input/calls.csv'
        self.input_code_function_clone_file = 'input/function_clone.csv'
        self.input_code_has_function_relation_file = 'input/has_function.csv'
        self.input_code_has_event_relation_file = 'input/has_event.csv'
        self.input_code_has_variable_file = 'input/has_variable.csv'
        self.input_code_has_structure_file = 'input/has_structure.csv'
        self.input_code_has_enum_file = 'input/has_enum.csv'
        self.input_code_has_para_file = 'input/has_para.csv'
        self.input_code_has_element_file = 'input/has_element.csv'
        self.input_code_has_returns_file = 'input/has_returns.csv'


        #neo4j
        self.graph = Graph('http://localhost:7474', username='neo4j', password='123456')

        self.saved_information_directory = 'saved_datas/'

        #code checking
        self.model_threshold = 0.82
        self.checked_code_file = 'tools/test.sol'
        self.checking_result_file = 'tools/Templefile.json'
        self.checking_result_nums = 20
        #code recommendation
        self.top_n = 5
        self.FEN_to_vectors = 'Model/FEN_to_vectors.csv'
        self.list_of_FENs = 'Model/list_of_FENs.npy'