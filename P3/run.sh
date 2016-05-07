#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 100 ]; do
	python busters.py -p P3QLearning
	let  COUNTER=COUNTER+1
done
COUNTER1=0
while [ $COUNTER1 -lt 100 ]; do
	python busters.py -p P3QLearning -l layouts/finalMap.lay
	let  COUNTER1=COUNTER1+1
done

COUNTER2=0
while [ $COUNTER2 -lt 100 ]; do
	python busters.py -p P3QLearning -l layouts/classic.lay
	let  COUNTER2=COUNTER2+1
done
