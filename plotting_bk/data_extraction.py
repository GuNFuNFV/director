import math


def extract_concurrent_flows(row):
    return int(row["traffic_generator_concurrency"])


def extract_state_size(row):
    return int(row["generic_access_size"])


def extract_packet_num(row):
    return int(row["packet_num"])


def extract_packet_size(row):
    return int(row["traffic_generator_packet_size"])


def extract_throughput(row):
    packet_size = extract_packet_size(row)
    packet_num = extract_packet_num(row)
    return packet_num * packet_size * 8 / 1000000000


def extract_l1_miss_rate(row):
    return float(row["l1_miss_rate"])


def extract_l2_miss_rate(row):
    return float(row["l2_miss_rate"])


def extract_llc_miss_rate(row):
    return float(row["llc_miss_rate"])


def extract_instructions(row):
    return float(row["instructions"])


def extract_cycles(row):
    return float(row["cycles"])


def extract_ipc(row):
    return float(extract_instructions(row)) / float(extract_cycles(row))


def extract_packet_num(row):
    return float(row["packet_num"])


def extract_l1_dcache_load_misses(row):
    return float(row["l1_dcache_load_misses"])


def extract_l1_miss_per_packet(row):
    return float(extract_l1_dcache_load_misses(row)) / float(extract_packet_num(row))


def extract_l2_rqsts_demand_data_rd_miss(row):
    return float(row["l2_rqsts_demand_data_rd_miss"])


def extract_l2_miss_per_packet(row):
    return float(extract_l2_rqsts_demand_data_rd_miss(row)) / float(extract_packet_num(row))


def extract_llc_load_misses(row):
    return float(row["llc_load_misses"])


def extract_llc_miss_per_packet(row):
    return float(extract_llc_load_misses(row)) / float(extract_packet_num(row))


key_to_extractor = {
    "concurrent flows": extract_concurrent_flows,
    "state size": extract_state_size,
    "throughput": extract_throughput,
    "l1 cache miss rate": extract_l1_miss_rate,
    "l2 cache miss rate": extract_l2_miss_rate,
    "last level cache miss rate": extract_llc_miss_rate,
    "instructions": extract_instructions,
    "cycles": extract_cycles,
    "ipc": extract_ipc,
    "l1 cache miss per packet": extract_l1_miss_per_packet,
    "l2 cache miss per packet": extract_l2_miss_per_packet,
    "last level cache miss per packet": extract_llc_miss_per_packet,
}

key_to_label = {
    # latex of 2 to the power of x
    "concurrent flows": "# concurrent flows ($2^x$)",
    "state size": "state size (# cache line)",
    "throughput": "throughput (Gbps)",
    "l1 cache miss rate": "miss rate",
    "l2 cache miss rate": "miss rate",
    "last level cache miss rate": "miss rate",
    "instructions": "instructions",
    "cycles": "cycles",
    "ipc": "ipc",
    "l1 cache miss per packet": "l1 miss per packet",
    "l2 cache miss per packet": "l2 miss per packet",
    "last level cache miss per packet": "llc miss per packet",
}


def log_2(x):
    return (int)(math.log(x, 2))


def identity(x):
    return x


key_to_x_tick = {
    "concurrent flows": log_2,
    "state size": identity,
}


class PlotConfiguration:
    def __init__(self, x_axis, y_axis_list):
        self.x_axis = x_axis
        self.y_axis_list = y_axis_list


exp_name_to_list_of_plot_configuration = {
    "motivation": [
        PlotConfiguration("concurrent flows", ["throughput"]),
        PlotConfiguration("concurrent flows", ["l1 cache miss per packet"]),
        PlotConfiguration("concurrent flows", ["last level cache miss per packet"]),
        PlotConfiguration("concurrent flows", ["ipc"])
    ],

    "motivation_generic_complex_state": [
        PlotConfiguration("state size", ["throughput"]),
        PlotConfiguration("state size", ["l1 cache miss per packet"]),
        PlotConfiguration("state size", ["last level cache miss per packet"]),
        PlotConfiguration("state size", ["ipc"])
    ]
}
