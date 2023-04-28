
class CFGnode():
    def __init__(self,cfgnode):
        self.cfgnode_id = cfgnode.node_id
        self.cfgnode_type = cfgnode.type

        self.cfgnode_rel = self.get_rel(cfgnode)

    #get the dict of next nodes.
    #key:node,value:son_true/son_false/normal
    def find_next_cfg_node(self,cfgnode):
        dict_next_cfg_node = {}
        for son in cfgnode.sons:
            next_node = son
            if cfgnode.son_false == next_node:
                label = 'son_false'
            elif cfgnode.son_true == next_node:
                label = 'son_true'
            else:
                label = 'normal'

            #find the next node
            if next_node not in dict_next_cfg_node:
                dict_next_cfg_node[next_node] = label

        return dict_next_cfg_node

    #get the relation of cfg nodes
    def get_rel(self,cfgnode):

        cfgnode_rel = []

        dict_next_cfg_node = self.find_next_cfg_node(cfgnode)
        for next_cfg_node in dict_next_cfg_node:

            cfgnode_rel.append([cfgnode,next_cfg_node,dict_next_cfg_node[next_cfg_node]])
        return cfgnode_rel




