#!/bin/bash

COUNTER=0
while [ $COUNTER -lt 20 ]; do
	python busters.py -p PacmanQAgent -s -t 0.0001
	COUNTER=$((COUNTER+1))
done
