import os
import subprocess

from orchestration import NFComposer
from orchestration.configuration_template.conjecture_data import Conjecture_Input, conjecture_data_loader
from orchestration.configuration_template.template_data import static_configuration_name_to_dict, \
    dynamic_configuration_name_to_func, configuration_name_to_dict, get_options_name_with_conjecture
from utility import ConfigurationPoint
import yaml
from utility.multiplex_input import Logger_Singleton, IO_Multiplexer, my_input


class option():
    '''
    name: the name of the option (e.g. machine_ip).

    Attributes:
        conjecture: 0 means no conjecture, 1 means conjecture, 2 means conjecture but the value is fixed
    '''

    def __init__(self, dic_option):
        self.name = dic_option["name"]
        # conjecture: 0 means no conjecture, 1 means conjecture, 2 means conjecture but the value is fixed
        self.conjecture = dic_option["conjecture"] if "conjecture" in dic_option else "0"
        self.available_values = dic_option["available_values"] if "available_values" in dic_option else None

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class static_configuration():
    def __init__(self, dict_static_configuration, instance_name=None):
        self.name = dict_static_configuration["name"]
        self.instance_num = dict_static_configuration["instance_num"]
        if instance_name is None:
            splitted = self.instance_num.split("_")
            self.instance_name = "_".join(splitted[:-1])


