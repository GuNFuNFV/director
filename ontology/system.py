from typing import Generic, TypeVar
# get the version of python
import sys

from utility import type_to_string
from ontology.recursivesystem import RecursiveStructure

T = TypeVar('T', bound=RecursiveStructure)  # Must be a RecursiveStructure
version = sys.version_info
# if version < 3.7
# then raise an error

if version < (3, 11):
    raise Exception("Python version must be 3.9 or greater")


class System(RecursiveStructure):
    id = 0
    root_system_list: list["System"] = []  # the source of all systems

    def __init__(self):
        super().__init__()
        System.root_system_list.append(self)
        self.system_id = System.id
        self.system_name = str(self.id)
        System.id += 1
        # self.duties = {
        # }  # task name to handler function
        # self.routing = {
        # }  # task name to parent

    # virtual method
    def add_component(self, component: RecursiveStructure) -> RecursiveStructure:
        return component


class ManagerSystem(System):
    def __init__(self, manager:"ManagerSystem" = None):
        super().__init__()
        self.manager_system_set: set["ManagerSystem"] = set()  # the system that this system manages
        self.managed_type: dict[
            type[RecursiveStructure], HomoSystem] = {}  # the type of the system that this system manages
        self.to_dict_list = []
        if manager is not None:
            self.manager_system_set.add(manager)
            manager.add_component(self)
        self.is_president = False # president is the top level system

    def manage_type(self, managed_type: type[RecursiveStructure]):
        self.managed_type[managed_type] = HomoSystem[managed_type](managed_type, type(self))
        # print("type {} is managed by {}".format(managed_type, type(self)))
        self.root_system_list.remove(self.managed_type[managed_type])

    def add_component(self, component: RecursiveStructure):
        # get the type of system
        component_type = type(component)
        if component_type in self.managed_type:
            # if the component already in the system
            if component in self.managed_type[component_type]:
                return
        for manager in self.manager_system_set:
            manager.add_component(component)

        for key in self.managed_type:
            if issubclass(component_type, key):
                self.managed_type[key].add_component(component)

        # if the component is a subclass of manager system
        # set its manager to self
        if issubclass(component_type, ManagerSystem):
            component: ManagerSystem
            component.manager_system_set.add(self)

        # check whether managed_type is a parent of component_type
        # add the component to the managed_type
        for key in self.managed_type:
            if issubclass(component_type, key):
                self.managed_type[key].add_component(component)

        # if the component is a system
        # remove it from the root_system_list
        if type(component) is System:
            component: System
            if component in System.root_system_list:
                System.root_system_list.remove(component)

        # if it has children, add the component to its children
        if len(component.children) > 0:
            for child in component.children:
                self.add_component(child)
        return

    def print_system(self, temp_type: type[RecursiveStructure]):
        # get all the homosystems of this type
        if temp_type in self.managed_type:
            print(self.managed_type[temp_type])

    def iter_on_type(self, temp_type: type[RecursiveStructure]):
        if temp_type in self.managed_type:
            return iter(self.managed_type[temp_type])

    def collect_on_type(self, type: type[RecursiveStructure]):
        if type in self.managed_type:
            return self.managed_type[type].collect()

    def __iter__(self):
        return iter(self.managed_type)

    def items(self):
        return self.managed_type.items()

    def __getitem__(self, temp_type: type[RecursiveStructure]):
        return self.managed_type[temp_type]

    def to_dict(self):
        if self.to_dict_list is []:
            return {}
        temp_dict = {}
        for key in self.to_dict_list:
            key_string = type_to_string(key)
            temp_dict[key_string] = self.managed_type[key].to_dict()

        return temp_dict

    def dump(self):
        # if self.name is None:
        #     self_index = self.manager.managed_type[type(self)].index(self)
        #     self.name = self.manager.name + "." + type_to_string(type(self)) + "_" + str(self_index)
        string = "ManagerSystem: system_id {}, name {}, {}\n".format(self.system_id, self.system_name, self.name)
        if self.__str__() == "None":
            print("None")
        for key, value in self.managed_type.items():
            string += "{}\n".format(type_to_string(key))
            temp_str = ""
            # check the type of the value
            if issubclass(type(value), System):
                temp_str += value.dump()
            else:
                temp_str += str(value)
            # for every line in the result
            for line in temp_str.splitlines():
                string += "\t{}\n".format(line)
        return string


class HomoSystem(System, Generic[T]):
    def __init__(self, component_type, manager_type):
        super().__init__()
        self.local_id: int = 0  # the id of the component in this homo system
        self.id_to_component: dict[int, T] = {}  # mapping from local id to component
        self.component_type = component_type
        self.manager_type = manager_type
        self.name = "(HomoSystem) sys_id:{} type:{}".format(self.system_id, type_to_string(component_type))

    def __contains__(self, item):
        return item in self.id_to_component.values()

    def __len__(self):
        return len(self.id_to_component)

    def to_dict(self):
        temp_dict = {}
        temp_dict[type_to_string(self.component_type)] = {}
        for key, value in self.id_to_component.items():
            # if value has to_dict method
            if hasattr(value, "to_dict"):
                temp_dict[type_to_string(self.component_type)][key] = value.to_dict()
            else:
                temp_dict[type_to_string(self.component_type)][key] = value
        return temp_dict

    def add_component(self, component: T) -> T:
        # check whether the component in the values of the dictionary
        if component in self.id_to_component.values():
            # print("(added) component:{}, component_type:{}, manager_type:{} local_id:{}".format(str(component),
            #                                                                             self.component_type,
            #                                                                             self.manager_type,
            #                                                                             self.get_id(component)))
            component.manager_type_component_type_to_id[self.manager_type][type_to_string(self.component_type)] = self.get_id(component)
            return component
        # if type is a derived type of the type system or the type is a system
        if issubclass(type(component), System):
            component: System
            if component in System.root_system_list:
                System.root_system_list.remove(component)
        self.id_to_component[self.local_id] = component
        component.manager_type_component_type_to_id[self.manager_type] = {}
        component.manager_type_component_type_to_id[self.manager_type][type_to_string(self.component_type)] = self.get_id(component)
        # print("component:{}, component_type:{}, manager_type:{} local_id:{}".format(str(component), self.component_type,
        #                                                                             self.manager_type,
        #                                                                             self.get_id(component)))
        self.local_id += 1
        return component

    def remove_component(self, component: T):
        if component in self.id_to_component.values():
            self.id_to_component.pop(self.get_id(component))
            return True
        return False

    def get_id(self, component: T) -> int:
        for key in self.id_to_component:
            if self.id_to_component[key] == component:
                return key
        raise Exception("Component not found")

    def __getitem__(self, key) -> T:
        if type(key) == int:
            return self.id_to_component[key]
        return None

    def __str__(self):
        return str(self.name)

    def collect(self):
        return self.id_to_component

    def __iter__(self):
        return iter(self.id_to_component)

    def items(self) -> dict[int, T].items:
        return self.id_to_component.items()

    def dump(self):
        if len(self.id_to_component) == 0:
            return "None"
        temp_str = "{}\n".format(self.name)
        for key in self.id_to_component:
            temp_str += "{}:\n".format(key)
            temp_result = ""
            if issubclass(type(self.id_to_component[key]), System):
                temp_result = self.id_to_component[key].dump()
            else:
                temp_result = str(self.id_to_component[key])
            # for every line in the result
            for line in temp_result.splitlines():
                temp_str += "\t{}\n".format(line)
        return temp_str

    def index(self, item):
        return list(self.id_to_component.values()).index(item)
