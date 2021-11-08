#!/bin/bash

# https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html#Example:_WordCount_v1.0
wordcount_jar="/opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.1.jar"

for f in $1/*.txt; do
	echo $f

	for i in {1..3}; do
		hdfs dfs -rm -f -r $1/output &>/dev/null
		before=$(date +"%s.%N")
		hadoop jar $wordcount_jar wordcount -files $f $1 $1/output &>/dev/null
		after=$(date +"%s.%N")

		echo $after-$before | bc
	done
done
