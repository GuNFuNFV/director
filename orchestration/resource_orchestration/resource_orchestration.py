import json
import math
import os
from copy import copy, deepcopy
from typing import Optional, Protocol

import yaml
from pandas import Series

from orchestration.nf import NFTypeCategory, NFType
from orchestration import load_composed_nf
from orchestration.configuration_template.filling_template import get_configuration_dict_list
from orchestration.nf_composer import NFDefinition, FlowStateVariableDefinition, NFComposer
from utility import make_print_depth, call_handler, type_to_string, debug_print
from ontology.recursivesystem import RecursiveStructure, RecursiveSystem
from ontology.system import HomoSystem, ManagerSystem

from enum import Enum


class PrefetchStrategy(Enum):
    NONE = 0
    ONCE_ONE_CACHELINE = 1
    ONCE_TWO_CACHELINE = 2
    ONCE_FOUR_CACHELINE = 3
    ONCE_EIGHT_CACHELINE = 4
    TWICE_ONE_CACHELINE = 5  # for second level classifier, since it is likely not in the cache. First prefetch the pointer, then the data structure itself


class EntryEvent(Enum):
    LOAD_PERFLOW_STATE = 0
    LOAD_CLASSIFIER_STATE = 1
    LOAD_CONTROL_STATE = 2
    DO_NOTHING = 3


class State(RecursiveStructure):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "State"


class PerFlowStateVariable(State):
    def __init__(self):
        super().__init__()
        self.perflow_state_variable_definition: Optional[FlowStateVariableDefinition] = None
        self.nf_definition_id = None

    def to_dict(self):
        return dict({
            "name": self.perflow_state_variable_definition.nf_definition.type.name,
            "orchestration": self.nf_definition_id,
            "size": self.perflow_state_variable_definition.size,
        })


class ControlState(State):
    def __init__(self):
        super().__init__()
        self.nf_definition_id = None
        self.associated_nf_definition_list = []
        self.transition_configuration = {}
        self.parameter_dict = {}  # this is the parameter dict for the NFType
        self.type = None

    def __str__(self):
        return "ControlState" + " " + str(self.nf_definition_id)

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        if self.nf_definition_id is None:
            return dict()
        # get the parameter space of the nf definition
        temp_dict = {}
        parameter_dict = {"transition": {}}
        for parameter in self.transition_configuration:
            parameter_dict["transition"] |= {parameter: self.transition_configuration[parameter]}
        temp_dict["parameters"] = parameter_dict
        temp_dict["parameters"] |= self.parameter_dict
        temp_dict["composed_nf"] = self.nf_definition_id
        temp_dict["type"] = self.type
        return temp_dict

    def get_entry_num(self):
        if "cuckoo_hash_entry_num" in self.parameter_dict:
            return self.parameter_dict["cuckoo_hash_entry_num"]
        if "interval_tree_depth" in self.parameter_dict:
            return self.parameter_dict["interval_tree_depth"]
        else:
            raise Exception("ControlState does not have size")

    def get_entry_size(self):
        # return entry size in terms of number of cache lines
        if "generic_access_size" in self.parameter_dict:
            return self.parameter_dict["generic_access_size"] * 64
        if "cuckoo_hash_entry_num" in self.parameter_dict:  # it is a hash table, return pointer size
            return 8
        if "interval_tree_depth" in self.parameter_dict:
            return 8
        if "reserved" in self.parameter_dict:
            return 512
        if "amf_free5gc" in self.parameter_dict:
            return 2048
        else:
            raise Exception("ControlState does not have size")


class StatefulMatchActorState(State):
    def __init__(self):
        super().__init__()
        self.type: Optional[NFType] = None

    def __str__(self):
        return "StatefulMatchActorState" + " " + str(self.type)

    def to_dict(self):
        return dict({
            "classifier_name": self.classifier_name,
            "control_state_id": self.control_state_id,
        })


