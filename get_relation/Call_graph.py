from slither.slither import Slither
import slither.printers.all_printers as printer
import slither.printers.functions.cfg
import logging
from slither.printers.call.call_graph import _process_function,_process_external_call
from collections import defaultdict
from slither.core.declarations.solidity_variables import SolidityFunction
from slither.core.declarations.function import Function
from slither.core.variables.variable import Variable
import csv


# return unique id for contract function to use as node name
def _function_node(contract, function):
    # return contract.source_mapping['filename_absolute']+ ':' + str(contract) + ':' + function.canonical_name.replace('.',':')
    a = contract.source_mapping['filename_absolute']
    b = function.canonical_name.replace('.',':')
    return contract.source_mapping['filename_absolute']+ ':' + function.canonical_name.replace('.',':')

# return unique id for solidity function to use as node name
def _solidity_function_node(solidity_function):
    return solidity_function.name

# return dot language string to add graph edge
def _edge(from_node, to_node):
    return from_node+ " -> " + to_node

# return dot language string to add graph node (with optional label)
def _node(node, label=None):
    return " ".join(
        (
            f'"{node}"',
            f'[label="{label}"]' if label is not None else "",
        )
    )

# pylint: disable=too-many-arguments
def _process_internal_call(
    contract,
    function,
    internal_call,
    contract_calls,
    solidity_functions,
    solidity_calls,
):
    if isinstance(internal_call, (Function)):
        contract_calls[contract].add(
            _edge(
                _function_node(contract, function),
                _function_node(contract, internal_call),
            )
        )
    elif isinstance(internal_call, (SolidityFunction)):
        solidity_functions.add(
            _node(_solidity_function_node(internal_call)),
        )
        solidity_calls.add(
            _edge(
                _function_node(contract, function),
                _solidity_function_node(internal_call),
            )
        )

def _process_external_call(
    contract,
    function,
    external_call,
    contract_functions,
    external_calls,
    all_contracts,
):
    external_contract, external_function = external_call

    if not external_contract in all_contracts:
        return

    # add variable as node to respective contract
    if isinstance(external_function, (Variable)):
        contract_functions[external_contract].add(
            _node(
                _function_node(external_contract, external_function),
                external_function.name,
            )
        )

    external_calls.add(
        _edge(
            _function_node(contract, function),
            _function_node(external_contract, external_function),
        )
    )

# pylint: disable=too-many-arguments
def _process_function(
    contract,
    function,
    contract_functions,
    contract_calls,
    solidity_functions,
    solidity_calls,
    external_calls,
    all_contracts,
):
    contract_functions[contract].add(
        _node(_function_node(contract, function), function.name),
    )

    for internal_call in function.internal_calls:
        _process_internal_call(
            contract,
            function,
            internal_call,
            contract_calls,
            solidity_functions,
            solidity_calls,
        )
    for external_call in function.high_level_calls:
        _process_external_call(
            contract,
            function,
            external_call,
            contract_functions,
            external_calls,
            all_contracts,
        )

def _process_functions(functions):
    contract_functions = defaultdict(set)  # contract -> contract functions nodes
    contract_calls = defaultdict(set)  # contract -> contract calls edges

    solidity_functions = set()  # solidity function nodes
    solidity_calls = set()  # solidity calls edges
    external_calls = set()  # external calls edges
    all_contracts = set()   # all contracts in sol file


    for function in functions:
        all_contracts.add(function.contract_declarer)

    for function in functions:
        _process_function(
            function.contract_declarer,
            function,
            contract_functions,
            contract_calls,
            solidity_functions,
            solidity_calls,
            external_calls,
            all_contracts,
        )
    call_list = []

    for contract in all_contracts:
        for call in contract_calls[contract]:
            call_list.append(call)
    for call in solidity_calls:
        call_list.append(call)
    for call in external_calls:
        call_list.append(call)


    return call_list

class Callgraph(printer.PrinterCallGraph):

    def output(self):
        """
        Output the graph in filename
        Args:
            filename(string)
        """
        list_of_calls_relation = []
        relation = 'Calls'

        call_list =_process_functions(self.slither.functions)
        for call in call_list:
            function_list = call.split(' -> ')
            function1_name = function_list[0]
            function2_name = function_list[1]
            relation_lists = [function1_name, function2_name, relation]
            list_of_calls_relation.append(relation_lists)
        return list_of_calls_relation


def get_Calls_relation(sol):
    logger = logging.getLogger("Slither")
    logging.basicConfig()

    # sol = Slither(sol_file)
    callgraph = Callgraph(sol,logger)
    list_of_calls_relation = callgraph.output()
    return list_of_calls_relation

if __name__ == '__main__':
    sol_file = 'AhooleeTokenPreSale.sol'
    relation_file = 'relation.csv'
    list_of_calls_relation = get_Calls_relation(sol_file)
    a = 1


