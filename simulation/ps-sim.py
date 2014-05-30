import numpy as np
import Queue

# Network characteristics
num_flows = 10
packet_size = 1000 # bytes
link_rate = 2.4 # Gbps
rtt = 0.1 # seconds

# Pareto
pareto_shape = 1.2
mean_npkts = 25

# Poisson arrival rate
load = 0.9
lamb = link_rate*load*1000000000/(mean_npkts*(packet_size)*8.0)

class Flow(object):
    def __init__(self, arrival, length):
        self.arrival = arrival # seconds
        self.length = length # number of packets
        self.bitlength = length*packet_size*8

    def __cmp__(self, other):
        return cmp(self.arrival, other.arrival)

def generate_flows(num_flows):
    all_flows = Queue.PriorityQueue()
    poisson_arrivals = np.random.poisson(lamb, num_flows)
    for i in range(num_flows):
        all_flows.put(Flow(poisson_arrivals[i], 2*i))
    return all_flows
        
if __name__ == "__main__":
    print "lambda:", lamb
    all_flows = generate_flows(10)
    while not all_flows.empty():
        flow = all_flows.get()
        print 'flow:', flow.arrival, flow.length
