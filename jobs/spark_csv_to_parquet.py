from pyspark.sql import SparkSession
import os
from datetime import datetime, timedelta

# Tạo phiên SparkSession
import pyspark
print("Phiên bản của nó nè:")
print(pyspark.__version__)

spark = SparkSession.builder \
    .appName("Save to MinIO") \
    .config("spark.hadoop.fs.s3a.access.key", "access_key") \
    .config("spark.hadoop.fs.s3a.secret.key", "secret_key") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Đường dẫn thư mục chứa các file CSV
local_csv_folder = "/mnt/shared/data/"
s3_output_path = "s3a://anti-money-laundering/"

# Lấy danh sách tất cả file có tên theo định dạng %Y-%m-%d
for file_name in os.listdir(local_csv_folder):
    try:
        # Kiểm tra nếu tên file phù hợp định dạng ngày
        datetime.strptime(file_name.replace(".csv", ""), "%Y-%m-%d")
        file_path = os.path.join(local_csv_folder, file_name)
        
        # Đọc CSV
        df = spark.read.option("header", "true").csv(file_path)
        
        # Xuất ra Parquet vào MinIO
        output_file_name = file_name.replace(".csv", "")
        df.write.mode("overwrite").parquet(f"{s3_output_path}{output_file_name}")
        print(f"Đã xử lý: {file_name}")
        
    except ValueError:
        print(f"Bỏ qua: {file_name} (không phải định dạng ngày hợp lệ)")
