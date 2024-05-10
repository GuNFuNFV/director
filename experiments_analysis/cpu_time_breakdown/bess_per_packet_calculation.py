from pprint import pprint

from runtime_agent import exp_loader
from runtime_agent.exp_result.exp_result_manager import read_file

result = {
    "12": {
        "flows_100k_pps": 5531443,
        "durations": 60,
        "packet_header": 7000,  # ms
        "perflow_state": 2800,  # ms
        "matching": 9633  # ms
    },

    "13": {
        "flows_100k_pps": 5325029,
        "durations": 60,
        "packet_header": 6946,  # ms
        "perflow_state": 2772,  # ms
        "matching": 10505  # ms
    },

    "14": {
        "flows_100k_pps": 5285977,
        "durations": 60,
        "packet_header": 6581,  # ms
        "perflow_state": 3152,  # ms
        "matching": 10976  # ms
    },
    "15": {
        "flows_100k_pps": 5160121,
        "durations": 60,
        "packet_header": 6285,  # ms
        "perflow_state": 3483,  # ms
        "matching": 11552  # ms
    },

    "16": {
        "flows_100k_pps": 4664255,
        "durations": 60,
        "packet_header": 6074,  # ms
        "perflow_state": 4030,  # ms
        "matching": 12369  # ms
    },

    "17": {
        "flows_100k_pps": 4236899,
        "durations": 60,
        "packet_header": 5458,  # ms
        "perflow_state": 4471,  # ms
        "matching": 13600  # ms
    },

    "18": {
        "flows_100k_pps": 3822569,
        "durations": 60,
        "packet_header": 4877,  # ms
        "perflow_state": 4235,  # ms
        "matching": 13913  # ms
    },

    "19": {
        "flows_100k_pps": 3594512,
        "durations": 60,
        "packet_header": 4691,  # ms
        "perflow_state": 3874,  # ms
        "matching": 14459  # ms
    },

    "20": {
        "flows_100k_pps": 3449019,
        "durations": 60,
        "packet_header": 4581,  # ms
        "perflow_state": 3588,  # ms
        "matching": 14920  # ms
    }
}


def ms_to_ns(ms):
    return ms * 1000000


def exp_data_extraction(exp):
    packet_header_time = exp["packet_header"]
    per_flow_state_time = exp["perflow_state"]
    matching_time = exp["matching"]
    flows_100k_pps = exp["flows_100k_pps"]
    durations = exp["durations"]
    packet_header_time_per_packet = ms_to_ns(packet_header_time / (flows_100k_pps * durations))
    per_flow_state_time_per_packet = ms_to_ns(per_flow_state_time / (flows_100k_pps * durations))
    matching_time_per_packet = ms_to_ns(matching_time / (flows_100k_pps * durations))
    per_packet_processing_time = (1/flows_100k_pps) * 1000000000
    return {
        "packet_header_time_pp": packet_header_time_per_packet,
        "per_flow_state_time_pp": per_flow_state_time_per_packet,
        "matching_time_pp": matching_time_per_packet,
        "per_packet_processing_time": per_packet_processing_time
    }


def old_calculation():
    output_result = {}
    for key in result.keys():
        print(key, exp_data_extraction(result[key]))
        output_result[key] = exp_data_extraction(result[key])
    # export the data to yaml in the current directory
    import yaml
    with open('data.yaml', 'w') as outfile:
        yaml.dump(output_result, outfile, default_flow_style=False)


def get_throughput(df):
    throughput = df["0_throughput"]
    result = []
    for item in throughput:
        evaled = eval(item)[0][0]
        result.append(evaled)
    return result


def get_l1_miss(df):
    data = df["l1d.replacement"]
    result = []
    for item in data:
        result.append(eval(item)[0])
    return result


def get_l2_miss(df):
    data = df["MEM_LOAD_RETIRED.L2_MISS"]
    result = []
    for item in data:
        result.append(eval(item)[0])
    return result


def get_l3_miss(df):
    data = df["LLC-load-misses"]
    result = []
    for item in data:
        result.append(eval(item)[0])

    data_2 = df["LLC-store-misses"]
    for item in range(len(data_2)):
        result[item] += eval(data_2[item])[0]
    return result


def get_access_time(df):
    data = df["hotspot"]
    result = []
    for i in data:
        filename = str((int(i)))
        lines = read_file(filename)
        temp_result = 0
        for line in lines:
            if "bess_nat" in line:
                temp_result += float(line.split("%")[0])
        result.append(temp_result)
    return result



if __name__ == "__main__":
    df = exp_loader("bess_nat")
    # print(df)
    print(df.columns)
    # print(get_access_time(df))
    # print(get_throughput(df))
    # print(get_l1_miss(df))
    # print(get_l2_miss(df))
    # print(get_l3_miss(df))

    # state_access_time = get_access_time(df)
    throughput_list = get_throughput(df)
    # per_packet_processing_time = [1 / throughput_list[i] for i in range(len(throughput_list))]
    # state_acess_time_per_packet = [state_access_time[i] * per_packet_processing_time[i] / 100 * 1000000000 for i in
    #                                range(len(state_access_time))]

    l1_miss_list = get_l1_miss(df)
    l1_miss_per_packet_list = [l1_miss_list[i] / throughput_list[i] for i in range(len(l1_miss_list))]
    l2_miss_list = get_l2_miss(df)
    l2_miss_per_packet_list = [l2_miss_list[i] / throughput_list[i] for i in range(len(l2_miss_list))]
    l3_miss_list = get_l3_miss(df)
    l3_miss_per_packet_list = [l3_miss_list[i] / throughput_list[i] for i in range(len(l3_miss_list))]
    print(l1_miss_per_packet_list)
    print(l2_miss_per_packet_list)
    print(l3_miss_per_packet_list)
    print(throughput_list)




