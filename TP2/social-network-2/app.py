import itertools
import sys

from pyspark import SparkContext

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: spark-submit socialNetwork.py <inputfile> <outputfile>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="Friend recommendations app")
    lines = sc.textFile(sys.argv[1], 1)
    lines = lines.map(lambda line: line.split())
    friends = lines.filter(lambda x: len(x) == 2).map(lambda t: (t[0], t[1].split(",")))

    # # map pairs of friends
    directFriends = friends.flatMap(lambda data: [((data[0], friend), -1000000) for friend in data[1]])
    mutualFriends = friends.flatMap(lambda data: [(pair, 1) for pair in itertools.permutations(data[1], 2)])
    fullList = directFriends.union(mutualFriends)
    # #
    # reduce to get recommendation list for every user based on number of mutual friends
    fullList = fullList.reduceByKey(lambda x, y: x + y)
    mutualCount = fullList\
        .filter(lambda x, count: count > 0)\
        .map(lambda user, friend, count: (user, (count, friend)))\
        .groupByKey()\
        .mapValues(list)

    print("******* TEST *******")

    # sort based on number of mutual friends and the list is capped at 10
    # print("mutualCount:  ", mutualCount)
    # first = mutualCount.first()
    print("*** first ***** , ")

    def one(x, data):
        return x, sorted(data, key=lambda xs: (-xs[0], int(xs[1])))


    mutualCount = mutualCount\
        .map(lambda x, data, c: (x, sorted(data, key=lambda x: (-x[0], int(x[1])))))\
        .map(lambda x, data, c: (x, data[:10]))\
        .map(lambda x, data: (x, [i[1] for i in data]))
    active = mutualCount.collect()
    #
    # edit content to present in specified format
    # for i in range(len(active)):
    #     active[i] = str(active[i][0]) + "\t" + ",".join(str(item) for item in active[i][1])
    lonely = lines.filter(lambda x: len(x) == 1).flatMap(lambda x: x).collect()
    complete = active + lonely
    sc.parallelize(complete).repartition(1).saveAsTextFile(sys.argv[2])
    sc.stop()
