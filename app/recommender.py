import pandas as pd
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType
import os

# Khởi tạo Spark Session cho UI
# Dùng cấu hình local
spark = SparkSession.builder \
    .appName("RetailRocket_UI") \
    .master("local[*]") \
    .getOrCreate()

# Load model (nên dùng cache hoặc chạy 1 lần để tránh UI bị đơ mỗi lần load)
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "als_model_final")
try:
    als_model = ALSModel.load(MODEL_PATH)
except:
    als_model = None
    print(f"Không tìm thấy model tại {MODEL_PATH}. Vui lòng chạy training pipeline trước.")

# Load danh sách top sản phẩm (Spark SQL đã chạy)
TOP_PRODUCTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "top_products_dir")

# Tạo danh sách các mặt hàng phổ biến tĩnh nếu chưa có data (Cold start)
def get_popular_products():
    """
    FALLBACK (COLD START): Gợi ý sản phẩm phổ biến nhất cho người dùng mới.
    """
    try:
        # Tìm file .csv thực sự nằm trong thư mục
        csv_file = None
        for file in os.listdir(TOP_PRODUCTS_DIR):
            if file.endswith(".csv"):
                csv_file = os.path.join(TOP_PRODUCTS_DIR, file)
                break
                
        if csv_file:
            df = pd.read_csv(csv_file)
            df = df.rename(columns={"itemid": "item_id"})
            # Thêm mock name và score cho UI
            df['name'] = df['item_id'].apply(lambda x: f"Sản phẩm Trending #{x}")
            df['score'] = [round(5.0 - (i * 0.1), 1) for i in range(len(df))]
            
            # Giới hạn lấy 4 sản phẩm để hiển thị cho gọn
            return df.head(4)[["item_id", "name", "score"]]
    except:
        pass
        
    # Nếu chưa chạy Bước 5 thì trả về dữ liệu mock
    return pd.DataFrame({
        "item_id": [461686, 119736, 213834, 312728],
        "name": ["Sản phẩm Hot 461686", "Sản phẩm Bán chạy 119736", "Sản phẩm 213834", "Sản phẩm 312728"],
        "score": [5.0, 4.9, 4.8, 4.8]
    })

def check_new_user(user_id):
    """
    Kiểm tra xem user_id có tồn tại trong tập dữ liệu train chưa.
    Ở đây ta tạm thời dùng quy tắc chẵn/lẻ hoặc nếu user chưa được dự đoán.
    """
    # Mô hình ALS nếu đẩy user ID không tồn tại sẽ trả về rỗng, ta có thể bắt ở đó.
    # Để test UI: số chẵn là user cũ, số lẻ là user mới.
    return user_id % 2 != 0

def get_recommendations(user_id):
    """
    Lấy danh sách gợi ý cho user đã có lịch sử dựa trên mô hình ALS.
    """
    if als_model is None:
        return get_popular_products()
        
    # Tạo dataframe chứa user
    user_df = spark.createDataFrame([(user_id,)], ["visitorid"])
    user_df = user_df.withColumn("visitorid", col("visitorid").cast(IntegerType()))
    
    # Dự đoán (trả về array các recomendations)
    try:
        user_recs = als_model.recommendForUserSubset(user_df, 4)
        recs_pandas = user_recs.toPandas()
        
        if recs_pandas.empty or len(recs_pandas['recommendations'][0]) == 0:
            return get_popular_products()
            
        items = recs_pandas['recommendations'][0]
        rec_list = []
        for row in items:
            rec_list.append({
                "item_id": row.itemid,
                "name": f"Sản phẩm #{row.itemid}",
                "score": round(row.rating, 1) if row.rating <= 5 else 5.0
            })
            
        return pd.DataFrame(rec_list)
    except Exception as e:
        print(f"Lỗi khi dự đoán: {e}")
        return get_popular_products()
