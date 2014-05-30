#!/usr/bin/perl -w

$sim_end = 300;
$cap = 2.4;
$rtt = 0.1;
$alpha = 0.1;
$beta = 1;
$load = 0.9;
$numbneck = 1;
$BWdelay = ($rtt*$cap*1000000000)/(1000*8);
@pareto_shape = (1.2);
$meanFlowSize = $BWdelay/1000;
$init_nr_flows = 5000;

for ($i = 0; $i < @pareto_shape; $i++) {
  `nice ns sim-rcp-pareto.tcl $sim_end $cap $rtt $load $numbneck $alpha $beta $init_nr_flows $meanFlowSize $pareto_shape[$i] > logs/logFile-pareto-sh$pareto_shape[$i]`;
  # Move extra traces to logs folder
  `mv flow.tr logs/flow-pareto-sh$pareto_shape[$i].tr`;
  `mv queue.tr logs/queue-pareto-sh$pareto_shape[$i].tr`;
  `mv rcp_status.tr logs/rcp-pareto-sh$pareto_shape[$i].tr`;
}

