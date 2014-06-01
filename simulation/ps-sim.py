import numpy as np
import Queue
from scipy.stats import pareto


# Network characteristics
num_flows = 2399499
# Total number of flows in rcp simulation: 2399499
packet_size = 1000 # bytes
link_rate = 2.4 # Gbps
link_rate_bits = link_rate * (10**9)
rtt = 0.1 # seconds

delta = 0.0000001

# Pareto
shape = 1.2
mean_npkts = 25
scale = (shape-1.0)/shape * mean_npkts

# Poisson arrival rate
load = 0.9
lamb = link_rate_bits*load/(mean_npkts*(packet_size)*8.0)

# Output parameters and details
debug_flag = False
output_file = "lib/ps/pareto-flowSizes/logs/flowSizeVsDelay-sh" + str(shape)
log_file_str = "lib/ps/pareto-flowSizes/logs/logFile-sh" + str(shape)

log_file = open(log_file_str, 'w')

class Flow(object):
    def __init__(self, arrival, length, inter_arrival):
        self.arrival = arrival # seconds
        self.bitlength = length # number of bits 
        self.packet_length = self.bitlength/(8*packet_size)
        self.complete_dl = arrival + length/link_rate_bits
        self.buffered = 0.0
        # seconds lasted until this flow starts
        self.inter_arrival = inter_arrival
        self.fct = -1 # default: not complete 
        self.finished = False
        self.max_flows_bottleneck = 0 # how many flows this one competed with

    def __cmp__(self, other):
        return cmp(self.arrival, other.arrival)

def generate_flows(num_flows):
    log_file.write("Generating flows...\n")
    all_flows = Queue.Queue()
    inter_arrivals = np.random.exponential(1.0/lamb, num_flows)
    flow_lengths = pareto.rvs(shape, scale=scale, size=num_flows)
    log_file.write("average flow length:%f \n" % (sum(flow_lengths)/num_flows))
    prev_time = 0
    for i in range(num_flows):
        curr_time = prev_time + inter_arrivals[i]
        flow = Flow(curr_time, int(8*packet_size*flow_lengths[i]), inter_arrivals[i])
        all_flows.put(flow)
        prev_time = curr_time
        if debug_flag:
            log_file.write("flow created: (%.8f, %d).\n" % (flow.arrival, flow.packet_length))
    max_packets = int(max(flow_lengths))
    log_file.write("Finished flow generation.\n")
    log_file.write("\n")
    return inter_arrivals, all_flows, max_packets

def update_flows(curr_flows, duration, curr_time):
    stop_time = curr_time + duration
    log_file.write("Starting update in time (%.8f, %.8f) Current active flows: %d.\n" % (curr_time, stop_time, len(curr_flows)))

    # update flow lists
    new_curr_flows = []
    done_flows = []
    if not curr_flows:
        log_file.write("No flows to update in this interval.\n")
    num_flows = len(curr_flows)
    # update how many flows each flow competed with
    for flow in curr_flows:
        flow.max_flows_bottleneck = max(num_flows, flow.max_flows_bottleneck)
    while curr_time < stop_time:
        for i in range(len(curr_flows)):
            flow = curr_flows[i]
            if flow.finished:
                continue
            if flow.arrival < curr_time and curr_time < flow.complete_dl:
                incoming = link_rate_bits * delta
                # incoming = link_rate_bits * min(delta, self.complete_dl - curr_time)
                flow.buffered += incoming
            outgoing = link_rate_bits * delta / (num_flows)
            flow.buffered = max(0.0, flow.buffered - outgoing)
            if flow.buffered <= 0.0 and flow.complete_dl < curr_time:
                # this flow has completed, so remove.
                flow.fct = curr_time
                flow.finished = True
                log_file.write("Finished flow (arrival: %.8f, packets: %d); fct %f\n" % (flow.arrival, flow.packet_length, flow.fct))
        curr_time += delta

    for flow in curr_flows:
        if debug_flag:
            log_file.write("status of flow (%.8f, %d): (fct: %.8f, finished: %s)\n" % (flow.arrival, flow.packet_length, flow.fct, flow.finished))
        if flow.finished:
            done_flows.append(flow)
        else:
            new_curr_flows.append(flow)
    
    return new_curr_flows, done_flows # flows completed in this duration

