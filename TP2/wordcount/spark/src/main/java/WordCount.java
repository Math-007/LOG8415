import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import scala.Tuple2;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;

// Inspired from https://javadeveloperzone.com/spark/spark-wordcount-example/
public class WordCount {

    private static final int PASS_PER_FILE = 3;

    public static void main(String[] args) throws IOException {

        SparkConf conf = new SparkConf()
                .setAppName("wordcount-spark")
                .setMaster("local[4]");
        JavaSparkContext sparkContext = new JavaSparkContext(conf);

        Files.walk(new File(args[0]).toPath())
                .filter(Files::isRegularFile)
                .filter(f -> f.toString().endsWith("txt"))
                .forEach(f -> processFile(f, args[1], sparkContext));

        sparkContext.close();
    }

    private static void processFile(Path file, String outputBasePath, JavaSparkContext sparkContext) {
        String filename = file.getFileName().toString();
        JavaRDD<String> textFile = sparkContext.textFile(file.toString());
        long totalExecTime = 0L;

        for (int i = 0; i < PASS_PER_FILE; i++) {
            String outputPath = Paths.get(outputBasePath, filename.substring(0, filename.length() - 4), String.valueOf(i)).toString();

            Instant start = Instant.now();

            JavaRDD<String> words = textFile.flatMap(str -> Arrays.asList(str.split("[ \\t\\n\\r\\f]")).iterator());
            JavaPairRDD<String, Integer> ones = words.mapToPair(word -> new Tuple2<>(word, 1));
            JavaPairRDD<String, Integer> wordCounts = ones.reduceByKey(Integer::sum);
            wordCounts.saveAsTextFile(outputPath);

            Instant end = Instant.now();

            long execTime = Duration.between(start, end).toMillis();
            totalExecTime += execTime;

            System.out.printf("%s (pass %d): %d ms%n", filename, i + 1, execTime);
        }
        System.out.printf("%s average: %f ms%n", filename, totalExecTime / (double) PASS_PER_FILE);
    }
}