class configuration_node():
    # model the configuration process as a tree
    # each node is a configuration component
    # some node will trigger dynamic configuration
    # the result of the configuration is also a tree
    def __init__(self, config_dictionary, instance_id=None, conjecture_data_dic=None, **kwargs):
        assert "name" in config_dictionary
        assert "options" in config_dictionary
        name = config_dictionary["name"]
        options = config_dictionary["options"]
        static_configuration_list = config_dictionary[
            "static_configuration_list"] if "static_configuration_list" in config_dictionary else []
        dynamic_configuration_list = config_dictionary[
            "dynamic_configuration_list"] if "dynamic_configuration_list" in config_dictionary else []
        self.options_dict = {}
        self.name = name
        # print("{} instance instance: ".format(self.__class__.__name__), kwargs["instance_id"])
        if options == None:
            self.options = []
        else:
            self.options: list[option] = [option(i) for i in options]
        self.static_configuration_list: list[static_configuration] = [static_configuration(i) for i in
                                                                      static_configuration_list]
        # list of static configuration that must be configured
        self.dynamic_configuration_list = dynamic_configuration_list
        self.configuration_point_list = []  # list of configuration points
        self.instance_id = instance_id
        self.conjecture_data_dic = conjecture_data_dic
        #### must called last
        self.post_process(**kwargs)

    def post_process(self, **kwargs):
        assert hasattr(self, "options")
        assert hasattr(self, "static_configuration_list")
        inputted_options = []
        for option in self.options:
            if self.instance_id != None:
                name = option.name + "$" + str(self.instance_id)
            else:
                name = option.name
            prompt = name
            if option.conjecture == "0":
                value = ["%" + option.name + "%"]
            else:
                if option.name in self.conjecture_data_dic:
                    value = [self.conjecture_data_dic[option.name]]
                else:
                    while True:
                        try:
                            # need to input
                            io_multiplexer = IO_Multiplexer.get_instance()
                            if io_multiplexer.mode == "input" and "configuration_point" in kwargs:
                                print(kwargs["configuration_point"], inputted_options)
                            if option.available_values is not None:
                                prompt += " available value("
                                for i in range(len(option.available_values)):
                                    prompt += option.available_values[i]
                                    if i != len(option.available_values) - 1:
                                        prompt += ", "
                                prompt += ")"
                            prompt += ": "
                            value = my_input(prompt)
                            if option.available_values is not None:
                                assert all([i in option.available_values for i in value])
                            break
                        except Exception as e:
                            print(e)
                            print("Please input again")
            assert isinstance(value, list)
            self.options_dict[name] = value
            inputted_options.append((name, value))

        temp_list = []
        for key in self.options_dict:
            temp_list.append(self.options_dict[key])

        # take product of the options
        from itertools import product
        self.options_product = list(product(*temp_list))
        self.configuration_point_list = []
        for option in range(len(self.options_product)):
            temp_dict = {}
            for j in range(len(self.options_product[option])):
                if self.instance_id != None:
                    key = self.options[j].name + "$" + str(self.instance_id)
                else:
                    key = self.options[j].name
                value = self.options_product[option][j]
                temp_dict[key] = value
            temp_configuration_point = ConfigurationPoint(temp_dict)
            self.configuration_point_list.append(temp_configuration_point)

        if "configuration_point" in kwargs:
            for option in range(len(self.configuration_point_list)):
                self.configuration_point_list[option] = kwargs["configuration_point"] + self.configuration_point_list[
                    option]

        if len(self.static_configuration_list) > 0:
            temp_configuration_point_list = []
            for option in range(len(self.configuration_point_list)):
                configuration_point = self.configuration_point_list[option]
                configuration_point_list = self.add_static_configuration(configuration_point,
                                                                         instance_id=self.instance_id,
                                                                         conjecture_data_dic=self.conjecture_data_dic,
                                                                         )
                temp_configuration_point_list.extend(configuration_point_list)
            self.configuration_point_list = temp_configuration_point_list

        if len(self.dynamic_configuration_list) > 0:
            assert len(self.dynamic_configuration_list) == 1  # otherwise not implemented
            temp_configuration_point_list = []
            for option in range(len(self.configuration_point_list)):
                configuration_point = self.configuration_point_list[option]
                dynamic_configuration_generator = dynamic_configuration_name_to_func[self.dynamic_configuration_list[0]]
                dict_for_configuration_and_instance_name_list: list[tuple[dict, str]] = dynamic_configuration_generator(
                    configuration_point,
                    instance_id=self.instance_id)
                configuration_point_list = self.add_dynamic_configuration(configuration_point,
                                                                          dict_for_configuration_and_instance_name_list,
                                                                          instance_id=self.instance_id,
                                                                          conjecture_data_dic=self.conjecture_data_dic)
                temp_configuration_point_list.extend(configuration_point_list)
            self.configuration_point_list = temp_configuration_point_list

    def add_dynamic_configuration(self, configuration_point, dict_for_configuration_and_instance_name_list: list[
        tuple[dict, str]], instance_id, conjecture_data_dic, **kwargs):
        if len(dict_for_configuration_and_instance_name_list) == 0:
            return [configuration_point]
        else:
            nf_instance_id = dict_for_configuration_and_instance_name_list[0][1]
            new_instance_id = instance_id + "-" + str(nf_instance_id)
            config_dict = dict_for_configuration_and_instance_name_list[0][0]
            temp_configuration_node = configuration_node(config_dictionary=config_dict, instance_id=new_instance_id,
                                                         configuration_point=configuration_point,
                                                         conjecture_data_dic=conjecture_data_dic, **kwargs)
            temp_configuration_point_list = temp_configuration_node.get_configuration_point_list()
            configuration_point_list = []
            for temp_configuration_point in temp_configuration_point_list:
                configuration_point_list.extend(
                    self.add_dynamic_configuration(temp_configuration_point,
                                                   dict_for_configuration_and_instance_name_list[1:],
                                                   instance_id=new_instance_id,
                                                   conjecture_data_dic=self.conjecture_data_dic, **kwargs))
            return configuration_point_list

    def add_instance(self, configuration_point: ConfigurationPoint, static_configuration_id, local_instance_id=0,
                     instance_id=None, conjecture_data_dic=None, **kwargs):
        # get the number of instances required by the static configuration
        instance_num_option = self.static_configuration_list[static_configuration_id].instance_num
        instance_name = self.static_configuration_list[static_configuration_id].instance_name
        try:
            if instance_id != None:
                instance_num_option = instance_num_option + "$" + str(self.instance_id)
            else:
                instance_num_option = instance_num_option
            instance_num = configuration_point[instance_num_option]
        except KeyError:
            print("Please input the number of instances for the static configuration: ")
            exit(1)
        if local_instance_id == instance_num:
            return [configuration_point]  # no more static configuration to add
        # get the initialization function
        configuration_class_name = self.static_configuration_list[static_configuration_id].name
        if instance_id != None:
            temp_instance_id = str(instance_id) + "-" + str(instance_name) + "#" + str(local_instance_id)
        else:
            temp_instance_id = str(instance_name) + "#" + str(local_instance_id)
        configuration_class_dict = configuration_name_to_dict[configuration_class_name]
        temp_configuration_node = configuration_node(
            config_dictionary=configuration_class_dict,
            configuration_point=configuration_point,
            instance_id=temp_instance_id, conjecture_data_dic=conjecture_data_dic)
        configuration_point_list = temp_configuration_node.get_configuration_point_list()

        # add remaining instances
        result_configuration_point_list = []
        for i in configuration_point_list:
            result = self.add_instance(i, static_configuration_id, local_instance_id + 1
                                       , instance_id=instance_id, conjecture_data_dic=conjecture_data_dic)
            result_configuration_point_list.extend(result)
        return result_configuration_point_list

    def add_static_configuration(self, configuration_point, instance_id=None, static_configuration_id=0,
                                 local_instance_id=0, conjecture_data_dic=None, **kwargs):
        if static_configuration_id == len(self.static_configuration_list):
            return [configuration_point]  # no more static configuration to add
        configuration_point_list = self.add_instance(configuration_point, static_configuration_id, local_instance_id,
                                                     instance_id, conjecture_data_dic, **kwargs)

        # add remaining static configuration
        result_configuration_point_list = []
        for i in configuration_point_list:
            result = self.add_static_configuration(i, instance_id, static_configuration_id + 1, **kwargs)
            result_configuration_point_list.extend(result)
        return result_configuration_point_list

    def get_configuration_point_list(self) -> list[ConfigurationPoint]:
        return self.configuration_point_list


