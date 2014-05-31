import numpy as np
import Queue
from scipy.stats import pareto

# Network characteristics
num_flows = 10000 
# Total number of flows in rcp simulation: 2399499
packet_size = 1000 # bytes
link_rate = 2.4 # Gbps
link_rate_bits = link_rate * (10**9)
rtt = 0.1 # seconds

delta = 0.00001

# Pareto
shape = 1.2
mean_npkts = 25
scale = (shape-1.0)/shape * mean_npkts

# Poisson arrival rate
load = 0.9
lamb = link_rate_bits*load/(mean_npkts*(packet_size)*8.0)

class Flow(object):
    def __init__(self, arrival, length, inter_arrival):
        self.arrival = arrival # seconds
        self.bitlength = length # number of bits 
        self.packet_length = self.bitlength/8000
        self.complete_dl = arrival + length/link_rate_bits
        self.buffered = 0.0
        # seconds lasted until this flow starts
        self.inter_arrival = inter_arrival
        self.fct = 0
        self.finished = False

    def __cmp__(self, other):
        return cmp(self.arrival, other.arrival)

class FlowCompletion(object):
    def __init__(self, length, fct):
        self.length = float(length) # number of packets
        self.fct = fct

    def __cmp__(self, other):
        return cmp(self.length, other.length)

def generate_flows(num_flows):
    all_flows = Queue.Queue()
    inter_arrivals = np.random.exponential(1.0/lamb, num_flows)
    flow_lengths = pareto.rvs(shape, scale=scale, size=num_flows)
    print "average flow length:", sum(flow_lengths)/num_flows
    prev_time = 0
    for i in range(num_flows):
        curr_time = prev_time + inter_arrivals[i]
        all_flows.put(Flow(curr_time, round(8*packet_size*flow_lengths[i]), inter_arrivals[i]))
        prev_time = curr_time
    return inter_arrivals, all_flows

def update_flows(curr_flows, duration, curr_time):
    stop_time = curr_time + duration
    print "Updating flow in time interval (%f, %f) Current active flows: %d." % (curr_time, stop_time, len(curr_flows))
    num_flows = len(curr_flows)
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
            flow.fct += delta # flow has progressed
            if flow.buffered <= 0.0 and flow.complete_dl < curr_time:
                # this flow has completed, so remove.
                print "Flow (arrival: %f, packets: %f) done at time %f, fct.%f" % (flow.arrival, flow.packet_length, curr_time, flow.fct)
                flow.finished = True
        curr_time += delta

    # update flow lists
    new_curr_flows = []
    done_flows = []
    for flow in curr_flows:
        if flow.finished:
            done_flows.append(flow)
        else:
            new_curr_flows.append(flow)
    
    return new_curr_flows, done_flows # flows completed in this duration

if __name__ == "__main__":
    print "Pareto distribution with shape:", shape, "mean:", mean_npkts
    print "Sanity check on pareto mean packets:", pareto.stats(shape, scale=scale, moments='m')
    print "Poisson process with lambda:", lamb
    inter_arrival, all_flows = generate_flows(num_flows)
    curr_flows = []
    all_done_flows = []
    curr_time = 0
    fct_q = Queue.PriorityQueue()
    while not all_flows.empty():
        flow = all_flows.get()
        print "flow (%f arrival, %d packets, %f completion), arrives after %f s" % (flow.arrival, flow.packet_length, flow.complete_dl, flow.inter_arrival)
        inter_arrival = flow.inter_arrival
        init_active_count = len(curr_flows)
        # update flows
        curr_flows, done_flows = update_flows(curr_flows, inter_arrival, curr_time)

        # update loop statestate
        curr_time += inter_arrival
        all_done_flows += done_flows

        for flow in done_flows:
            print "completed: flow (%f, %d)" % (flow.arrival, flow.packet_length)
            fct_q.put(FlowCompletion(flow.packet_length, flow.fct))

        print "Update at time %f: Initially active: %d, finished: %d, total_finished: %d" % (curr_time, init_active_count, len(done_flows), len(all_done_flows))
        curr_flows.append(flow) # newest arriving flow
        for flow in curr_flows:
            print "still waiting: flow (%f, %d)" % (flow.arrival, flow.packet_length)

    fct_list = []
    while not fct_q.empty():
        curr_fct = fct_q.get()
        # print "Flow completion: (%d, %f)" % (curr_fct.length, curr_fct.fct)
        fct_list.append((curr_fct.length, curr_fct.fct))
    # print fct_list