class Actor(ManagerSystem):
    def __init__(self):
        super().__init__()
        self.manage_type(ControlState)
        self.manage_type(NFDefinition)
        self.manage_type(NFType)
        self.manage_type(DataBlock)
        self.datablock_id = -1
        self.datablock_offset = 0
        self.control_state: ControlState = None
        self.entry_event = EntryEvent.DO_NOTHING

    def to_dict(self):
        temp_dict = {}
        for managed_type, component in self.managed_type.items():
            for id, obj in component.items():
                try:
                    # obj.manager_type_component_type_to_id maps the type of the component to the id of the component
                    # in different manager system in Worker
                    # only choose the manager system that is the most specific
                    # for example, if the managed_type is StatefulMatchActorState, then the most specific manager system
                    # is StatefulMatchActorState instead of State,
                    # although it is managed by both State and StatefulMatchActorState
                    temp_dict[type_to_string(managed_type)] = obj.manager_type_component_type_to_id[WorkerSetting][
                        type_to_string(managed_type)]
                except KeyError:
                    print("KeyError: ", managed_type, obj)
        temp_dict["datablock_id"] = self.datablock_id
        temp_dict["datablock_offset"] = self.datablock_offset
        temp_dict["abstract"] = self.is_abstract()
        temp_dict["entry_event"] = self.entry_event.value
        return temp_dict

    def set_definition(self, nf_definition: NFDefinition):
        assert isinstance(nf_definition, NFDefinition)
        self.add_component(nf_definition)
        self.add_component(nf_definition.type)

    def get_definition(self) -> NFDefinition | None:
        if len(self[NFDefinition]) == 0:
            return None
        return self[NFDefinition][0]

    def is_abstract(self):
        return self.get_definition().is_abstract()

    def is_top_level(self):
        return self.get_definition().is_top_level()

    def get_type(self):
        return self.get_definition().get_type()

    def add_control_state(self, control_state: ControlState):
        assert isinstance(control_state, ControlState)
        self.control_state = control_state

    def __str__(self):
        return "Actor" + " " + str(self.get_definition())


class SystemActor(Actor):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "SystemActor" + " " + str(self.get_definition())


class StatelessMatchActor(Actor):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "StatelessMatchActor" + " " + str(self.get_definition())


class StatefulMatchActor(Actor):
    def __init__(self):
        super().__init__()
        self.manage_type(StatefulMatchActorState)

    def __str__(self):
        return "StatefulMatchActor" + " " + str(self.get_definition())


class StatefulActionActor(Actor):
    def __init__(self):
        super().__init__()
        self.manage_type(PerFlowStateVariable)

    def __str__(self):
        return "StatefulActionActor" + " " + str(self.get_definition())


class StatelessActionActor(Actor):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "StatelessActionActor" + " " + str(self.get_definition())


class DataBlock(RecursiveStructure):
    def __init__(self):
        super().__init__()
        # one data slot can hold multiple kind of data
        # it could be used to hold match state
        # or it can be used to hold per flow state
        # the data slot are organized as a tree structure
        # each nf is associated with a data slot
        # the id of the data slot is determined dynamically
        # based on the result of the potential match
        self.nf_definition_id = -1
        self.control_state = None
        self.num_flow_differentiated_per_entry = 0  # the number of entries per bucket; how many flows can be supported
        # num_flow_differentiated_per_entry * bucket_num = total_entry_num
        self.total_entry_num = 0  # the number of total entries for the level

        # if it is a first level classifier, then the bucket_num is 1
        self.datablock_id = 0
        self.size = 0
        self.type = None  # datablock type can be classifier or per-flow state

    def to_dict(self):
        return dict({
            "type": self.type,
            "datablock_id": self.datablock_id,
            "control_state_id": self.control_state.get_id(WorkerSetting, ControlState),
            "num_flow_differentiated_per_entry": self.num_flow_differentiated_per_entry,
            "total_entry_num": self.total_entry_num,
            "size": self.size,
        })

    def __str__(self):
        return "[DataSlot" + " " + str(self.nf_definition_id) + " " + str(
            self.num_flow_differentiated_per_entry) + " " + str(
            self.level) + "]"

    def __getitem__(self, key):
        if key == "entry_num":
            return self.num_flow_differentiated_per_entry
        elif key == "level":
            return self.level


