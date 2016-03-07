#!/bin/bash
for fname in layouts/bigHunt.lay layouts/20Hunt.lay layouts/openClassic.lay layouts/openHunt.lay
do
	for i in 1 2 3 4 5; do
		python busters.py -p GreedyBustersAgent -l -t 0.005 $fname
	done
done