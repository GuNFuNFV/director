import enum
import os
from typing import List, Tuple, Dict

import yaml

from utility.functional_utility import call_handler
from ontology.recursivesystem import RecursiveSystem, RecursiveStructure, Vector


# the foundation of the programming model define the most basic building block the basic building block is NFtype,
# which is characterized with its state (parameters(configuration), per-flow state, classification), transitions
# based on its event

class NFTypeCategory(enum.Enum):
    COMPOSITION = 0
    STATEFUL_MATCH = 1
    STATELESS_MATCH = 2
    STATEFUL_NF = 3
    STATELESS_NF = 4
    SYSTEM = 5
    NONE = 6


category_str_to_enum: Dict[str, NFTypeCategory] = {
    "composition": NFTypeCategory.COMPOSITION,
    "stateful_match": NFTypeCategory.STATEFUL_MATCH,
    "stateless_match": NFTypeCategory.STATELESS_MATCH,
    "stateful_action": NFTypeCategory.STATEFUL_NF,
    "stateless_action": NFTypeCategory.STATELESS_NF,
    "system": NFTypeCategory.SYSTEM,
    # the same as stateful_action/stateless_action
    "stateful_nf": NFTypeCategory.STATEFUL_NF,
    "stateless_nf": NFTypeCategory.STATELESS_NF,
}


class FlowStateVariable(RecursiveStructure):
    def __init__(self, name, size):
        super().__init__()
        self.name = name
        self.type = None
        self.size = size
        # if size is string, convert to int
        if isinstance(self.size, str):
            self.size = int(self.size)


class Event(RecursiveStructure):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.children_events: list[Event] = []  # the list of more specific events


class Parameter(RecursiveStructure):
    def __init__(self, name):
        super().__init__()
        self.name = name


class NFType(RecursiveStructure):
    def __init__(self):
        super().__init__()
        self.category = NFTypeCategory.NONE
        self.possible_input_events: List[Event] = []
        self.possible_output_events: List[Event] = []

        self.parameters: RecursiveSystem = RecursiveSystem()
        self.flow_state_variables: list[FlowStateVariable] = []
        self.transition_system: RecursiveSystem = RecursiveSystem()

    def is_system(self):
        return self.category == NFTypeCategory.SYSTEM
    def is_stateful_action(self):
        return self.category == NFTypeCategory.STATEFUL_NF
    def is_top_level(self):
        return len(self.parent) == 0

    def is_abstract(self):
        # if it has a child, it is abstract
        if len(self.children) > 0:
            return True
        return False

    def is_concrete(self):
        return not self.is_abstract()

    def add_flow_state_variable(self, flow_state_variable: Dict):
        flow_state_variable_name = flow_state_variable["name"]
        flow_state_variable_size = flow_state_variable["size"]
        temp_flow_state_variable = FlowStateVariable(flow_state_variable_name, flow_state_variable_size)
        if temp_flow_state_variable not in self.flow_state_variables:
            self.flow_state_variables.append(temp_flow_state_variable)


    def get_category(self):
        return self.category

    def add_category(self, category_str: str):
        assert category_str in category_str_to_enum
        self.category = category_str_to_enum[category_str]

    def add_parameter(self, parameter: str):
        temp_parameter = Parameter(parameter)
        self.parameters.add_entry(temp_parameter)

    def add_possible_input_event(self, event: Event):
        self.possible_input_events.append(event)
        # remove duplicates
        self.possible_input_events = list(set(self.possible_input_events))

    def add_possible_output_event(self, event: Event):
        self.possible_output_events.append(event)
        # remove duplicates
        self.possible_output_events = list(set(self.possible_output_events))

    def add_name(self, name: str):
        self.name = name

    def __str__(self):
        return "{}:{}".format(self.name, self.category)

    def add_child(self, child: "NFType"):
        assert isinstance(child, NFType)
        super().add_child(child)
        self.possible_input_events.extend(child.possible_input_events)
        self.possible_input_events = list(set(self.possible_input_events))
        self.possible_output_events.extend(child.possible_output_events)
        self.possible_output_events = list(set(self.possible_output_events))

    def to_dict(self):
        return self.name


