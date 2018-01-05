package edu.gatech.cse6242;

import java.io.IOException;
import java.util.StringTokenizer;
import java.lang.InterruptedException;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.util.*;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class Q1 {

  public static class BreakTokens extends Mapper<Object, Text, Text, IntWritable>{
            private Text nodeID = new Text();

            public void map(Object key, Text value, Context context)
                    throws IOException, InterruptedException {
                StringTokenizer itr = new StringTokenizer(value.toString(), "\t");
                // Waste the first value
                itr.nextToken();
                // Set key value as node ID
                nodeID.set(itr.nextToken());
                // Set weight
                int weight = Integer.parseInt(itr.nextToken());
                context.write(nodeID, new IntWritable(weight));
        }
  }  

  public static class MinReducer
        extends Reducer<Text,IntWritable,Text,IntWritable> {
    private IntWritable result = new IntWritable();

    public void reduce(Text nodeID, Iterable<IntWritable> values,
                    Context context) throws IOException, InterruptedException {
        int min = 0;
        int flag = 0;
        for (IntWritable val : values) {
            if (flag == 0) {
                // First value being encountered for this node
                min = val.get();
                flag = 1;
            } else {
                if (min > val.get()) {
                    min = val.get();
                }
            }
        }
        result.set(min);
        context.write(nodeID, result);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "Q1");

    job.setJarByClass(edu.gatech.cse6242.Q1.class);


    job.setMapperClass(BreakTokens.class);
    // job.setCombinerClass(MinReducer.class);
    job.setReducerClass(MinReducer.class);
    
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
