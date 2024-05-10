from orchestration.configuration_template.conjecture_data import save_conjecture_data
from orchestration.configuration_template.create_exp import create_exp
from orchestration.configuration_template.template_generator import generate_template

# default value of the conjecture data
conjecture_data_default = {
    "machine_num": 2,
    "traffic_class_num": 1,
    "worker_num": 1
}  # the mapping between the conjecture data and the default value

# the mapping from the experiment name to the conjecture data, which represents the basic structure of the configuration
# override the default value of the conjecture data if necessary
exp_name_to_conjecture_data_dic_list = {
    "passthrough": [{
        "machine_num": 2,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "passthrough_testing": [{
        "machine_num": 1,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "cuckoo_hash_testing": [{
        "machine_num": 1,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "cuckoo_hash_rtc": [{
        "machine_num": 2,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "traffic_generator_veda": [{
        "machine_num": 1,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "traffic_generator_aum": [{
        "machine_num": 1,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "cuckoo_hash_flow_steering_example": [{
        "machine_num": 2,
        "traffic_class_num": 2,
        "worker_num": 2,
    }],
    "cuckoo_hash_rtc_state_size": [{
        "machine_num": 2,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "cuckoo_hash_interleaved": [{
        "machine_num": 2,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "sfc_cuckoo_hash_rtc": [{
        "machine_num": 2,
        "traffic_class_num": 1,
        "worker_num": 1,
    }],
    "interleaved_experiments": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "test_amf": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "optimized_sfc": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "test_amf_non_temporal": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "upf_monolithic": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "upf_interleaved": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "amf_monolithic": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        },
    ],
    "scalability_exp": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "real_world_rtc": [
        {
            "machine_num": 2,
            "traffic_class_num": 5,
            "worker_num": 1,
        }
    ],
    "real_world_interleaved": [
        {
            "machine_num": 2,
            "traffic_class_num": 5,
            "worker_num": 1,
        }
    ],
    "test_exp": [
        {
            "machine_num": 2,
            "traffic_class_num": 5,
            "worker_num": 1,
        }
    ],
    "bess_nat": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "fastclick_lb": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "amf_free5gc": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "sfc_simulation": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 1,
        }
    ],
    "traffic_generator_latency_test": [
        {
            "machine_num": 1,
            "traffic_class_num": 1,
            "worker_num": 2,
        }
    ],
    "bess_latency_test": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 2,
        }
    ],
    "interleaved_latency_test": [
        {
            "machine_num": 2,
            "traffic_class_num": 1,
            "worker_num": 2,
        }
    ],
}


def configuration_generation(exp_name):
    # conjecture data dic
    conjecture_data_dic_list = exp_name_to_conjecture_data_dic_list[exp_name]
    template_file_list = []
    for i, conjecture_data_dic in enumerate(conjecture_data_dic_list):
        # fill the default value
        for key, value in conjecture_data_default.items():
            if key not in conjecture_data_dic:
                conjecture_data_dic[key] = value
        conjecture_data_file_name = save_conjecture_data(conjecture_data_dic)
        template_file_name_l = generate_template(conjecture_data_file_name, template_file_name=exp_name)
        template_file_list.extend(template_file_name_l)
    create_exp({"exp_name": exp_name, "template_file_list": template_file_list})
    return template_file_list


if __name__ == "__main__":
    exp_name = "interleaved_latency_test"
    configuration_generation(exp_name)
