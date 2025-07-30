from pyspark.sql import SparkSession
from pyspark.sql.functions import unix_timestamp
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql.types import DoubleType, IntegerType

# --- Step 1: Spark session with MinIO configs ---
spark = SparkSession.builder \
    .appName("Train RF Model - AML") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "access_key") \
    .config("spark.hadoop.fs.s3a.secret.key", "secret_key") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.shuffle.compress", "true") \
    .config("spark.shuffle.spill.compress", "true") \
    .getOrCreate()
    # .config("spark.io.compression.codec", "lz4") \
    # .getOrCreate()

# --- Step 2: Đọc dữ liệu từ ngày 2022-09-01 đến 2022-09-14 ---
start_day = 1
end_day = 2
base_path = "s3a://anti-money-laundering"

input_paths = [
    f"{base_path}/2022-09-{str(day).zfill(2)}/*.parquet"
    for day in range(start_day, end_day + 1)
]

df = spark.read.parquet(*input_paths).coalesce(8)
df = df.withColumn("Amount Received", df["Amount Received"].cast(DoubleType()))
df = df.withColumn("Amount Paid", df["Amount Paid"].cast(DoubleType()))
df = df.withColumn("Is Laundering", df["Is Laundering"].cast(IntegerType()))
df.printSchema()

# --- Step 3: Tiền xử lý ---
# Chuyển timestamp thành số
df = df.withColumn("timestamp_unix", unix_timestamp("Timestamp"))

# Cột phân loại
categorical_cols = ["From Bank", "To Bank", "Payment Format", "Receiving Currency"]
indexers = [StringIndexer(inputCol=c, outputCol=c+"_idx", handleInvalid="keep") for c in categorical_cols]
encoders = [OneHotEncoder(inputCol=c+"_idx", outputCol=c+"_vec") for c in categorical_cols]

# Cột số
numeric_cols = ["Amount Received", "Amount Paid", "timestamp_unix"]

# Vector hóa
assembler_inputs = [c+"_vec" for c in categorical_cols] + numeric_cols
assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="features")

# Chuẩn hóa
scaler = StandardScaler(inputCol="features", outputCol="scaled_features")

# Random Forest
rf = RandomForestClassifier(
    featuresCol="scaled_features",
    labelCol="Is Laundering",
    predictionCol="prediction",
    probabilityCol="probability",
    numTrees=10
)

# Tạo pipeline
pipeline = Pipeline(stages=indexers + encoders + [assembler, scaler, rf])

# --- Step 4: Chia train/test ---
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# --- Step 5: Train model ---
model = pipeline.fit(train_data)

# --- Step 6: Đánh giá ---
predictions = model.transform(test_data)
evaluator = BinaryClassificationEvaluator(
    labelCol="Is Laundering",
    rawPredictionCol="probability",
    metricName="areaUnderROC"
)
auc = evaluator.evaluate(predictions)

print(f"AUC: {auc:.4f}")

# --- Step 7: Lưu mô hình vào MinIO (tuỳ chọn) ---
model.write().overwrite().save("s3a://anti-money-laundering/model/random_forest_model")

spark.stop()