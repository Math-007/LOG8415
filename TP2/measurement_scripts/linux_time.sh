#!/bin/bash

directory=$1

for f in $1/*.txt; do
	echo $f

	for i in {1..3}; do
		before=$(date +"%s.%N")
		cat $f | tr ' ' "\n" | sort | uniq -c > /dev/null
		after=$(date +"%s.%N")

		echo $after-$before | bc
	done
done
