from pprint import pprint

result = {
    "14": {
        "flows_100k_pps": 11009984,
        "durations": 60,
        "packet_header": 13350,  # ms
        "perflow_state": 4405,  # ms4405
    },
    "15": {
        "flows_100k_pps": 10597907,
        "durations": 60,
        "packet_header": 13600,  # ms
        "perflow_state": 5864,  # ms
    },

    "16": {
        "flows_100k_pps": 9997716,
        "durations": 60,
        "packet_header": 12900,  # ms
        "perflow_state": 8400,  # ms
    },

    "17": {
        "flows_100k_pps": 9526296,
        "durations": 60,
        "packet_header": 12300,  # ms
        "perflow_state": 10800,  # ms
    },

    "18": {
        "flows_100k_pps": 9277977,
        "durations": 60,
        "packet_header": 11700,  # ms
        "perflow_state": 12000,  # ms
    },

    "19": {
        "flows_100k_pps": 9089088,
        "durations": 60,
        "packet_header": 11700,  # ms
        "perflow_state": 12800,  # ms
    },

    "20": {
        "flows_100k_pps": 8886579,
        "durations": 60,
        "packet_header": 11400,  # ms
        "perflow_state": 13900,  # ms
    }
}


def ms_to_ns(ms):
    return ms * 1000000


def exp_data_extraction(exp):
    packet_header_time = exp["packet_header"]
    per_flow_state_time = exp["perflow_state"]
    # matching_time = exp["matching"]
    flows_100k_pps = exp["flows_100k_pps"]
    durations = exp["durations"]
    packet_header_time_per_packet = ms_to_ns(packet_header_time / (flows_100k_pps * durations))
    per_flow_state_time_per_packet = ms_to_ns(per_flow_state_time / (flows_100k_pps * durations))
    # matching_time_per_packet = ms_to_ns(matching_time / (flows_100k_pps * durations))
    per_packet_processing_time = (1/flows_100k_pps) * 1000000000
    return {
        "packet_header_time_pp": packet_header_time_per_packet,
        "per_flow_state_time_pp": per_flow_state_time_per_packet,
        # "matching_time_pp": matching_time_per_packet,
        "per_packet_processing_time": per_packet_processing_time
    }


if __name__ == "__main__":
    output_result = {}
    for key in result.keys():
        print(key, exp_data_extraction(result[key]))
        output_result[key] = exp_data_extraction(result[key])
    # export the data to yaml in the current directory
    import yaml
    with open('lb_data.yaml', 'w') as outfile:
        yaml.dump(output_result, outfile, default_flow_style=False)


