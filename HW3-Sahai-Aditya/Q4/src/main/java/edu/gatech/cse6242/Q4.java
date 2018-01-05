package edu.gatech.cse6242;

import java.io.IOException;
import java.util.StringTokenizer;
import java.lang.InterruptedException;

import org.apache.hadoop.fs.*;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.util.*;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import java.io.IOException;

public class Q4 {

  public static class BreakTokens extends 
  		Mapper<Object, Text, IntWritable, IntWritable> {
  			private IntWritable minusOne = new IntWritable(-1);
  			private IntWritable plusOne = new IntWritable(1);

  			public void map(Object key, Text value, Context context)
  				throws IOException, InterruptedException {
  					StringTokenizer itr = new StringTokenizer(value.toString(), "\t");
  					// Source Node
  					if (itr.countTokens() == 2) {
	  					IntWritable sourceNode = new IntWritable(Integer.parseInt(itr.nextToken()));
	  					context.write(sourceNode, plusOne);
	  					// Target Node
	  					IntWritable targetNode = new IntWritable(Integer.parseInt(itr.nextToken()));
	  					context.write(targetNode, minusOne);
	  				}
  				}
    }

  public static class Combiner extends
  		Reducer<IntWritable, IntWritable, IntWritable, IntWritable> {
  			private IntWritable result = new IntWritable();
  			private IntWritable one = new IntWritable(1);

  			public void reduce(IntWritable nodeID, Iterable<IntWritable> values,
  						Context context) throws IOException, InterruptedException {
  				int sum = 0;
  				for (IntWritable val : values) {
  					sum += val.get();
  				}

  				result.set(sum);
  				context.write(result, one);
  			}
  	}

  public static class NodeMap extends
  		Mapper<Object, Text, IntWritable, IntWritable> {
  			private IntWritable numNodes = new IntWritable();
  			private IntWritable count = new IntWritable();
  			public void map(Object key, Text value, Context context)
  				throws IOException, InterruptedException {
  					StringTokenizer itr = new StringTokenizer(value.toString(), "\t");
  					numNodes.set(Integer.parseInt(itr.nextToken()));
  					count.set(Integer.parseInt(itr.nextToken()));
  					context.write(numNodes, count);
  				}
  	}

  public static class CountNodes extends
  		Reducer<IntWritable, IntWritable, IntWritable, IntWritable> {
  			private IntWritable result = new IntWritable();

  			public void reduce(IntWritable nodeID, Iterable<IntWritable> values,
  					Context context) throws IOException, InterruptedException {
  				int sum = 0;
  				for (IntWritable val : values) {
  					sum += val.get();
  				}

  				result.set(sum);
  				context.write(nodeID, result);
  			}
  	}

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "Q4_1");

    job.setJarByClass(edu.gatech.cse6242.Q4.class);

    // job.setNumReduceTasks(2);
    job.setMapperClass(BreakTokens.class);
    job.setReducerClass(Combiner.class);
    // job.setReducerClass(CountNodes.class);

    job.setOutputKeyClass(IntWritable.class);
    job.setOutputValueClass(IntWritable.class);

    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1] + "_temp"));
    boolean jobComplelted = job.waitForCompletion(true);
    if (jobComplelted) {
    	Configuration conf2 = new Configuration();
    	Job job2 = Job.getInstance(conf2, "Q4_2");

    	job2.setJarByClass(edu.gatech.cse6242.Q4.class);

    	job2.setMapperClass(NodeMap.class);
    	job2.setReducerClass(CountNodes.class);

    	job2.setOutputKeyClass(IntWritable.class);
    	job2.setOutputValueClass(IntWritable.class);

    	FileInputFormat.setInputDirRecursive(job2, true);

    	FileInputFormat.addInputPath(job2, new Path(args[1] + "_temp"));
    	FileOutputFormat.setOutputPath(job2, new Path(args[1]));

    	boolean job2Completed = job2.waitForCompletion(true);
      if (job2Completed) {
        // Delete temp directory
        FileSystem hdfs = FileSystem.get(conf2);
        hdfs.delete(new Path(args[1] + "_temp"), true);
      }
    }
  }
}
