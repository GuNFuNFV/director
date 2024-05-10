def return_variables():
    col_name = [
        "worker_0_traffic_class_0_destination_instance",
        "worker_0_traffic_class_0_flow_id_upper",
        "worker_0_traffic_class_0_proportion",
        "worker_0_traffic_class_1_destination_instance",
        "worker_0_traffic_class_1_flow_id_lower",
        "worker_0_traffic_class_1_proportion",
        "worker_1_traffic_class_0_destination_instance",
        "worker_1_traffic_class_0_flow_id_upper",
        "worker_1_traffic_class_0_proportion",
        "worker_1_traffic_class_1_destination_instance",
        "worker_1_traffic_class_1_flow_id_lower",
        "worker_1_traffic_class_1_proportion",
    ]
    input_list = [
        "worker_0_traffic_class_0_destination_instance",
        "worker_0_traffic_class_1_destination_instance",
        "worker_0_traffic_class_0_flow_id_upper",
        "worker_0_traffic_class_0_proportion",
        "worker_1_traffic_class_0_destination_instance",
        "worker_1_traffic_class_1_destination_instance",
    ]

    input_1 = {
        "worker_0_traffic_class_0_destination_instance": 0,
        "worker_0_traffic_class_1_destination_instance": 0,
        "worker_0_traffic_class_0_flow_id_upper": 10000,
        "worker_0_traffic_class_0_proportion": 200,
        "worker_1_traffic_class_0_destination_instance": 0,
        "worker_1_traffic_class_1_destination_instance": 0,
        "num_possible_interleaved_threads": 1,
    }  # no flow steering

    proportion = [10*i for i in range(1, 30)]
    input_list = [
        {
            "worker_0_traffic_class_0_destination_instance": 0,
            "worker_0_traffic_class_1_destination_instance": 2,
            "worker_0_traffic_class_0_flow_id_upper": 10000,
            "worker_0_traffic_class_0_proportion": p,
            "worker_1_traffic_class_0_destination_instance": -2,
            "worker_1_traffic_class_1_destination_instance": 0,
            "num_possible_interleaved_threads": 16,
        } for p in proportion
    ]  # with flow steering



    # with the input, derive other variables
    result = []
    result.append(derive_variables(input_1))
    for input_dict in input_list:
        result.append(derive_variables(input_dict))
    return result


def derive_variables(input_dict: dict):
    result = {}
    result["worker_0_traffic_class_0_destination_instance"] = input_dict[
        "worker_0_traffic_class_0_destination_instance"]
    result["worker_0_traffic_class_0_flow_id_upper"] = input_dict["worker_0_traffic_class_0_flow_id_upper"]
    result["worker_0_traffic_class_0_proportion"] = input_dict["worker_0_traffic_class_0_proportion"]
    result["worker_0_traffic_class_1_destination_instance"] = input_dict[
        "worker_0_traffic_class_1_destination_instance"]
    result["worker_0_traffic_class_1_flow_id_lower"] = input_dict["worker_0_traffic_class_0_flow_id_upper"] + 1
    result["worker_0_traffic_class_1_proportion"] = 300 - input_dict["worker_0_traffic_class_0_proportion"]
    result["worker_1_traffic_class_0_destination_instance"] = input_dict[
        "worker_1_traffic_class_0_destination_instance"]
    result["worker_1_traffic_class_0_flow_id_upper"] = input_dict["worker_0_traffic_class_0_flow_id_upper"]
    result["worker_1_traffic_class_0_proportion"] = input_dict["worker_0_traffic_class_0_proportion"]
    result["worker_1_traffic_class_1_destination_instance"] = input_dict[
        "worker_1_traffic_class_1_destination_instance"]
    result["worker_1_traffic_class_1_flow_id_lower"] = input_dict["worker_0_traffic_class_0_flow_id_upper"] + 1
    result["worker_1_traffic_class_1_proportion"] = 300 - input_dict["worker_0_traffic_class_0_proportion"]
    result["num_possible_interleaved_threads"] = input_dict["num_possible_interleaved_threads"]
    return result


def return_scaling():
    return [1]
