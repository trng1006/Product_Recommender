from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("RetailRocket_SparkSQL_TopProducts") \
        .getOrCreate()
        
    print("--- [1] ĐỌC DỮ LIỆU TỪ HDFS ---")
    events_df = spark.read.csv("hdfs://namenode:9000/data/raw/events.csv", header=True, inferSchema=True)
        
    print("--- [2] SỬ DỤNG SPARK SQL ĐỂ TÌM TOP SẢN PHẨM ---")
    # Đăng ký DataFrame thành một bảng SQL ảo (Temporary View)
    events_df.createOrReplaceTempView("events_table")
    
    # Viết câu lệnh SQL thuần túy (Thỏa mãn yêu cầu Bước 5)
    # Tìm top 10 sản phẩm có tổng số lượt tương tác (view/addtocart/transaction) nhiều nhất
    sql_query = """
        SELECT 
            itemid, 
            COUNT(event) as total_interactions
        FROM events_table
        GROUP BY itemid
        ORDER BY total_interactions DESC
        LIMIT 10
    """
    
    top_products_df = spark.sql(sql_query)
    
    # Hiển thị kết quả ra console
    top_products_df.show()
    
    print("--- [3] LƯU KẾT QUẢ CHO GIAO DIỆN STREAMLIT ---")
    out_path = "/spark/models/top_products_dir"
    
    # Spark ghi file sẽ ra dạng thư mục. Mình gộp thành 1 file duy nhất
    top_products_df.coalesce(1).write.mode("overwrite").csv(out_path, header=True)
    print(f"Đã lưu danh sách Top Sản phẩm tại thư mục: {out_path}")
    
    spark.stop()

if __name__ == "__main__":
    main()
