from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.types import IntegerType, FloatType

def main():
    # 1. Khởi tạo Spark Session
    spark = SparkSession.builder \
        .appName("RetailRocket_ALS_Model") \
        .getOrCreate()
        
    print("--- [1] ĐỌC DỮ LIỆU ĐÃ TIỀN XỬ LÝ (PARQUET) TỪ HDFS ---")
    data_path = "hdfs://namenode:9000/data/processed/als_implicit_ratings.parquet"
    data = spark.read.parquet(data_path)
    
    # Ép kiểu dữ liệu (ALS yêu cầu ID là Integer và Rating là Float)
    data = data.withColumn("visitorid", data["visitorid"].cast(IntegerType())) \
               .withColumn("itemid", data["itemid"].cast(IntegerType())) \
               .withColumn("rating", data["rating"].cast(FloatType()))
               
    print("--- [2] CHIA TẬP TRAIN & TEST ---")
    # Tỉ lệ 80% train, 20% test
    (training, test) = data.randomSplit([0.8, 0.2], seed=42)
    
    print("--- [3] CẤU HÌNH VÀ HUẤN LUYỆN MÔ HÌNH ALS ---")
    # Khởi tạo thuật toán Lọc cộng tác (Collaborative Filtering)
    # Vì đây là dữ liệu lượt click/xem/mua chứ không phải user chủ động rate sao, ta dùng implicitPrefs=True
    als = ALS(maxIter=10, 
              regParam=0.01, 
              userCol="visitorid", 
              itemCol="itemid", 
              ratingCol="rating",
              implicitPrefs=True,  
              coldStartStrategy="drop") # Bỏ qua người dùng chưa từng tương tác khi test
              
    model = als.fit(training)
    
    print("--- [4] ĐÁNH GIÁ MÔ HÌNH ---")
    predictions = model.transform(test)
    evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
    rmse = evaluator.evaluate(predictions)
    print(f">> Root-mean-square error (RMSE) = {rmse}")
    
    print("--- [5] LƯU MÔ HÌNH (Dành cho phần Giao diện) ---")
    model_path = "/spark/models/als_model_final"
    model.write().overwrite().save(model_path)
    print(f"Đã lưu mô hình tại: {model_path}")
    
    print("--- HOÀN THÀNH TRAINING ---")
    spark.stop()

if __name__ == "__main__":
    main()
