#!/bin/bash
for fname in layouts/bigHunt.lay layouts/20Hunt.lay layouts/openClassic.lay layouts/openHunt.lay
do
	for i in 1 2 3 4 5; do
		python busters.py -p GreedyBustersAgent -l $fname -t 0.005 -q
	done
done
mv data/game.arff data/training_tutorial1.arff

for fname in layouts/bigHunt.lay layouts/20Hunt.lay layouts/openClassic.lay layouts/openHunt.lay
do
	for i in 1 2; do
		python busters.py -p GreedyBustersAgent -l $fname -t 0.005 -q
	done
done
mv data/game.arff data/test_samemaps_tutorial1.arff

for fname in layouts/trappedClassic.lay layouts/sixHunt.lay
do
	for i in 1 2 3; do
		python busters.py -p GreedyBustersAgent -l $fname -t 0.005 -q
	done
done
mv data/game.arff data/test_othermaps_tutorial1.arff
