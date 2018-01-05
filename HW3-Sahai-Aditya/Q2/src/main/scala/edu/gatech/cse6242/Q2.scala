package edu.gatech.cse6242

import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.SparkConf
import org.apache.spark.sql.SQLContext
import org.apache.spark.sql.functions._

object Q2 {

    case class Node(source: Int, target: Int, weight: Int)

    def main(args: Array[String]) {
        val sc = new SparkContext(new SparkConf().setAppName("Q2"))
        val sqlContext = new SQLContext(sc)
        import sqlContext.implicits._

        // read the file
        val file = sc.textFile("hdfs://localhost:8020" + args(0))

        val link = file.map(_.split("\t")).map(p => Node(p(0).trim.toInt, p(1).trim.toInt, p(2).trim.toInt)).toDF()
        val filtered = link.filter("weight > 5")
        val outgoing_w = filtered.groupBy("source").agg(sum("weight").alias("outgoing"))
        val incoming_w = filtered.groupBy("target").agg(sum("weight").alias("incoming"))
        val new_tab = incoming_w.join(outgoing_w, incoming_w("target") === outgoing_w("source")).withColumn("diff", incoming_w("incoming") - outgoing_w("outgoing"))
        val ans = new_tab.select(new_tab("source"), new_tab("diff"))
        ans.map(x => x.mkString("\t")).saveAsTextFile("hdfs://localhost:8020" + args(1))
    }
}
