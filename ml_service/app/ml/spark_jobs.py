from typing import List, Dict

from pyspark.sql import SparkSession, functions as F


def spark_generate_pairs(docs: List[Dict], negative_sampling_ratio: int, seed: int):
    """
    Returns Spark DF: query, doc_text, label, doc_id
    Databricks-ready batch pipeline style.
    """
    spark = SparkSession.builder.appName("docfleet-ml").getOrCreate()

    df_docs = spark.createDataFrame(docs)  # expects id,title,text,tags
    df_docs = df_docs.withColumn(
        "tags_str",
        F.when(F.col("tags").isNull(), F.lit("")).otherwise(F.concat_ws(" ", F.col("tags")))
    )

    pos = df_docs.select(
        (F.concat_ws(" ", F.col("title"), F.col("tags_str"))).alias("query"),
        (F.concat_ws("\n", F.col("title"), F.col("text"))).alias("doc_text"),
        F.lit(1).alias("label"),
        F.col("id").alias("doc_id"),
    )

    joined = df_docs.alias("a").crossJoin(df_docs.alias("b")).where(F.col("a.id") != F.col("b.id"))
    joined = joined.withColumn("rand", F.rand(seed))

    neg = joined.select(
        (F.concat_ws(" ", F.col("a.title"), F.col("a.tags_str"))).alias("query"),
        (F.concat_ws("\n", F.col("b.title"), F.col("b.text"))).alias("doc_text"),
        F.lit(0).alias("label"),
        F.col("b.id").alias("doc_id"),
        F.col("rand"),
    )

    from pyspark.sql.window import Window
    w = Window.partitionBy("query").orderBy(F.col("rand"))
    neg = neg.withColumn("rn", F.row_number().over(w)).where(F.col("rn") <= negative_sampling_ratio).drop("rn", "rand")

    return pos.unionByName(neg)