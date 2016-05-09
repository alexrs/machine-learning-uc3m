#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 10 ]; do
	python busters.py -p PacmanQAgent -s -t 0.05
	COUNTER=$((COUNTER+1))
done
