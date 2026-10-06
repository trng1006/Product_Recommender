from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, sum as _sum

def main():
    # 1. Khởi tạo Spark Session
    spark = SparkSession.builder \
        .appName("RetailRocket_ETL") \
        .getOrCreate()

    print("--- [1] ĐANG ĐỌC DỮ LIỆU TỪ HDFS ---")
    # Đọc dữ liệu ban đầu từ HDFS
    events_df = spark.read.csv("hdfs://namenode:9000/data/raw/events.csv", header=True, inferSchema=True)
    
    # 2. Làm sạch dữ liệu (Tiền xử lý)
    print("--- [2] TIẾN HÀNH LÀM SẠCH ---")
    # Bỏ các dòng trùng lặp
    events_clean = events_df.dropDuplicates()
    
    # Lọc bỏ các dòng bị null ở các trường quan trọng (visitorid, itemid, event)
    events_clean = events_clean.dropna(subset=["visitorid", "itemid", "event"])
    
    # 3. Chuyển đổi dữ liệu (Feature Engineering)
    # Quy đổi hành vi: view = 1, addtocart = 2, transaction = 3
    print("--- [3] QUY ĐỔI HÀNH VI (IMPLICIT FEEDBACK) ---")
    events_scored = events_clean.withColumn(
        "score",
        when(col("event") == "view", 1)
        .when(col("event") == "addtocart", 2)
        .when(col("event") == "transaction", 3)
        .otherwise(0)
    )
    
    # 4. Xây dựng User-Item Interaction Matrix
    # Một user có thể thao tác nhiều lần trên 1 item -> ta tính tổng điểm tương tác
    print("--- [4] XÂY DỰNG MA TRẬN TƯƠNG TÁC ---")
    interaction_df = events_scored.groupBy("visitorid", "itemid") \
        .agg(_sum("score").alias("rating"))
    
    # 5. Lưu kết quả ra file trên HDFS
    out_path = "hdfs://namenode:9000/data/processed/als_implicit_ratings.parquet"
    print(f"--- [5] LƯU DỮ LIỆU RA: {out_path} ---")
    # Lưu dưới định dạng Parquet để tối ưu tốc độ đọc khi đưa vào Model
    interaction_df.write.mode("overwrite").parquet(out_path)
    
    print("--- HOÀN THÀNH ETL ---")
    spark.stop()

if __name__ == "__main__":
    main()
