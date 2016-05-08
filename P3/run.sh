#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 30 ]; do
	python busters.py -p P3QLearning -s
	COUNTER=$((COUNTER+1))
done
COUNTER=0
while [ $COUNTER -lt 30 ]; do
	python busters.py -p P3QLearning -l layouts/finalMap.lay -s
	COUNTER=$((COUNTER+1))
done

COUNTER=0
while [ $COUNTER -lt 30 ]; do
	python busters.py -p P3QLearning -l layouts/classic.lay -s
	COUNTER=$((COUNTER+1))
done