class WorkerSetting(ManagerSystem):
    def __init__(self, manager, worker_dict: dict, **kwargs):
        super().__init__(manager=manager)
        self.manage_type(NFType)
        self.manage_type(NFDefinition)
        self.manage_type(SystemActor)
        self.manage_type(StatelessMatchActor)
        self.manage_type(StatefulMatchActor)
        self.manage_type(StatefulActionActor)
        self.manage_type(StatelessActionActor)
        self.manage_type(Actor)
        self.manage_type(ControlState)
        self.manage_type(PerFlowStateVariable)
        self.manage_type(StatefulMatchActorState)
        self.manage_type(State)
        self.manage_type(DataBlock)
        self.worker_control_state: ControlState = ControlState()
        self.add_component(self.worker_control_state)
        self.optimization_options = kwargs["optimization_options"]
        worker_control_state_name = "{0}".format(self.name)
        self.worker_control_state.name = worker_control_state_name
        self.add_component(self.worker_control_state)

        self.composed_nf = worker_dict["worker_composed_nf"]
        # self.worker_prefetch_perflow = worker_dict["worker_prefetch_perflow"]
        if worker_dict["worker_composed_nf"] == "traffic_generator":
            self.worker_tx_mode = 1
            self.worker_rx_port = 0
            self.worker_tx_port = 0
            self.port_num = 1
        else:
            self.worker_tx_mode = 0
            self.worker_rx_port = 0
            self.worker_tx_port = 0
            self.port_num = 1
        self.worker_core_id = worker_dict["core_id"]
        self.worker_queue_id = worker_dict["queue_id"]
        if "worker_destination_instance" in worker_dict:
            self.worker_destination_instance = worker_dict["worker_destination_instance"]
        else:
            self.worker_destination_instance = 0
        self.worker_num_interleaved = worker_dict["num_possible_interleaved_threads"]
        self.initial_actor = 0

        composed_nf = load_composed_nf(self.composed_nf)
        for transition in composed_nf.nf_transition_system:
            if transition.initial_nf.type.name == "receive_packet":
                final_nf_nf_definition = transition.final_nf
                final_nf_nf_definition_id = composed_nf.nf_definition_system.index(final_nf_nf_definition)
                self.initial_actor = final_nf_nf_definition_id

        type_category_to_actor_initialization = {
            lambda x: x is NFTypeCategory.SYSTEM: [SystemActor],
            lambda x: x is NFTypeCategory.STATEFUL_MATCH: [StatefulMatchActor],
            lambda x: x is NFTypeCategory.STATELESS_MATCH: [StatelessMatchActor],
            lambda x: x is NFTypeCategory.STATEFUL_NF: [StatefulActionActor],
            lambda x: x is NFTypeCategory.STATELESS_NF: [StatelessActionActor],
        }

        for nf_definition in composed_nf.nf_definition_system:
            # based on each definition, generate an actor for the worker
            result = call_handler(type_category_to_actor_initialization, operand=nf_definition.type.category)
            actor = result[0]
            actor.worker_name = self.name  # deploy the actor to the worker actor system
            self.add_component(actor)
            actor.set_definition(nf_definition)

        for id, actor in self[Actor].items():
            for id2, actor2 in self[Actor].items():
                if actor.get_definition() in actor2.get_definition().get_children():
                    actor2.add_child(actor)

        actor: Actor

        def search_dic_by_key(dic, key):
            for k, v in dic.items():
                if k == key:
                    return v
                elif isinstance(v, dict):
                    item = search_dic_by_key(v, key)
                    if item is not None:
                        return item

        # create the necessary control states
        for i, nf_definition in enumerate(composed_nf.nf_definition_system):
            if nf_definition.is_top_level() and nf_definition.type.category is not NFTypeCategory.SYSTEM:
                control_state = ControlState()
                control_state.name = str(nf_definition.type.name) + "#" + str(nf_definition.name)
                control_state.nf_definition_id = nf_definition.name
                parameter_dic = search_dic_by_key(worker_dict, control_state.name)
                if parameter_dic is None:
                    parameter_dic = {}
                self.add_component(control_state)
                control_state.parameter_dict = copy(parameter_dic)
                for key, next_actor_id in control_state.parameter_dict.items():
                    # if value is a dict
                    if isinstance(next_actor_id, dict):
                        if "traffic_class" in key:
                            continue
                        else:
                            del control_state.parameter_dict[key]
                            break
                control_state.type = str(nf_definition.type.name)

                for id, actor in self[Actor].items():
                    if actor.get_definition() == nf_definition:
                        actor.add_component(control_state)

                children_nf_definition = nf_definition.get_children()
                control_state.set_attribute(
                    {"associated_nf_definition_list": children_nf_definition + [nf_definition]}
                )
                for transition in composed_nf.nf_transition_system:
                    initial_nf = transition.initial_nf
                    # if the initial nf is not the children of the actor, skip
                    # configure the control state so that it contains the routing information
                    # todo: change this to actor
                    if initial_nf not in children_nf_definition + [nf_definition]:
                        continue
                    intial_nf_type = initial_nf.type
                    final_nf = transition.final_nf
                    next_actor_id = self[NFDefinition].get_id(final_nf)
                    event = transition.event
                    key_name = "{}.{}".format(intial_nf_type.name, event.name)
                    control_state.transition_configuration[key_name] = next_actor_id

        for id, actor in self[Actor].items():
            if type(actor) == SystemActor:
                actor.add_component(self.worker_control_state)

        # add the control state to the actor
        for id, control_state in self[ControlState].items():
            # if control state has attribute nf_definition_list, it means it is not a system actor
            # system actor does not have nf_definition_list and has added its control state
            if control_state.is_contain_attribute("associated_nf_definition_list"):
                nf_definition_list = control_state.get_attribute("associated_nf_definition_list")
                for id, actor in self[Actor].items():
                    if actor.get_definition() in nf_definition_list:
                        actor.add_component(control_state)
                        actor.add_control_state(control_state)

        # if there is stateful network function
        exist_stateful_match_actor_n = 0
        exist_stateful_action_actor_n = 0
        for id, actor in self[Actor].items():
            if type(actor) == StatefulMatchActor and actor.get_definition().is_top_level():
                exist_stateful_match_actor_n += 1
            if type(actor) == StatefulActionActor and actor.get_definition().is_top_level():
                exist_stateful_action_actor_n += 1
        try:
            assert exist_stateful_match_actor_n == exist_stateful_action_actor_n
            if exist_stateful_match_actor_n > 0:
                self.setup_datablocks()
        except AssertionError:
            assert exist_stateful_match_actor_n == 2 and exist_stateful_action_actor_n == 1  # multi-level classification illustrated using upf
            self.setup_datablocks_multi_level_classification()
        self.setup_entry_event(composed_nf.nf_transition_system)

        # optimization process
        if len(self.optimization_options) > 0:
            if "data_packing" in self.optimization_options:
                to_merge_datablocks = []
                merged_block_size = 0
                offset_is_set = False
                for datablock_id in self[DataBlock]:
                    temp_datablock: DataBlock = self[DataBlock][datablock_id]
                    if temp_datablock.type == "per_flow_state":
                        print("size of datablock {} is {}".format(datablock_id, temp_datablock.size))
                        to_merge_datablocks.append(temp_datablock)
                        merged_block_size += temp_datablock.size
                        if not offset_is_set:
                            offset = temp_datablock.size
                            offset_is_set = True
                # change the size of the first datablock in to_merge_datablocks to the merged_block_size
                # and associate the actors that previously associate with the other datablocks to the first datablock
                if len(to_merge_datablocks) > 1:
                    to_merge_datablocks[0].size = merged_block_size
                    merged_datablock_id = to_merge_datablocks[0].datablock_id
                    for actor_id in self[Actor]:
                        actor = self[Actor][actor_id]
                        for temp_datablock in to_merge_datablocks[1:]:
                            temp_datablock_id = temp_datablock.datablock_id
                            if temp_datablock_id == actor.datablock_id:
                                actor.datablock_id = merged_datablock_id
                                original_offset = actor.datablock_offset
                                actor.datablock_offset = offset
                                offset += temp_datablock.size
                                # print("change datablock id of actor {} from {} to {}".format(actor_id, temp_datablock_id, merged_datablock_id))
                                print("change datablock offset of actor {} from {} to {}".format(actor_id,
                                                                                                 original_offset,
                                                                                                 actor.datablock_offset))
                                self[DataBlock].remove_component(temp_datablock)

            if "redundant_match_removal" in self.optimization_options:
                stateful_match_actor_list = []
                for actor_id in self[Actor]:
                    actor = self[Actor][actor_id]
                    if type(actor) == StatefulMatchActor:
                        stateful_match_actor_list.append(actor)

                stateful_action_actor_list = []
                for actor_id in self[Actor]:
                    actor = self[Actor][actor_id]
                    if type(actor) == StatefulActionActor:
                        stateful_action_actor_list.append(actor)

                # change the transition of the stateful action actor to the next stateful action actor
                for stateful_action_actor in stateful_action_actor_list:
                    # get its control state
                    control_state = stateful_action_actor.control_state
                    # get the transition configuration
                    transition_configuration = control_state.transition_configuration
                    for key, next_actor_id in transition_configuration.items():
                        # value is the actor id of the next actor
                        actor_corresponding_to_value = self[Actor][next_actor_id]
                        if type(actor_corresponding_to_value) == StatefulMatchActor:
                            # get the control state of the next stateful match actor
                            match_actor_control_state = actor_corresponding_to_value.control_state
                            # get the transition configuration of the next control state
                            match_actor_transition_configuration = match_actor_control_state.transition_configuration
                            for match_actor_key, match_actor_next_actor_id in match_actor_transition_configuration.items():
                                next_actor_of_match_actor = self[Actor][match_actor_next_actor_id]
                                if type(next_actor_of_match_actor) == StatefulActionActor:
                                    transition_configuration[key] = match_actor_next_actor_id
                                    print("change transition configuration of actor {} from {} to {}".format(
                                        self[Actor].get_id(stateful_action_actor), next_actor_id,
                                        match_actor_next_actor_id))
                                    break

                # for stateful_match_actor in stateful_match_actor_list[1:]:
                #     stateful_match_actor_control_state = stateful_match_actor.control_state
                #     self[ControlState].remove_component(stateful_match_actor_control_state)  # remove the control state of the stateful match actor, as it is redundant
                #     self[Actor].remove_component(stateful_match_actor)  # remove the stateful match actor, as it is redundant

                # remove the data block of the stateful match actor except the first one
                datablock_list = []
                for datablock_id in self[DataBlock]:
                    datablock = self[DataBlock][datablock_id]
                    if datablock.type != "per_flow_state":  # if it is not the per flow state, then it is the stateful match actor
                        datablock_list.append(datablock)

                for datablock in datablock_list[1:]:
                    self[DataBlock].remove_component(datablock)

    def setup_datablocks(self):
        # add two data blocks * num
        # one for the stateful match actor
        # one for the per-flow state
        # must follow the pattern:
        # stateful match actor -> stateful action actor -> stateful match actor -> stateful action actor -> ...
        actor: Actor
        state = 0
        datablock_id = 0
        for actor_id in self[Actor]:
            actor = self[Actor][actor_id]
            if actor.is_top_level():
                if state == 0:
                    if actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH or actor[NFDefinition][
                        0].type.category == NFTypeCategory.STATEFUL_NF:
                        assert actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH
                        state = 1
                        temp_datablock = DataBlock()
                        temp_datablock.datablock_id = datablock_id
                        actor.datablock_id = datablock_id
                        temp_datablock.control_state = actor.control_state
                        temp_datablock.num_flow_differentiated_per_entry = temp_datablock.control_state.get_entry_num()  #
                        # the datablock size depends on the configuration of the control state
                        temp_datablock.bucket_num = 1
                        temp_datablock.total_entry_num = 0
                        temp_datablock.size = temp_datablock.control_state.get_entry_size()
                        temp_datablock.type = actor[NFDefinition][0].type.name
                        self[DataBlock].add_component(temp_datablock)

                        # for every child actor, set the datablock id to be the same as the parent actor
                        for child_actor in actor.children:
                            assert isinstance(child_actor, Actor)
                            child_actor.datablock_id = datablock_id

                        datablock_id += 1
                        continue
                if state == 1:
                    if actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH or actor[NFDefinition][
                        0].type.category == NFTypeCategory.STATEFUL_NF:
                        assert actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_NF
                        actor.datablock_id = datablock_id
                        previous_datablock = self[DataBlock][datablock_id - 1]
                        temp_datablock = DataBlock()
                        temp_datablock.datablock_id = datablock_id
                        temp_datablock.control_state = actor.control_state
                        temp_datablock.total_entry_num = previous_datablock.total_entry_num + previous_datablock.num_flow_differentiated_per_entry
                        temp_datablock.num_flow_differentiated_per_entry = 0  # this value is not used
                        temp_datablock.type = "per_flow_state"
                        temp_datablock.size = temp_datablock.control_state.get_entry_size()
                        self[DataBlock].add_component(temp_datablock)
                        # for every child actor, set the datablock id to be the same as the parent actor
                        for child_actor in actor.children:
                            assert isinstance(child_actor, Actor)
                            child_actor.datablock_id = datablock_id
                        state = 0
                        datablock_id += 1
                        continue

    def setup_datablocks_multi_level_classification(self):
        # quick and dirty implementation of the data-block configuration of multi-level classification
        # three states: 0, 1, 2
        # 0: cuckoo_hash
        # 1: multi-dimensional tree
        # 2: encapsulation
        actor: Actor
        state = 0
        datablock_id = 0
        for actor_id in self[Actor]:
            actor = self[Actor][actor_id]
            if actor.is_top_level():
                if state == 0:
                    if actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH or actor[NFDefinition][
                        0].type.category == NFTypeCategory.STATEFUL_NF:
                        assert actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH
                        state = 1
                        temp_datablock = DataBlock()
                        temp_datablock.datablock_id = datablock_id
                        actor.datablock_id = datablock_id
                        temp_datablock.control_state = actor.control_state
                        temp_datablock.num_flow_differentiated_per_entry = temp_datablock.control_state.get_entry_num()
                        # the datablock size depends on the configuration of the control state
                        temp_datablock.bucket_num = 1
                        temp_datablock.total_entry_num = 0
                        temp_datablock.size = temp_datablock.control_state.get_entry_size()
                        temp_datablock.type = actor[NFDefinition][0].type.name
                        self[DataBlock].add_component(temp_datablock)

                        # for every child actor, set the datablock id to be the same as the parent actor
                        for child_actor in actor.children:
                            assert isinstance(child_actor, Actor)
                            child_actor.datablock_id = datablock_id

                        datablock_id += 1
                        continue
                if state == 1:
                    if actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH or actor[NFDefinition][
                        0].type.category == NFTypeCategory.STATEFUL_NF:
                        assert actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH
                        actor.datablock_id = datablock_id
                        previous_datablock = self[DataBlock][datablock_id - 1]
                        temp_datablock = DataBlock()
                        temp_datablock.datablock_id = datablock_id
                        temp_datablock.control_state = actor.control_state
                        temp_datablock.total_entry_num = previous_datablock.total_entry_num + previous_datablock.num_flow_differentiated_per_entry
                        temp_datablock.num_flow_differentiated_per_entry = temp_datablock.control_state.get_entry_num()  #
                        temp_datablock.type = actor[NFDefinition][0].type.name
                        temp_datablock.size = temp_datablock.control_state.get_entry_size()
                        self[DataBlock].add_component(temp_datablock)
                        # for every child actor, set the datablock id to be the same as the parent actor
                        for child_actor in actor.children:
                            assert isinstance(child_actor, Actor)
                            child_actor.datablock_id = datablock_id
                        state = 2
                        datablock_id += 1
                        continue
                if state == 2:
                    if actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH or actor[NFDefinition][
                        0].type.category == NFTypeCategory.STATEFUL_NF:
                        assert actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_NF
                        actor.datablock_id = datablock_id
                        previous_datablock = self[DataBlock][datablock_id - 1]
                        temp_datablock = DataBlock()
                        temp_datablock.datablock_id = datablock_id
                        temp_datablock.control_state = actor.control_state
                        temp_datablock.total_entry_num = previous_datablock.total_entry_num + previous_datablock.num_flow_differentiated_per_entry
                        temp_datablock.num_flow_differentiated_per_entry = 0  # this value is not used
                        temp_datablock.type = "per_flow_state"
                        temp_datablock.size = 512  # fixed for now
                        self[DataBlock].add_component(temp_datablock)
                        # for every child actor, set the datablock id to be the same as the parent actor
                        for child_actor in actor.children:
                            assert isinstance(child_actor, Actor)
                            child_actor.datablock_id = datablock_id
                        state = 0
                        datablock_id += 1
                        continue

    def setup_entry_event(self, nf_transition_system):
        # look at the transition system in nf_definition_factory
        for nf_transition in nf_transition_system:
            nf_1 = nf_transition.initial_nf.get_ancestor()
            nf_2 = nf_transition.final_nf.get_ancestor()
            if nf_1 == nf_2:
                continue

            temp_actor: Actor | None = None
            # search the actor with nf_transition.final_nf as its orchestration
            found = False
            for actor_id in self[Actor]:
                temp_actor = self[Actor][actor_id]
                if temp_actor[NFDefinition][0] == nf_transition.final_nf:
                    found = True
                    break
            assert found
            if temp_actor.entry_event != EntryEvent.DO_NOTHING:
                continue  # already set
            if temp_actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_MATCH:
                temp_actor.entry_event = EntryEvent.LOAD_CLASSIFIER_STATE
            elif temp_actor[NFDefinition][0].type.category == NFTypeCategory.STATEFUL_NF:
                temp_actor.entry_event = EntryEvent.LOAD_PERFLOW_STATE
            elif temp_actor[NFDefinition][0].type.category == NFTypeCategory.SYSTEM:
                temp_actor.entry_event = EntryEvent.LOAD_CONTROL_STATE
            elif temp_actor[NFDefinition][0].type.category == NFTypeCategory.STATELESS_NF:
                temp_actor.entry_event = EntryEvent.LOAD_CONTROL_STATE
            else:
                raise Exception("Unknown NF type")

    def to_dict(self):
        temp_dict = {}
        temp_dict |= self[Actor].to_dict()
        temp_dict |= self[ControlState].to_dict()
        temp_dict |= self[NFDefinition].to_dict()
        temp_dict |= self[NFType].to_dict()
        temp_dict |= self[DataBlock].to_dict()
        # self.composed_nf = worker_setting_series["composed_nf"]
        # self.worker_prefetch_perflow = worker_setting_series["worker_prefetch_perflow"]
        # self.worker_tx_mode = worker_setting_series["worker_tx_mode"]
        # self.worker_core_id = worker_setting_series["core_id"]
        # self.worker_port_id = 0
        # self.worker_queue_id = worker_setting_series["queue_id"]
        # self.worker_num_interleaved = worker_setting_series["num_interleaved"]
        # self.data_packing_optimization = worker_setting_series["data_packing_optimization"]
        # self.per_flow_state_size = worker_setting_series["per_flow_state_size"]
        # self.sub_flow_state_size = worker_setting_series["sub_flow_state_size"]
        # self.num_per_flow_state = worker_setting_series["num_per_flow_state"]
        # self.num_sub_flow_state = worker_setting_series["num_sub_flow_state"]
        # self.initial_actor = 0
        temp_dict |= {
            "WorkerParameters": {
                # "num_per_flow_state": self.num_per_flow_state,
                # "num_sub_flow_state": self.num_sub_flow_state,
                # "per_flow_state_size": self.per_flow_state_size,
                # "sub_flow_state_size": self.sub_flow_state_size,
                # "data_packing_optimization": self.data_packing_optimization,
                "worker_num_interleaved": self.worker_num_interleaved,
                "worker_queue_id": self.worker_queue_id,
                "worker_rx_port": self.worker_rx_port,
                "worker_tx_port": self.worker_tx_port,
                "worker_core_id": self.worker_core_id,
                "worker_tx_mode": self.worker_tx_mode,
                "worker_destination_instance": self.worker_destination_instance,
                # "worker_prefetch_perflow": self.worker_prefetch_perflow,
                "initial_actor": self.initial_actor,
            }
        }
        return temp_dict

    def get_control_states_configuration(self):
        return self.collect_on_type(ControlState)

    def get_classifiers_configuration(self):
        return self.collect_on_type(StatefulMatchActorState)

    def get_actor_control_state_correspondence_configuration(self):
        return self.collect_on_type(ControlState)

    def get_actor_stateful_match_correspondence(self):
        return self.collect_on_type(StatefulMatchActorState)

    def get_actor_table(self):
        return self.collect_on_type(Actor)

    def get_actor_table_configuration(self):
        return self.collect_on_type(Actor)

    def __str__(self):
        return "Worker"

    def setup_classifier_initialization_info(self):
        pass


