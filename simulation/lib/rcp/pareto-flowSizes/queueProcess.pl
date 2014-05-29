#!/usr/bin/perl -w

$C = 2.4*1000000000/8;

@fNameIn = ("queue-pareto-sh1.8.tr");
@fNameOut = ("linkUtil-sh1.8");

for ($i=0; $i<=$#fNameIn; $i++) {

    open(fileOut, ">$fNameOut[$i]") or dienice("Can't open $fNameOut[$i] for writing: $!");
    open(fileIn, "$fNameIn[$i]") or dienice ("Can't open $fNameIn[$i]: $!");

    $prev = 0;
    $BDeparture = 0;
    while (<fileIn>) {
      chomp;
      @items = split;

      $totBDeparture = $items[9];
      $BDeparture = $totBDeparture - $prev;
      $prev = $totBDeparture;
      printf fileOut "$items[0] BDeparture_ $BDeparture Bqueue_ $items[3]\n";
    }
    print $totBDeparture/($items[0] * $C) ;
    print "\n";

    close(fileIn);
    close(fileOut);
}

