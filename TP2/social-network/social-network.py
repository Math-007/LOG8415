import itertools
import sys

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType

if __name__ == "__main__":

    ALL_READY_CONNECTED_PENALTY = -sys.maxsize
    RECOMMENDED_LIST_LENGTH = 10

    if len(sys.argv) != 3:
        print("Usage: spark-submit socialNetwork.py <inputfile> <outputfile>", file=sys.stderr)
        exit(-1)

    spark = SparkSession.builder.appName("Friend recommendations app").getOrCreate()

    df = spark.read.csv(sys.argv[1], sep='\t')
    df_rdd = df.rdd \
        .filter(lambda data: len(data) == 2 and data[1] is not None) \
        .map(lambda data: (data[0], data[1].split(',')))

    already_friends = df_rdd.flatMap(
        lambda data: [((data[0], friend), ALL_READY_CONNECTED_PENALTY) for friend in data[1]]
    )
    potential_recommended_friends = df_rdd.flatMap(
        lambda data: [(friends_pair, 1) for friends_pair in itertools.permutations(data[1], 2)]
    )

    friends_recommendation_score = already_friends.union(potential_recommended_friends)

    raw_user_recommendation = friends_recommendation_score.reduceByKey(
        lambda score1, score2: score1 + score2
    )

    valid_recommendations = raw_user_recommendation.filter(
        lambda data: data[1] > 0  # remove negative scores
    )
    user_recommendation = valid_recommendations.map(
        lambda data: (data[0][0], (data[0][1], data[1]))  # (user, (friend, score))
    )

    # To avoid using groupByKey:
    # https://spark.apache.org/docs/3.1.1/api/python/reference/api/pyspark.RDD.combineByKey.html
    def to_list(a):
        return [a]

    def append(a, b):
        a.append(b)
        return a

    def extend(a, b):
        a.extend(b)
        return a

    combined_user_recommendations = user_recommendation.combineByKey(
        to_list, append, extend
    )

    recommended_friends = combined_user_recommendations.map(
        lambda data: (
            data[0],
            sorted(data[1], key=lambda recommendation: recommendation[1])[:RECOMMENDED_LIST_LENGTH]
        )
    )

    recommended_friends.toDF(['user', '(friend, score)']).show()

    print("")