class NFTypeTransition(RecursiveStructure):
    def __init__(self, ):
        super().__init__()
        self.initial_nf_type = None
        self.event = None
        self.result_nf_type = None
        self.linked = False

    def set_initial_nf_type(self, nf_type: NFType):
        assert isinstance(nf_type, NFType)
        self.initial_nf_type = nf_type

    def set_input_event(self, event: Event):
        self.event = event

    def set_result_nf_type(self, nf_type: NFType):
        assert isinstance(nf_type, NFType)
        self.result_nf_type = nf_type

    def add_child(self, nf_type_transition: "NFTypeTransition"):
        assert isinstance(nf_type_transition, NFTypeTransition)
        super().add_child(nf_type_transition)

    def __str__(self):
        return "{} {} -> {}".format(self.initial_nf_type, self.event, self.result_nf_type)


def transition_str_to_transition_tuple(transition: str):
    # parse the transition
    # which is a string of the form "Type, Event -> Type"
    # first remove the spaces
    transition = transition.replace(" ", "")
    # check if the transition is valid
    # first split by ","
    transition_split_by_comma = transition.split(",")
    assert len(transition_split_by_comma) == 2
    # then split by "->"
    transition_split_by_arrow = transition_split_by_comma[1].split("->")
    assert len(transition_split_by_arrow) == 2
    transition_tuple = (
        transition_split_by_comma[0], transition_split_by_arrow[0], transition_split_by_arrow[1])
    # none of the result should be empty
    assert all(transition_tuple)
    # print("transition {} is valid".format(transition_tuple))
    return transition_tuple


