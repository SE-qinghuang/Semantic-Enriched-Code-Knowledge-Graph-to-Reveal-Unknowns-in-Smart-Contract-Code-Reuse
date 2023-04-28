import datetime
from config import configs
from get_node_information.get_node_information import Basic_node_and_relations
from get_relation.normalize_and_get_vec import normalize_and_get_vec
from get_relation.function_clone import function_clone
from get_node_information.composition_count import composition_count
from get_node_information.make_comment_to_description import comment_to_description
from get_node_information.enrich_comment_by_using_has_and_similar_relation import enrich_description
from get_relation.Flow_Chart import get_Flow_Chart
from get_relation.override import Override
from get_relation.Cooccurrence import Cooccurrence
from get_node_information.convert_line_to_string import convert
from Model.bm25Model import bm25_for_search

def make_solidity_kg():
    #get basic kg
    #nodes
    #relations : has,used it
    information_class = Basic_node_and_relations(configs())
    information_class.get_Basic_node_and_relations()

    #get override relation
    Override_class = Override(configs())
    Override_class.get_override_relations()

    #Enrichment
    #get tokens
    normalize_and_get_vec_object = normalize_and_get_vec(configs())
    normalize_and_get_vec_object.get_tokens()

    # #train the word2vec for code clone
    normalize_and_get_vec_object.handle_the_model()

    function_clone_object = function_clone(configs())
    function_clone_object.get_function_clone_relation()

    #if you want to check the implement result,run RQ1 and RQ2 first
    # 1 hour getting
    Composition_Count_object = composition_count(configs())
    Composition_Count_object.get_composition_count()

    enrich_description_object = enrich_description(configs())
    enrich_description_object.enrich_comment()

    comment_to_description_object = comment_to_description(configs())
    comment_to_description_object.make_comment_to_description()

    # get_execution
    flow_chart_object = get_Flow_Chart(configs())
    flow_chart_object. get_all_flow_chart()

    cooccurrence_object = Cooccurrence(configs())
    cooccurrence_object.get_cooccurrence_relations()
    #
    # convert_line_to_string_object = convert(configs())
    # convert_line_to_string_object.convert_special_symbol_to_string()

    # bm25_for_search_object = bm25_for_search(configs())
    # bm25_for_search_object.train_bm25()


if __name__ == '__main__':
    starttime = datetime.datetime.now()

    make_solidity_kg()
    endtime = datetime.datetime.now()
    print((endtime - starttime).seconds)