def arrival_log(new_flow):
    return "Arrival at time %.8f (after %.8f s): flow (%d packets, %.8f completion)" % (new_flow.arrival, new_flow.inter_arrival, new_flow.packet_length, new_flow.complete_dl)

def update_log(curr_time, init_active_count, finished, total_finished):
    return "Update at time %.8f: Initially active: %d, finished: %d, total_finished: %d" % (curr_time, init_active_count, finished, total_finished)

def packet_info(all_done_flows):
    fcts_aggregate = {}
    for flow in all_done_flows:
        if int(flow.packet_length) not in fcts_aggregate:
            fcts_aggregate[int(flow.packet_length)] = []
        entries = fcts_aggregate[int(flow.packet_length)]
        entries.append(flow.fct)

    if debug_flag:
        for packet_length in fcts_aggregate.keys():
            log_file.write("packet length: %d \n" % (packet_length), fcts_aggregate[packet_length])
    return fcts_aggregate

def average_fct(fcts_aggregate):
    avg_fcts = {}
    for packet_length in fcts_aggregate.keys():
        packet_entries = fcts_aggregate[packet_length]
        avg_fcts[packet_length] = sum(packet_entries)/len(packet_entries)
    return avg_fcts

def max_fct(fcts_aggregate):
    max_fcts = {}
    for packet_length in fcts_aggregate.keys():
        max_fcts[packet_length] = max(fcts_aggregate[packet_length]) 
    return max_fcts

def simulate():
    """
    """
    log_file.write("Pareto distribution with shape: %d, mean: %d\n" % (shape, mean_npkts))
    log_file.write("Sanity check on pareto mean packets: %f\n" % (pareto.stats(shape, scale=scale, moments='m')))
    log_file.write("Poisson process with lambda: %f\n" % (lamb))
    inter_arrival, all_flows, max_packets = generate_flows(num_flows)
    curr_flows = []
    all_done_flows = []
    curr_time = 0
    while not all_flows.empty():
        new_flow = all_flows.get()
        inter_arrival = new_flow.inter_arrival
        init_active_count = len(curr_flows)
        # update flows
        curr_flows, done_flows = update_flows(curr_flows, inter_arrival, curr_time)

        # update loop state
        curr_time += inter_arrival
        all_done_flows += done_flows

        log_file.write(update_log(curr_time, init_active_count, len(done_flows), len(all_done_flows)))
        log_file.write("\n")

        curr_flows.append(new_flow) # newest arriving flow
        log_file.write(arrival_log(new_flow))
        log_file.write("\n\n")

    # all flows have arrived, so migrate to updating once every E[arrival] = 1/lamb.
    log_file.write("All flows have arrived. Updating remaining flows...\n")
    update_duration = 1.0/lamb
    while len(all_done_flows) != num_flows:
        init_active_count = len(curr_flows)
        curr_flows, done_flows = update_flows(curr_flows, update_duration, curr_time)
        curr_time += update_duration
        all_done_flows += done_flows
        log_file.write(update_log(curr_time, init_active_count, len(done_flows), len(all_done_flows)))
        log_file.write("\n")

    log_file.write("Finished simulation. FCT results:\n")
    for done_flow in all_done_flows:
        if debug_flag:
            log_file.write("(packets: %d, fct: %.8f, bottleneck: %d flows)\n" % (done_flow.packet_length, done_flow.fct, done_flow.flow_bottleneck))
    fcts_aggregate = packet_info(all_done_flows)
    avg_fcts = average_fct(fcts_aggregate)
    max_fcts = max_fct(fcts_aggregate)

    packet_list = avg_fcts.keys()
    packet_list.sort()
    ret_list = []
    for packet_length in packet_list:
        log_file.write("Packet length: %d, average FCT: %.8f, max FCT: %.8f\n" % (packet_length, avg_fcts[packet_length], max_fcts[packet_length]))
        ret_list.append((packet_length, avg_fcts[packet_length], max_fcts[packet_length]))
    return ret_list # tuples (packet_length, average fct)

if __name__ == "__main__":
    ret_list = simulate()
    f = open(output_file, 'w')
    for entry in ret_list:
        f.write('%d 0 0 0 0 0 %.12f 0 %.12f\n' % entry)
    f.close()
