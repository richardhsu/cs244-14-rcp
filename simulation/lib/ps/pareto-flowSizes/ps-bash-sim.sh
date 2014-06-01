#!/bin/bash

# usage: python ps.sim.py <pareto shape> <link capacity> [num_of_flows: default 100]
python ps-sim.py 1.2 2.4 10000 > /dev/null
python ps-sim.py 2.2 2.4 10000 > /dev/null