class PM_Model(RecursiveStructure):
    def __init__(self):
        super().__init__()
        self.core_list = [i for i in range(2, 34, 2)]


class RuntimeSetting(ManagerSystem):
    # generate a set of worker configurations
    def __init__(self, manager, configuration_dict: dict, **kwargs):
        assert type(configuration_dict) == dict
        super().__init__(manager=manager)
        self.manage_type(WorkerSetting)
        # machine model
        self.available_core_list = [i for i in range(2, 48, 2)]
        self.is_president = False
        self.machine_ip = configuration_dict["machine_ip"]
        self.worker_num = int(configuration_dict["worker_num"])
        self.optimization_options = kwargs["optimization_options"]
        for i in range(0, self.worker_num):
            worker_name = "worker#{}".format(i)
            worker_config_dict = configuration_dict[worker_name]
            # allocate core and queue for each worker
            worker_config_dict["core_id"] = self.available_core_list.pop(0)
            worker_config_dict["queue_id"] = i
            worker_setting = WorkerSetting(self, worker_config_dict, **kwargs)
            self.add_component(worker_setting)

    def to_dict(self):
        temp_dict = {}
        temp_dict |= self[WorkerSetting].to_dict()
        temp_dict["ip"] = self.machine_ip
        return temp_dict

    def extract_configuration_series(self, configuration_series, keys):
        # for each key, rename the key to remove the machine name
        # return a new series with the new keys
        copied_configuration_series = Series(dtype='object')
        for key in keys:
            split_key = key.split("$")
            new_key = "$".join(split_key[1:])
            copied_configuration_series[new_key] = configuration_series[key]
        return copied_configuration_series

    def get_keys_and_machine_name(self, configuration_series):
        keys = configuration_series.keys()
        # machine name is in every key
        # every key is in the form of "machine_name$...$..."
        # so we can split the key by "$"
        machine_name = keys[0].split("$")[0]
        return keys, machine_name


