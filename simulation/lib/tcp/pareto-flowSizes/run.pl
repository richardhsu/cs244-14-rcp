#!/usr/bin/perl -w

$numFlows = 100000;
$cap = 2.4;
$rtt = 0.1;
$load = 0.9;
$numbneck = 1;
# $BWdelay = ($rtt*$cap*1000000000)/(1000*8);
$init_nr_flows = 10000;
$meanFlowSize = 25;
@pareto_shape = (1.2, 2.2);

for ($i = 0; $i < @pareto_shape; $i++) {
  `nice -n +20 ns sim-tcp-pareto.tcl $numFlows $cap $rtt $load $numbneck $init_nr_flows $meanFlowSize $pareto_shape[$i] > logs/logFile-pareto-sh$pareto_shape[$i]`;

  # Move extra traces to logs folder
  `mv flow.tr logs/flow-pareto-sh$pareto_shape[$i].tr`;
  `mv queue.tr logs/queue-pareto-sh$pareto_shape[$i].tr`;
}

