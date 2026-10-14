import streamlit as st
import pandas as pd
import os
import shutil

# --- SỬA LỖI MACOS XOÁ FILE TẠM CỦA PYSPARK ---
# Ép Python và PySpark dùng thư mục .spark_temp của project thay vì /tmp/ của Mac
temp_path = os.path.abspath("./.spark_temp")
os.makedirs(temp_path, exist_ok=True)
os.environ["TMPDIR"] = temp_path
os.environ["SPARK_LOCAL_DIRS"] = temp_path

from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="RetailRocket Recommender", page_icon="🛒", layout="wide")
st.title("🛒 Hệ Khuyến Nghị Sản Phẩm - Đồ Án Big Data")
st.markdown("Hệ thống gợi ý sản phẩm dựa trên **Lọc cộng tác (ALS)** được huấn luyện bằng **Apache Spark**.")

@st.cache_resource
def init_spark():
    # Khởi tạo Spark Session cục bộ cho Web UI
    spark = SparkSession.builder \
        .appName("Streamlit_Recommender") \
        .config("spark.driver.memory", "2g") \
        .config("spark.local.dir", temp_path) \
        .getOrCreate()
    return spark

@st.cache_resource
def load_model(_spark):
    model_path = "models/als_model"
    if os.path.exists(model_path):
        return ALSModel.load(model_path)
    return None

def main():
    spark = init_spark()
    model = load_model(spark)
    
    # Giao diện chính chia làm nhiều Tab
    tab1, tab2, tab3 = st.tabs(["🛒 Hệ Khuyến Nghị (ALS)", "📊 Thống Kê Dữ Liệu (EDA)", "⚙️ Thông Tin Mô Hình"])
    
    with tab1:
        st.markdown("### Tìm kiếm & Đề xuất Sản phẩm")
        if model is None:
            st.error("⚠️ Chưa tìm thấy mô hình ALS. Vui lòng chạy script huấn luyện trước!")
            return
            
        st.sidebar.header("🔍 Cấu hình Gợi ý")
        user_id = st.sidebar.number_input("Nhập User ID (VD: 147545, 12345):", min_value=0, value=147545)
        num_recs = st.sidebar.slider("Số lượng gợi ý:", min_value=1, max_value=12, value=4)
        
        if st.sidebar.button("Phân tích & Gợi ý 🚀", type="primary"):
            with st.spinner("Đang tính toán ma trận gợi ý bằng Spark..."):
                user_df = spark.createDataFrame([(user_id,)], ["visitorid"])
                recommendations = model.recommendForUserSubset(user_df, num_recs)
                
                if recommendations.count() == 0:
                    st.warning(f"Không có gợi ý nào cho User ID {user_id}. (Người dùng mới - Cold Start).")
                else:
                    st.success(f"Đã tìm thấy các sản phẩm phù hợp nhất cho Khách hàng **{user_id}**!")
                    recs_row = recommendations.first()
                    
                    if recs_row and recs_row.recommendations:
                        items = [row.itemid for row in recs_row.recommendations]
                        scores = [round(row.rating, 4) for row in recs_row.recommendations]
                        
                        # --- Hiển thị dạng Card / Cột ---
                        st.markdown("#### 🎁 Các sản phẩm đề xuất hàng đầu:")
                        cols = st.columns(len(items))
                        
                        for i, col in enumerate(cols):
                            with col:
                                # Tạo một hình ảnh giả lập (Placeholder) cho đẹp mắt
                                st.image(f"https://picsum.photos/seed/{items[i]}/200/200", use_container_width=True)
                                st.markdown(f"**Mã SP:** `{items[i]}`")
                                st.metric(label="Độ phù hợp", value=scores[i])
                                
                        # --- Hiển thị Biểu đồ trực quan ---
                        st.markdown("---")
                        st.markdown("#### 📈 Mức độ quan tâm (Latent Score)")
                        df_chart = pd.DataFrame({"Điểm phù hợp": scores}, index=[f"SP {i}" for i in items])
                        st.bar_chart(df_chart, color="#ff4b4b")
                        
    with tab2:
        st.markdown("### 📊 Tổng quan Tập Dữ liệu (RetailRocket)")
        st.info("Phân tích dữ liệu Khách hàng & Hành vi (Exploratory Data Analysis)")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Tổng lượt tương tác", "2,756,101", "+1.2%")
        col2.metric("Số lượng Khách hàng", "1,407,580", "")
        col3.metric("Số lượng Sản phẩm", "235,061", "")
        
        st.markdown("#### Tỷ lệ Hành vi Khách hàng")
        # Biểu đồ mô phỏng tỷ lệ View/Cart/Transaction
        chart_data = pd.DataFrame(
            {"Số lượng": [2664312, 69332, 22457]},
            index=["Xem (View)", "Thêm Giỏ (Cart)", "Mua (Transaction)"]
        )
        st.bar_chart(chart_data, color="#29b5e8")

    with tab3:
        st.markdown("### ⚙️ Kiến trúc Hệ thống Big Data")
        st.markdown("""
        - **Data Storage:** Hadoop HDFS (Namenode & Datanode)
        - **Data Processing:** Apache Spark (Master & Worker)
        - **Algorithm:** Collaborative Filtering (Alternating Least Squares - ALS)
        - **Web Framework:** Streamlit
        - **RMSE Score:** ~ `0.021` (Độ đo sai số của mô hình)
        """)
        st.success("Hệ thống được Container hóa 100% bằng Docker.")

if __name__ == "__main__":
    main()
