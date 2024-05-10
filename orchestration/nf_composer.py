# declaration type: composition, match, action
# create enum for declaration type
import os

from ontology.recursivesystem import RecursiveSystem, RecursiveStructure

from orchestration.nf import type_system, event_system, NFType, Event, FlowStateVariable


def nf_definition_file_loader(nf_definition_file_name):
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder_name = "nf_composition"
    nf_definition_file_path = os.path.join(current_path, folder_name, nf_definition_file_name)
    return nf_definition_file_path


# this layer of abstraction is to make it possible to have multiple NFs with the same NFtype in the same NF system

class parse_result:
    def __init__(self, actor_1: str, actor_1_type: str, event: str, actor_2: str, actor_2_type: str):
        assert isinstance(actor_1, str)
        assert isinstance(actor_1_type, str)
        assert isinstance(event, str)
        assert isinstance(actor_2, str)
        assert isinstance(actor_2_type, str)
        self.nf_1 = actor_1
        self.nf_1_type = actor_1_type
        self.event = event
        self.nf_2 = actor_2
        self.nf_2_type = actor_2_type


def parse_statement(statement) -> (parse_result, bool):
    # break down the statement into tokens
    # three parts
    # actor, event, actor
    # first split by comma
    # then split by ->
    first_split = statement.split(",")
    if len(first_split) != 2:
        return 0, False
    second_split = first_split[1].split("->")
    if len(second_split) != 2:
        return 0, False
    actor_1 = first_split[0]
    if ":" in actor_1:
        split = actor_1.split(":")
        actor_1 = split[0]
        actor_1_type = split[1]
    else:
        actor_1_type = "unknown"
    event = second_split[0]
    actor_2 = second_split[1]
    if ":" in actor_2:
        split = actor_2.split(":")
        actor_2 = split[0]
        actor_2_type = split[1]
    else:
        actor_2_type = "unknown"
    return parse_result(actor_1, actor_1_type, event, actor_2, actor_2_type), True


# system_actor = {
#     "packet_in": Actor("packet_in", "system"),
#     "packet_out": Actor("packet_out", "system"),
#     "drop": Actor("drop", "system"),
#     "exit": Actor("exit", "system"),
# }


class NFDefinition(RecursiveStructure):
    def __init__(self, name: str, type: NFType):
        super().__init__()
        self.name = name
        self.type: NFType = type
        self.full_name = self.type.name + "#" + self.name # name is the instance name
        self._flowstate_variables_definitions: list[FlowStateVariableDefinition] = []

    def is_system_nf(self):
        return self.type.is_system()
    @property
    def per_flow_state_variable_definitions(self):
        assert self.is_stateful_nf()
        return self._flowstate_variables_definitions

    def add_per_flow_state_variable(self, variable: "FlowStateVariableDefinition"):
        assert self.is_stateful_nf()
        self._flowstate_variables_definitions.append(variable)

    def is_stateful_nf(self):
        return self.type.is_stateful_action()

    def get_children(self):
        children = []
        # add children recursively
        for child in self.children:
            children.append(child)
            children += child.get_children()
        return children

    def get_type(self) -> NFType:
        return self.type

    def is_top_level(self):
        return len(self.parent) == 0

    def is_abstract(self):
        return self.type.is_abstract()

    def is_concrete(self):
        return self.type.is_concrete()
    def __str__(self):
        return self.name + " " + self.type.name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.name, self.type))

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type.name,
            "is_abstract": self.is_abstract()
        }


class NFTransition(RecursiveStructure):
    def __init__(self, name: str):
        super().__init__()
        self.initial_nf: NFDefinition = None
        self.final_nf: NFDefinition = None
        self.name = name
        self.event: Event = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class FlowStateVariableDefinition(RecursiveStructure):
    def __init__(self, name):
        super().__init__()
        self._per_flow_state_variables: FlowStateVariable = None
        self._nf_definition = None
        self.name = name

    @property
    def size(self) -> int:
        return self._per_flow_state_variable.size

    @property
    def per_flow_state_variable(self) -> FlowStateVariable:
        return self._per_flow_state_variable

    @per_flow_state_variable.setter
    def per_flow_state_variable(self, value):
        self._per_flow_state_variable = value

    @property
    def nf_definition(self) -> NFDefinition:
        return self._nf_definition

    @nf_definition.setter
    def nf_definition(self, value):
        self._nf_definition = value

    def __str__(self):
        return self.name