class DistributedRuntimeSetting(ManagerSystem):
    # generate a set of worker configurations
    def __init__(self, manager, configuration_dict, **kwargs):
        super().__init__(manager=manager)
        assert type(configuration_dict) == dict
        self.is_president = False
        assert "machine_num" in configuration_dict.keys()
        self.machine_num = int(configuration_dict["machine_num"])
        self.optimization_options = configuration_dict["optimization_options"].copy()
        self.manage_type(RuntimeSetting)
        for i in range(0, self.machine_num):
            machine_name = "machine#{}".format(i)
            machine_dic = configuration_dict[machine_name]
            temp_runtime_setting = RuntimeSetting(self, machine_dic, optimization_options=self.optimization_options,
                                                  **kwargs)
            self.add_component(temp_runtime_setting)

    def to_dict(self):
        temp_dict = {}
        temp_dict |= self[RuntimeSetting].to_dict()
        temp_dict["optimization_options"] = self.optimization_options
        return temp_dict

    def generate_asymmetric_deployment(self):
        print_cs("not implemented yet")
        pass

    def generate_traffic_generator(self):
        pass


class ExperimentSetup(ManagerSystem):
    def __init__(self, configuration_dict_list: list[dict], **kwargs):
        super().__init__(**kwargs)
        self.is_president = True
        self.manage_type(DistributedRuntimeSetting)
        for configuration_dict in configuration_dict_list:
            temp_runtime_setting = DistributedRuntimeSetting(self, configuration_dict, **kwargs)
            self.add_component(temp_runtime_setting)

    def to_dict(self):
        return self[DistributedRuntimeSetting].to_dict()


