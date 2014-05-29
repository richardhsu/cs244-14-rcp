#!/usr/bin/perl -w

$sim_end = 300;
$cap = 2.4;
$rtt = 0.1;
$alpha = 0.1;
$beta = 1;
$load = 0.8;
$numbneck = 1;
$BWdelay = ($rtt*$cap*1000000000)/(1000*8);
@pareto_shape = (1.8);
$meanFlowSize = $BWdelay/1000;
$init_nr_flows = 5000;

for ($i = 0; $i < @pareto_shape; $i++) {

`nice ns sim-rcp-pareto.tcl $sim_end $cap $rtt $load $numbneck $alpha $beta $init_nr_flows $meanFlowSize $pareto_shape[$i] > logFile`;
`mv logFile logFile-pareto-sh$pareto_shape[$i]`;
`mv flow.tr flow-pareto-sh$pareto_shape[$i].tr`;
`mv queue.tr queue-pareto-sh$pareto_shape[$i].tr`;
`mv rcp_status.tr rcp-pareto-sh$pareto_shape[$i].tr`;

}

