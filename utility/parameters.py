from typing import List, Dict
from collections import OrderedDict


class Point:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.name}={self.value}"

    def __str__(self):
        return f"{self.name}={self.value}"


class Vector:
    def __init__(self, name, list_of_value):
        self._name = name
        self.list_of_parameters = [Point(name, value) for value in list_of_value]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        # if you change the name, change the name of all the parameters
        self._name = value
        for i in self.list_of_parameters:
            i.name = value
    def available_values(self):
        return [i.value for i in self.list_of_parameters]

    def __getitem__(self, item):
        return self.list_of_parameters[item]

    def return_parameter_name(self):
        return self.name

    def __repr__(self):
        return f"{self.name}={self.available_values()}"

    def __str__(self):
        return f"{self.name}={self.available_values()}"

    def sub_vector(self, value_list: str | int | List[str | int]):
        assert type(value_list) == str or type(value_list) == int or type(value_list) == list
        if type(value_list) == str or type(value_list) == int:
            value_list = [value_list]
        for value in value_list:
            try:
                assert value in self.available_values()
            except AssertionError:
                raise Exception(f"Value {value} is not available in {self.name}")
        return Vector(self.name, value_list)


class ConfigurationPoint:
    # a point in the configuration space
    # the "point" is a vector of key-value pairs
    # automatically convert int value if possible
    def __init__(self, configuration_dict=None):
        self.key_value: OrderedDict = OrderedDict()
        if configuration_dict is not None:
            for key, value in configuration_dict.items():
                self.key_value[key] = value
                # convert to int if possible
                try:
                    self.key_value[key] = int(value)
                except ValueError:
                    pass
        self.bundle_dimensions = []

    # define add operator
    def __add__(self, other):
        if isinstance(other, ConfigurationPoint):
            for i in other.key_value:
                self.key_value[i] = other.key_value[i]
            self.bundle_dimensions += other.bundle_dimensions
        else:
            raise Exception("Cannot add ConfigurationVector to a non-ConfigurationVector object")

        return self.copy()

    def __repr__(self):
        temp_str = "("
        for i in self.key_value:
            temp_str += f"{i}={self.key_value[i]}, "
        temp_str = temp_str[:-2]
        temp_str += ")"
        return temp_str

    def copy(self):
        tempParameterPoint = ConfigurationPoint(dict())
        tempParameterPoint.key_value = self.key_value.copy()
        return tempParameterPoint

    def __getitem__(self, item):
        return self.key_value[item]

    def __setitem__(self, key, value):
        self.key_value[key] = value

    # in operator
    def __contains__(self, item):
        return item in self.key_value

    def __iter__(self):
        return self.key_value.__iter__()

    def __len__(self):
        return len(self.key_value)

    def items(self):
        return self.key_value.items()

    def __list__(self):
        return list(self.key_value)


def cartesian_product_to_list_of_configuration_point(list_of_parameter_list: List[Vector]) -> list[ConfigurationPoint]:
    if len(list_of_parameter_list) == 0:
        raise Exception("Cannot create a parameter space with no parameters")
    if len(list_of_parameter_list) == 1:
        i: Point
        # for each item in the list, create a tuple
        return [ConfigurationPoint({i.name: i.value}) for i in list_of_parameter_list[0].list_of_parameters]
    else:
        p1: ConfigurationPoint
        p2: ConfigurationPoint
        temp_list: List[ConfigurationPoint] = []
        for p1 in cartesian_product_to_list_of_configuration_point(list_of_parameter_list[:-1]):
            for p2 in cartesian_product_to_list_of_configuration_point(list_of_parameter_list[-1:]):
                temp_list.append(p1 + p2)
        return temp_list


class ConfigurationVectorList:
    def __init__(self, list_of_configuration_vector: List[Vector], name):
        self.name = name
        self.list_of_configuration_vector = list_of_configuration_vector

    def __iter__(self):
        return self.list_of_configuration_vector.__iter__()


# create a product space
# zip the lists together
# and you can lookup each point by name
class ProductSpace:
    def __init__(self, list_of_vector: List[Vector], name=None | str):
        self.list_of_parameter_list = list_of_vector
        self.point_list_of_space: List[ConfigurationPoint] = []
        if len(list_of_vector) != 0:
            self.point_list_of_space = cartesian_product_to_list_of_configuration_point(list_of_vector)
        # get the name of the list
        self.dimensions = [i.name for i in list_of_vector]
        self.name = name

    def __len__(self):
        # how many points in the parameter space
        return len(self.point_list_of_space)
    def as_csv(self, filename):
        with open(filename, "w") as f:
            # get the header
            header = ""
            for parameterlist in self.list_of_parameter_list:
                header += f"{parameterlist.name}, "
            header = header[:-2]
            header += "\n"
            f.write(header)
            for parameter_point in self.point_list_of_space:
                temp_str = ""
                for parameter in parameter_point.key_value:
                    temp_str += f"{parameter_point.key_value[parameter]}, "
                temp_str = temp_str[:-2]
                if parameter_point != self.point_list_of_space[-1]:
                    temp_str += "\n"
                f.write(temp_str)
            # remove the last row

    def get_subspace(self, condition: Dict[str, List]) -> "ProductSpace":
        # select a point in the parameter space
        # use it to create a parameter space
        list_of_parameter_list = []
        for i in self.list_of_parameter_list:
            name = i.name
            if name not in condition:
                temp_list = []
                for j in i:
                    temp_list.append(j.value)
                list_of_parameter_list.append(Vector(name, temp_list))
                continue
            temp_list = []
            for j in i:
                if j.value in condition[name]:
                    temp_list.append(j.value)
            list_of_parameter_list.append(Vector(name, temp_list))
        return ProductSpace(list_of_parameter_list)

    def __str__(self):
        temp_str = "parameter space: "
        for i in self.dimensions:
            temp_str += f"{i}, "
        temp_str = temp_str[:-2]
        temp_str += "\n"
        for paramter_point in self.point_list_of_space:
            parameter_pointer_index = self.point_list_of_space.index(paramter_point)
            temp_str += f"{parameter_pointer_index}: "
            temp_str += f"{paramter_point}, "
            temp_str += "\n"
        temp_str += "parameter space end"
        return temp_str

    def __iter__(self):
        return self.point_list_of_space.__iter__()

    def index(self, item):
        return self.point_list_of_space.index(item)


def CartesianProduct_Space_Merge(space1: ProductSpace, space2: ProductSpace):
    list_of_list = space1.list_of_parameter_list + space2.list_of_parameter_list
    return ProductSpace(list_of_list)


def CartesianProduct_SpaceList_Merge(space_list: List[ProductSpace]):
    list_of_list = []
    for space in space_list:
        list_of_list += space.list_of_parameter_list
    return ProductSpace(list_of_list)