class NFComposer:
    # one definition can run on one worker
    def __init__(self, nfd_name = None):
        self.state_list = None
        self.initial_state = None
        self.nfd_name = nfd_name
        self.machine = None
        self.statements = None
        self.nf_definition_system: RecursiveSystem[NFDefinition] = RecursiveSystem[NFDefinition]()
        self.type_system: RecursiveSystem[NFType] = type_system
        self.event_system: RecursiveSystem[Event] = event_system
        self.perflow_state_variable_system: RecursiveSystem[FlowStateVariableDefinition] = RecursiveSystem[
            FlowStateVariableDefinition]()
        self.nf_transition_system: RecursiveSystem[NFTransition] = RecursiveSystem[NFTransition]()


        if self.nfd_name is not None:
            if not self.nfd_name.endswith(".nfd"):
                self.nfd_name += ".nfd"
            dut_nfd_file = nf_definition_file_loader(self.nfd_name)
            self.compile(dut_nfd_file)

    def get_composed_nf_and_corresponding_type(self):
        top_level_nfd_list = self.get_top_level_nfd()
        temp_list = []
        for nfd in top_level_nfd_list:
            if nfd.is_system_nf():
                continue
            nfd_name = nfd.full_name
            type_name = nfd.type.name
            temp_list.append((nfd_name, type_name))
        return temp_list

    def get_related_type(self):
        top_level_nfd_list = self.get_top_level_nfd()
        temp_list = []
        for nfd in top_level_nfd_list:
            if nfd.is_system_nf():
                continue
            type_name = nfd.type.name
            temp_list.append(type_name)
        return temp_list
    def get_top_level_nfd(self):
        temp_list = []
        for nf in self.nf_definition_system:
            if nf.is_top_level():
                temp_list.append(nf)
        return temp_list

    def add_transition_within_nf(self, nf: NFDefinition):
        # print(actor.type.transition_system)
        for child_nf_1 in nf.children:
            for child_nf_2 in nf.children:
                for transition in nf.type.transition_system:
                    if transition.initial_nf_type == child_nf_1.type and transition.result_nf_type == child_nf_2.type:
                        self.add_transitions(child_nf_1, child_nf_2, transition.event)

    def add_transitions(self, initial_nf: NFDefinition, final_nf: NFDefinition, event: Event):
        # add the transition to the system
        # if none of the nfs have childeren, add the transition
        # if one of the nfs has children, add the transition to all the children instead
        initial_nf_children_number = len(initial_nf.children)
        final_nf_children_number = len(final_nf.children)
        if initial_nf_children_number == 0 and final_nf_children_number == 0:
            # add only if event in the initial_nf possible input events and final_nf possible output events
            if event not in initial_nf.type.possible_output_events \
                    or self.event_system.is_or_is_child_of_one_item_in_list(
                final_nf.type.possible_input_events, event) == False:
                return

            transition = NFTransition(initial_nf.name + "_" + event.name + "_" + final_nf.name)
            # replace "." with ":" in the name
            transition.name = transition.name.replace(".", ":")
            # check if the transition already exists
            if transition in self.nf_transition_system:
                return
            transition.initial_nf = initial_nf
            transition.final_nf = final_nf
            transition.event = event
            self.nf_transition_system.add_entry(transition)
        else:
            # only add if compatible
            if initial_nf_children_number != 0 and final_nf_children_number == 0:
                for child in initial_nf.children:
                    self.add_transitions(child, final_nf, event)
            elif initial_nf_children_number == 0 and final_nf_children_number != 0:
                for child in final_nf.children:
                    self.add_transitions(initial_nf, child, event)
            else:
                for child_1 in initial_nf.children:
                    for child_2 in final_nf.children:
                        self.add_transitions(child_1, child_2, event)

    def preprocessor(self):
        # remove comments
        # remove spaces
        # remove newlines
        # in place
        for i in range(len(self.statements)):
            self.statements[i] = self.statements[i].split("#")[0].strip()
            self.statements[i] = self.statements[i].replace(" ", "")
            self.statements[i] = self.statements[i].replace("\t", "")
            self.statements[i] = self.statements[i].replace("\n", "")

    def compile(self, function_requirement_file):
        self.nfd_name = function_requirement_file.split(".")[0]
        # get the current path of the file
        current_path = os.path.dirname(os.path.abspath(__file__))
        # get the path of the file to be added
        # file_path is current_path + composed_nf_definition_file + filename
        file_path = os.path.join(current_path, "nf_composition", function_requirement_file)
        # add '.nfd' to the end of the file name if it is not there
        if not file_path.endswith(".nfd"):
            file_path += ".nfd"
        with open(file_path, 'r') as stream:
            # read lines as a list of statements
            self.statements = stream.readlines()
        self.preprocessor()
        self.parse_statements()
        # self.visualize()

    def declared(self, name):
        return self.nf_definition_system[name] is not None

    def declare(self, name, nftype: NFType) -> NFDefinition:
        # declare the actor of NFType type
        # to declare nf, its children must be declared
        # if not, declare them recursively
        temp_nf = NFDefinition(name, nftype)
        if nftype.children is not None:
            for child in nftype.children:
                child_name = name + "_" + str(nftype.children.index(child))
                child_nf = self.declare(child_name, child)
                temp_nf.add_child(child_nf)
        self.nf_definition_system.add_entry(temp_nf)
        if nftype.is_stateful_action():
            for state_variable in nftype.flow_state_variables:
                per_flow_state_variable_name = name + "_" + state_variable.name
                state_variable_definition = FlowStateVariableDefinition(per_flow_state_variable_name)
                state_variable_definition.nf_definition = temp_nf
                state_variable_definition.per_flow_state_variable = state_variable
                temp_nf.add_per_flow_state_variable(state_variable_definition)
                self.perflow_state_variable_system.add_entry(state_variable)
        return temp_nf

    def parse_statements(self):
        # check whether each statement is value
        # if not, return false
        # if yes, parse the statement
        for statement in self.statements:
            # parse the statement
            result, status = parse_statement(statement)
            try:
                assert status is True
            except AssertionError:
                print("Parsing Error: " + statement)
                exit(1)
            if not self.declared(result.nf_1):
                # assert that it has a type not unknown
                try:
                    assert result.nf_1_type != "unknown"
                except AssertionError:
                    print("Parsing Error: " + statement)
                    exit(1)
                temp_nf_name = result.nf_1
                temp_nf_type = self.type_system[result.nf_1_type]
                assert temp_nf_type is not None
                nf_1 = self.declare(temp_nf_name, temp_nf_type)
            else:
                # its type must be unknown, otherwise it is a redeclaration
                assert result.nf_1_type == "unknown"
                nf_1 = self.nf_definition_system[result.nf_1]
            # check whether temp_actor_2 is declared
            if not self.declared(result.nf_2):
                # assert that it has a type not unknown
                assert result.nf_2_type != "unknown"
                temp_nf_name = result.nf_2
                temp_nf_type = self.type_system[result.nf_2_type]
                assert temp_nf_type is not None
                nf_2 = self.declare(temp_nf_name, temp_nf_type)
            else:
                # its type must be unknown, otherwise it is a redeclaration
                assert result.nf_2_type == "unknown"
                nf_2 = self.nf_definition_system[result.nf_2]

            temp_event = self.event_system[result.event]
            if temp_event is None:
                raise Exception("Event not found")
            # check whether the transition is valid
            # temp_event must be in actor2.type.possible_input_events
            if not self.event_system.is_or_is_child_of_one_item_in_list(nf_2.type.possible_input_events, temp_event):
                raise Exception("Transition not valid")
            # temp_event must be in actor1.type.possible_output_events
            if temp_event not in nf_1.type.possible_output_events:
                raise Exception("Transition not valid")
            self.add_transition_within_nf(nf_1)
            self.add_transition_within_nf(nf_2)
            # add the transition
            self.add_transitions(nf_1, nf_2, temp_event)

        actor_transition_1: NFTransition
        actor_transition_2: NFTransition
        for actor_transition_1 in self.nf_transition_system:
            for actor_transition_2 in self.nf_transition_system:
                if not isinstance(actor_transition_1, NFTransition):
                    continue
                if not isinstance(actor_transition_2, NFTransition):
                    continue
                if actor_transition_1.final_nf == actor_transition_2.initial_nf:
                    actor_transition_1.add_child(actor_transition_2)
        # print(self.actor_definition_system)

        # compile it into a state machine
        self.state_list = []
        self.initial_state = ""

        exist_receive_packet = False
        for nf_transition in self.nf_transition_system:
            initial_actor = nf_transition.initial_nf
            if initial_actor.type.name == "receive_packet":
                exist_receive_packet = True
                self.initial_state = initial_actor.full_name
            initial_actor_name = initial_actor.full_name
            final_nf = nf_transition.final_nf
            final_nf_name = final_nf.full_name
            self.state_list.append(initial_actor_name)
            self.state_list.append(final_nf_name)
            # remove duplicates
            self.state_list = list(dict.fromkeys(self.state_list))
        if not exist_receive_packet:
            # the initial state should be the first state in the first transition
            self.initial_state = self.nf_transition_system[0].initial_nf.full_name

    def visualize(self):
        from transitions.extensions import GraphMachine
        transition_list = []
        for actor_transition in self.nf_transition_system:
            initial_actor = actor_transition.initial_nf
            initial_actor_name = initial_actor.full_name
            final_actor = actor_transition.final_nf
            final_actor_name = final_actor.full_name
            event = actor_transition.event
            transition_list.append({'trigger': event.name, 'source': initial_actor_name, 'dest': final_actor_name})

        self.machine = GraphMachine(model=self, states=self.state_list, transitions=transition_list,
                                    initial=self.initial_state)
        # plot the state machine
        # import pygraphviz
        # vertical layout
        file_name = self.nfd_name + ".png"
        self.machine.get_graph().draw(file_name, prog='dot')


if __name__ == "__main__":
    nf_definition_factory = NFComposer()
    nf_definition_factory.compile("cuckoo_hash_generic.nfd")