class Factory:
    type_system: RecursiveSystem = RecursiveSystem()
    event_system: RecursiveSystem = RecursiveSystem()

    def __init__(self):
        start_nf_type = NFType()
        start_nf_type.add_name("Start")
        start_nf_type.add_category("system")
        self.type_system.add_entry(start_nf_type)

        end_nf_type = NFType()
        end_nf_type.add_name("End")
        end_nf_type.add_category("system")
        self.type_system.add_entry(end_nf_type)

    def add_event(self, event_name: str):
        # first lookup if the event already exists
        temp_event = self.event_system[event_name]
        if temp_event is not None:
            return temp_event
        # check whether it has a parent
        # if it contains a dot, then it has a parent
        if "." in event_name:
            parent_event_name = event_name.split(".")[0]
            parent_event = self.add_event(parent_event_name)
            temp_event = Event(event_name)
            parent_event.add_child(temp_event)
            self.event_system.add_entry(temp_event)
            return temp_event
        else:
            temp_event = Event(event_name)
            self.event_system.add_entry(temp_event)
            return temp_event

    def add_possible_input_event(self, nftype: NFType = None, transition_tuple: Tuple[str, str, str] = None):
        event_name = transition_tuple[1]
        temp_event = self.add_event(event_name)
        nftype.add_possible_input_event(temp_event)
        pass

    def add_possible_output_event(self, nftype: NFType = None,
                                  transition_tuple: Tuple[str, str, str] = None):
        event_name = transition_tuple[1]
        temp_event = self.add_event(event_name)
        nftype.add_possible_output_event(temp_event)
        pass

    def add_transition(self, nftype: NFType, transition_tuple: Tuple[str, str, str] = None):
        transition = NFTypeTransition()
        event_name = transition_tuple[1]
        event = self.add_event(event_name)
        transition.set_input_event(event)

        initial_nf_type_name = transition_tuple[0]
        if initial_nf_type_name == "Self":
            initial_nf_type = nftype
        else:
            initial_nf_type = self.type_system.lookup(name=initial_nf_type_name)
        if initial_nf_type is None:
            initial_nf_type = self.add_type(type_name=initial_nf_type_name)
            if initial_nf_type.category is NFTypeCategory.NONE:
                initial_nf_type.category = nftype.category
        initial_nf_type.add_possible_output_event(event)
        transition.set_initial_nf_type(initial_nf_type)
        result_nf_type_name = transition_tuple[2]
        if result_nf_type_name == "Self":
            result_nf_type = nftype
        else:
            result_nf_type = self.type_system.lookup(name=result_nf_type_name)
        if result_nf_type is None:
            result_nf_type = self.add_type(type_name=result_nf_type_name)
            if result_nf_type.category is NFTypeCategory.NONE:
                result_nf_type.category = nftype.category
        result_nf_type.add_possible_input_event(event)
        transition.set_result_nf_type(result_nf_type)
        name_tuple = (initial_nf_type_name, event_name, result_nf_type_name)
        transition.name = Vector(name_tuple)
        nftype.transition_system.add_entry(transition)

    def add_transitions(self, nftype: NFType, type_dict):
        transition_str_list = type_dict["transitions"]
        condition_to_handler = {
            lambda x: "Start" in transition_tuple[0]:
                [self.add_possible_input_event, self.add_transition],
            lambda x: "End" in transition_tuple[2]:
                [self.add_possible_output_event, self.add_transition],
            # wildcard
            lambda x: "Start" not in transition_tuple[0] and "End" not in transition_tuple[2]:
                [self.add_transition]
        }
        transition_tuple_list = []
        for transition_str in transition_str_list:
            transition_tuple = transition_str_to_transition_tuple(transition_str)
            transition_tuple_list.append(transition_tuple)
            call_handler(condition_to_handler, operand=transition_tuple, nftype=nftype,
                         transition_tuple=transition_tuple)

        for transition in nftype.transition_system:
            for transition2 in nftype.transition_system:
                if transition != transition2:
                    if transition.result_nf_type == transition2.initial_nf_type:
                        transition.add_child(transition2)

        for transition in nftype.transition_system:
            nftype_list = [transition.initial_nf_type, transition.result_nf_type]
            for temp_nftype in nftype_list:
                if temp_nftype.category != NFTypeCategory.SYSTEM and temp_nftype != nftype:
                    nftype.add_child(temp_nftype)

    def add_parameters(self, nftype: NFType, type_dict):
        if "parameters" not in type_dict:
            return
        param_list = type_dict["parameters"]
        for param in param_list:
            nftype.add_parameter(param)

    def add_flow_state_variables(self, nftype: NFType, type_dict):
        if "flow_state_variables" not in type_dict:
            raise Exception("flow_state_variables not in type_dict")
        flow_state_variables_list: List[Dict] = type_dict["flow_state_variables"]
        for flow_state_variable in flow_state_variables_list:
            nftype.add_flow_state_variable(flow_state_variable)

    def not_impl(self, temp_type: NFType, type_dict):
        print("Type {} is not implemented".format(type_name))
        exit(1)

    def add_type(self, type_name=None) -> NFType:
        temp_type = NFType()
        temp_type.name = type_name
        self.type_system.add_entry(temp_type)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        file_name = type_name + ".yaml"
        # file_path is current_dir + composed_nf_definition_file + file_name
        file_path = os.path.join(current_dir, "files", file_name)
        # if the file does not exist, which means no further information about the type
        if not os.path.exists(file_path):
            # print("Type {} is not specified".format(type_name))
            return temp_type
        # read the file yaml as dict
        with open(file_path, "r") as f:
            type_dict = yaml.load(f, Loader=yaml.FullLoader)
            # print(type_dict)
        assert "category" in type_dict
        assert "transitions" in type_dict
        temp_type.add_category(type_dict["category"])
        condition_to_handler = {
            lambda x: x.get_category() == NFTypeCategory.STATEFUL_MATCH:
                [self.add_transitions,
                 self.add_parameters],
            lambda x: x.get_category() == NFTypeCategory.STATELESS_MATCH:
                [],
            lambda x: x.get_category() == NFTypeCategory.STATEFUL_NF:
                [self.add_transitions,
                 self.add_parameters,
                 self.add_flow_state_variables],
            lambda x: x.get_category() == NFTypeCategory.STATELESS_NF:
                [self.add_transitions,
                 self.add_parameters],
            lambda x: x.get_category() == NFTypeCategory.SYSTEM:
                [self.add_transitions, self.add_parameters],
        }
        call_handler(condition_to_handler, operand=temp_type, nftype=temp_type,
                     type_dict=type_dict)
        return temp_type
        # temp_type.transition_system.visualize()

    def __str__(self):
        return str(self.type_system) + \
            "\n" + \
            str(self.event_system)


# get the composed_nf_definition_file under current_path + composed_nf_definition_file
current_path = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(current_path, "files")
file_list = os.listdir(file_path)
# get the type_list from the file_list
type_list = []
for file in file_list:
    if file.endswith(".yaml"):
        type_list.append(file.split(".")[0])

TypeFactory = Factory()
for type_name in type_list:
    TypeFactory.add_type(type_name)

type_system = TypeFactory.type_system
event_system = TypeFactory.event_system
# event_system.visualize()
