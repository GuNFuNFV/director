from typing import Tuple, List, Dict, Iterator

from utility import type_to_string


class Vector:
    def __init__(self, tuple: Tuple[str, ...] = None):
        self.data = tuple
        self.dimension = len(tuple)

    def __hash__(self):
        return hash(self.data)

    def __eq__(self, other):
        return self.data == other.data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()


class RecursiveStructure:
    def __init__(self):
        self.children = []
        self.parent = []
        self.name = None
        self.recursive_system_list = []  # list of recursive systems that this structure belongs to
        self.manager_type_component_type_to_id = dict() # type to id # when it is used in a sytem, it can be contained by multiple systems; the id in each system is different
        # the manager type not translated to string
        # the component type translated to string
        self.name_to_attribute = {} # provide a serverless way to access attributes
        for attribute in self.__dict__:
            self.name_to_attribute[attribute] = attribute

    def get_id(self, manager_type, component_type):
        return self.manager_type_component_type_to_id[manager_type][type_to_string(component_type)]
    def is_contain_attribute(self, name: str):
        return name in self.name_to_attribute
    def set_attribute(self, dict: Dict):
        for key, value in dict.items():
            if key in self.name_to_attribute:
                setattr(self, self.name_to_attribute[key], value)
            else:
                # add new attribute
                self.name_to_attribute[key] = key
                setattr(self, key, value)

    def get_attribute(self, name: str):
        if name in self.name_to_attribute:
            return getattr(self, self.name_to_attribute[name])
        else:
            return None

    def set_name(self, name):
        self.name = name

    def copy(self):
        return self.__class__()

    def add_child(self, child):
        # add child if not already in the list
        if child not in self.children:
            self.children.append(child)
        # set parent
        if self not in child.parent:
            child.parent.append(self)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
        if self in child.parent:
            child.parent.remove(self)

    def get_ancestor(self) -> "RecursiveStructure":
        assert len(self.parent) <= 1
        if len(self.parent) == 0:
            return self
        else:
            return self.parent[0].get_ancestor()

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return self.__str__()


from typing import Generic, TypeVar

T = TypeVar('T')


class RecursiveSystem(Generic[T]):
    # can look up every recursive structure by any means
    def __init__(self):
        self.table = []


    def __len__(self):
        return len(self.table)

    # support [] operator
    def __getitem__(self, key) -> T:
        if type(key) == int:
            return self.table[key]
        for entry in self.table:
            if entry.name == key:
                return entry
        return None

    def is_or_is_child(self, parent: RecursiveStructure, child: RecursiveStructure):
        if parent == child:
            return True
        for c in parent.children:
            if self.is_or_is_child(c, child):
                return True
        return False

    def is_or_is_child_of_one_item_in_list(self, parent_list: List[RecursiveStructure], child: RecursiveStructure):
        for parent in parent_list:
            if self.is_or_is_child(parent, child):
                return True
        return False

    def is_or_is_father_of_one_item_in_list(self, child_list: List[RecursiveStructure], parent: RecursiveStructure):
        for child in child_list:
            if self.is_or_is_child(parent, child):
                return True
        return False

    def add_entry_with_name(self, name: str):
        entry = RecursiveStructure()
        entry.set_name(name)
        self.add_entry(entry)
        entry.recursive_system_list.append(self)

    def lookup_and_add_if_not_exist(self, name: str = None):
        entry = self[name]
        if entry is None:
            entry = RecursiveStructure()
            entry.set_name(name)
            self.add_entry(entry)
            entry.recursive_system_list.append(self)
        return entry

    def lookup(self, name: str = None):
        entry = self[name]
        return entry

    def index(self, entry: RecursiveStructure):
        return self.table.index(entry)

    # add entry to table
    def add_entry(self, entry: RecursiveStructure = None):
        # assert entry has a property name
        assert hasattr(entry, "name")
        if self[entry.name] != None:
            # print("entry {} already exists".format(entry.name))
            return
        if entry.name is None:
            raise Exception("entry name is None")
        # check whether the name has the form of "x.y"
        # if so, it means that is has a parent
        if type(entry.name) == str:
            if "." in entry.name:
                # get the parent name
                parent_name = ".".join(entry.name.split(".")[:-1])
                # get the parent
                parent = self[parent_name]
                # if not found, add the parent
                if parent is None:
                    parent = entry.copy()  # copy the entry, check if it is a good idea
                    parent.set_name(parent_name)
                    parent.add_child(entry)
                    self.add_entry(parent)
                    parent.recursive_system_list.append(self)
        self.table.append(entry)
        entry.recursive_system_list.append(self)

    def visualize(self):
        import networkx as nx
        import matplotlib.pyplot as plt
        # directed graph
        G = nx.DiGraph()
        for entry in self.table:
            G.add_node(entry.name)
            for child in entry.children:
                G.add_edge(entry.name, child.name)
        # arrow from parent to child

        nx.draw(G, with_labels=True, arrows=True, node_size=50, font_size=10, arrowsize=30
                , node_color="skyblue", edge_color="black", linewidths=1, width=2)

        # figure size
        fig = plt.gcf()
        fig.set_size_inches(10, 6)
        plt.show()

    def __str__(self):
        return str(self.table)

    def __repr__(self):
        return self.__str__()

    def __iter__(self) -> Iterator[T]:
        return iter(self.table)

    def __contains__(self, item):
        return item in self.table