def scale_worker(configuration_dict_list, scaling_worker):
    for configuration_dict in configuration_dict_list:
        machine_num = int(configuration_dict["machine_num"])
        for i in range(0, machine_num):
            machine_name = "machine#{}".format(i)
            machine_dic = configuration_dict[machine_name]
            worker_num = int(machine_dic["worker_num"])
            machine_dic["worker_num"] = worker_num * scaling_worker
            for j in range(worker_num, worker_num * scaling_worker):
                worker_name = "worker#{}".format(j)
                corresponding_worker_name = "worker#{}".format(j % worker_num)
                machine_dic[worker_name] = deepcopy(machine_dic[corresponding_worker_name])
    return configuration_dict_list


def get_exp_setup(exp_name):
    '''

    :param exp_name:
    based on exp name, get the configuration dict list based on the admin input
    :return:
    '''
    configuration_dict_list, scaling_worker, optimization_options = get_configuration_dict_list(exp_name)
    configuration_dict_list_list = []
    # copy the configuration dict list with len(scaling_worker) copies
    assert scaling_worker is not None
    scaling_worker: list[int]
    for i in range(0, len(scaling_worker)):
        temp_configuration_dict_list = deepcopy(configuration_dict_list)
        temp_configuration_dict_list = scale_worker(temp_configuration_dict_list, scaling_worker[i])
        configuration_dict_list_list.append(temp_configuration_dict_list)
    # flatten the list
    configuration_dict_list = [item for sublist in configuration_dict_list_list for item in sublist]

    configuration_dict_list_list = []
    if optimization_options is None:
        optimization_options = [[]]
    optimization_options: list[list]
    for i in range(0, len(optimization_options)):
        temp_configuration_dict_list = deepcopy(configuration_dict_list)
        for temp_configuration_dict in temp_configuration_dict_list:
            temp_configuration_dict["optimization_options"] = optimization_options[i]
        configuration_dict_list_list.append(temp_configuration_dict_list)
    # flatten the list
    configuration_dict_list = [item for sublist in configuration_dict_list_list for item in sublist]

    # remove the duplicated configurations
    def equal_dict(dict1, dict2):
        return dict1 == dict2

    # remove the duplicated configurations
    for i in range(0, len(configuration_dict_list)):
        for j in range(i + 1, len(configuration_dict_list)):
            if equal_dict(configuration_dict_list[i], configuration_dict_list[j]):
                configuration_dict_list[j] = None
    configuration_dict_list = [item for item in configuration_dict_list if item is not None]

    exp_setup = ExperimentSetup(configuration_dict_list)
    result = exp_setup.to_dict()
    folder_path = "exp"
    current_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_path, folder_path)
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    # save the result as a yaml file
    with open("{}/{}.yaml".format(file_path, exp_name), "w") as f:
        yaml.dump(result, f)
    return result


print_cs = make_print_depth(4)

if __name__ == "__main__":
    '''
    :arg exp_name: the name of the experiment
    python3 resource_orchestrator.py exp_name=traffic_generator_testing
    '''
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("exp_name", type=str, nargs='?', default="traffic_generator_testing")
    args = parser.parse_args()
    exp_name = args.exp_name
    result_dic = get_exp_setup(exp_name)