class template_node:
    def __init__(self, template_name):
        self.template_name = template_name
        self.component_dict: dict[str, list[template_node] | template_node] = {}
        self.parameter_dict: dict[str, any] = {}

    @staticmethod
    def from_configuration_pointer_list(configuration_point: ConfigurationPoint):
        # get all the paths existed in the configuration pointer list
        path_list = []
        for key, value in configuration_point.items():
            if "$" in key:
                path_of_key = key.split("$")[1]
                steps = path_of_key.split("-")
                steps.insert(0, "root")
                path_list.append(steps)
            else:
                steps = ["root"]
                path_list.append(steps)
        # construct a tree based on the path list
        root = template_node("root")
        for i, key in enumerate(configuration_point.key_value.keys()):
            value = configuration_point[key]
            temp_node = root
            # get the node according to the path
            # skip the first step
            path = path_list[i]
            for j in range(1, len(path)):
                step = path[j]
                if step not in temp_node.component_dict:
                    temp_node.component_dict[step] = template_node(step)
                temp_node = temp_node.component_dict[step]
            # add the parameter
            key = key.split("$")[0]
            temp_node.parameter_dict[key] = value

        return root

    def __dict__(self) -> dict[str, any]:
        temp_dict = {}
        for key, value in self.component_dict.items():
            temp_dict[key] = value.__dict__()
        for key, value in self.parameter_dict.items():
            temp_dict[key] = value
        return temp_dict

    def to_yaml(self, file_name):
        current_path = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_path, "template")
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        if not file_name.endswith(".yaml"):
            file_name = file_name + ".yaml"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w") as f:
            yaml.dump(self.__dict__(), f)


def generate_template(conjecture_data_file_name, mode="f", template_file_name="template"):
    input_log_file = conjecture_data_file_name + "$" + template_file_name
    conjecture_data_dic = conjecture_data_loader(conjecture_data_file_name)
    IO_Multiplexer.get_instance(mode=mode)
    Logger_Singleton.get_instance(IO_Multiplexer.mode, file_name=input_log_file)
    Conjecture_Input(get_options_name_with_conjecture())
    a = configuration_node(config_dictionary=static_configuration_name_to_dict["exp_configuration"],
                           conjecture_data_dic=conjecture_data_dic)
    base_file_name = Logger_Singleton.get_file_name().split(".")[-2].split("/")[-1]
    file_name_list = []
    for i in range(len(a.get_configuration_point_list())):
        configuration_point = a.get_configuration_point_list()[i]
        file_name = base_file_name + "_" + str(i) + ".yaml"
        template_node.from_configuration_pointer_list(configuration_point).to_yaml(file_name)
        file_name_list.append(file_name)
    return file_name_list


if __name__ == "__main__":
    '''
        get the command line argument file_name if it exists
        format is python conjecture_data.py conjecture=filename
    '''
    import sys

    conjecture_data_file = None
    mode = None
    for arg in sys.argv:
        if arg.startswith("conjecture="):
            conjecture_data_file = arg.split("=")[1]
        if arg.startswith("mode="):
            mode = arg.split("=")[1]
    if conjecture_data_file == None:
        conjecture_data_file = "Machine2_Traffic1_Worker1"
    if mode == None:
        mode = "f"

    # generate_template(conjecture_data_file, mode)
