import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.time.Instant;
import java.util.StringTokenizer;


public class WordCount {
    private static final int PASS_PER_FILE = 3;

    public static class TokenizerMapper
            extends Mapper<Object, Text, Text, IntWritable> {

        private final static IntWritable one = new IntWritable(1);
        private Text word = new Text();

        public void map(Object key, Text value, Context context
        ) throws IOException, InterruptedException {
            StringTokenizer itr = new StringTokenizer(value.toString());
            while (itr.hasMoreTokens()) {
                word.set(itr.nextToken());
                context.write(word, one);
            }
        }
    }

    public static class IntSumReducer
            extends Reducer<Text, IntWritable, Text, IntWritable> {
        private IntWritable result = new IntWritable();

        public void reduce(Text key, Iterable<IntWritable> values,
                           Context context
        ) throws IOException, InterruptedException {
            int sum = 0;
            for (IntWritable val : values) {
                sum += val.get();
            }
            result.set(sum);
            context.write(key, result);
        }
    }

    public static void queueJobForFile(Path path, Path outputBasePath, Configuration conf) {
        String filename = path.getFileName().toString();
        long totalExecTime = 0L;

        try {
            for (int i = 0; i < PASS_PER_FILE; i++) {
                Path output_path = Paths.get(outputBasePath.toString(), filename.substring(0, filename.length() - 4), String.valueOf(i));

                Job job = Job.getInstance(conf, "word count - " + filename + " - " + i);
                job.setJarByClass(WordCount.class);
                job.setMapperClass(TokenizerMapper.class);
                job.setCombinerClass(IntSumReducer.class);
                job.setReducerClass(IntSumReducer.class);
                job.setOutputKeyClass(Text.class);
                job.setOutputValueClass(IntWritable.class);
                FileInputFormat.addInputPath(job, new org.apache.hadoop.fs.Path(path.toUri()));
                FileOutputFormat.setOutputPath(job, new org.apache.hadoop.fs.Path(output_path.toUri()));

                Instant start = Instant.now();
                job.waitForCompletion(true);

                Instant end = Instant.now();
                long execTime = Duration.between(start, end).toMillis();
                totalExecTime += execTime;

                System.out.printf("%s (pass %d): %d ms%n", filename, i + 1, execTime);
            }
            System.out.printf("%s average: %f ms%n", filename, totalExecTime / (double) PASS_PER_FILE);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws Exception {
        Configuration conf = new Configuration();

        File outputBasePath = new File(args[1]);
        outputBasePath.mkdir();

        Files.walk(new File(args[0]).toPath())
                .filter(Files::isRegularFile)
                .filter(f -> f.toString().endsWith("txt"))
                .forEach(path -> queueJobForFile(path, outputBasePath.toPath(), conf));
    }
}