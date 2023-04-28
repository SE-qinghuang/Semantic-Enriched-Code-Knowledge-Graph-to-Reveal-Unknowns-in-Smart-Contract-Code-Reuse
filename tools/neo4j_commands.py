from config import configs

class Neo4jCommands():
    def __init__(self, configs):
        self.configs = configs

    def get_neo4j_command_about_para(self, neo4j_command, list_of_parameter):

        if len(list_of_parameter) == 0:
            neo4j_command += " match(node) where not ((node)-[:has_parameter]->()) with node "
        else:
            neo4j_command += " match(node)-[relation:has_parameter]->() with node,count(relation) as rels where rels=%s " % (
                len(list_of_parameter))

            i = 0
            for parameter in list_of_parameter:
                para_entityType = 'Parameter_' + str(i)
                para_dataType = parameter.type.type
                neo4j_command += " match(node)-[:has_parameter]->(next_node:%s{Data_Type:'%s'}) with node " % (
                    para_entityType, para_dataType)
                i += 1
        return neo4j_command

    def get_neo4j_command_about_returns(self, neo4j_command, list_of_returns):
        if len(list_of_returns) == 0:
            neo4j_command += " match(node) where not ((node)-[:has_returns]->()) with node "
        else:
            neo4j_command += " match(node)-[relation:has_returns]->() \
                                with node,count(relation) as rels\
                                where rels=%s" % (len(list_of_returns))
            i = 0
            for returns in list_of_returns:
                returns_entityType = 'Returns_' + str(i)
                returns_dataType = returns.type.type
                neo4j_command += " match(node)-[:has_returns]->(next_node:%s{Data_Type:'%s'}) with node " % (
                    returns_entityType, returns_dataType)
                i += 1
        return neo4j_command

    def nodes_with_same_para_and_returns(self, list_of_parameter, list_of_returns):
        neo4j_command = 'optional '
        neo4j_command = self.get_neo4j_command_about_para(neo4j_command, list_of_parameter)
        neo4j_command = self.get_neo4j_command_about_returns(neo4j_command, list_of_returns)
        neo4j_command += "where node:Function OR node:Modifier OR node:Constructor OR node:Fallback with node return node"
        nodes = self.configs.graph.run(neo4j_command)
        return nodes

    def find_node_by_description_attribute(self, description):

        nodes_searched_by_description = self.configs.graph.run("\
        match(node:Function{description:'%s'}) return node\
        Union all\
        match(node:Modifier{description:'%s'}) return node\
        Union all\
        match(node:Constructor{description:'%s'}) return node\
        Union all\
        match(node:Fallback{description:'%s'}) return node"
                                                  % (description,description,description,description))

        list_of_nodes_searched_by_description = list(nodes_searched_by_description)
        return list_of_nodes_searched_by_description

    def find_nodes_of_function_clone(self, FEN):

        matched_nodes = self.configs.graph.run("match(pre_node{FEN:'%s'})-[:function_clone]->(node) return node" % (FEN))
        return matched_nodes