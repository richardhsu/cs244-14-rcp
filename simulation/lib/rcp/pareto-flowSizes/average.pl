#!/usr/bin/perl -w

@fNameIn = ("logs/flow-pareto-sh1.2.tr", "logs/flow-pareto-sh2.2.tr");
@fNameOut = ("logs/flowSizeVsDelay-sh1.2", "logs/flowSizeVsDelay-sh2.2");

$maximum = 0;

for ($i=0; $i<=$#fNameIn; $i++) {

    for ($j=0; $j< 10000000; $j++) {
    $sumDur[$j] = 0;
    $avgDur[$j] = 0;
    $maxDur[$j] = 0;
    $numFlows[$j] = 0;
    }

    open(fileOut, ">$fNameOut[$i]") or dienice("Can't open $fNameOut[$i] for writing: $!");
    open(fileIn, "$fNameIn[$i]") or dienice ("Can't open $fNameIn[$i]: $!");

    $maximum = 0;
    $simTime = 65;
    while (<fileIn>) {
      chomp;
      @items = split;
      if ($items[1] <= $simTime) {
        if ($items[7] > $maximum) {
          $maximum = $items[7];
        }
        $sumDur[$items[7]] += $items[9];
        if ($items[9] > $maxDur[$items[7]]) {
          $maxDur[$items[7]] = $items[9];
        }
        $numFlows[$items[7]] += 1;
        $avgDur[$items[7]] = $sumDur[$items[7]] / $numFlows[$items[7]];
      }
    }

    for ($j=1; $j<= $maximum; $j++) {
      if ($avgDur[$j] != 0) {
        printf fileOut "$j sum_ $sumDur[$j] numFlows_ $numFlows[$j] avg_ $avgDur[$j] max_ $maxDur[$j] \n";
      }
    }

    close(fileIn);
    close(fileOut);
}

