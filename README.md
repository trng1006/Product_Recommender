# ĐỒ ÁN: HỆ KHUYẾN NGHỊ SẢN PHẨM CHO SÀN THƯƠNG MẠI ĐIỆN TỬ

**Môn học:** Nhập môn Big Data (HUIT)  
**Đề tài 3:** Hệ Khuyến Nghị Sản Phẩm Cho Sàn Thương Mại Điện Tử  

---

## 📌 Thông tin chung
- **Khu vực nghiên cứu:** Lĩnh vực thương mại điện tử (E-commerce), tập trung vào hệ thống khuyến nghị sản phẩm và phân tích hành vi người dùng trên nền tảng bán hàng trực tuyến.
- **Phạm vi dữ liệu:** [RetailRocket Recommender System Dataset](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset/data)
- **Thời khoảng dữ liệu:** 02/05/2015 – 17/09/2015

## 🎯 Mục tiêu đồ án (Chuẩn Rubric)
1. **Lưu trữ và xử lý dữ liệu (20%):** Dùng hệ thống file phân tán Hadoop HDFS và Apache Spark RDD/DataFrame.
2. **Mô hình/Công nghệ xử lý (25%):** Áp dụng thuật toán Lọc cộng tác (Collaborative Filtering) thông qua mô hình ALS.
3. **Trực quan hóa & Xây dựng ứng dụng (25%):** Biểu đồ EDA và Giao diện Web tương tác bằng Streamlit.
4. **Tính ứng dụng (10%):** Giải quyết bài toán E-commerce thực tế (Implicit Feedback, Cold Start).
5. **Trình bày & Phối hợp (20%):** Báo cáo chuẩn chỉ theo 2 giai đoạn và phối hợp nhóm hiệu quả.

---

## 👥 Phân công công việc (Nhóm 4 thành viên)

| Thành viên | Vai trò | Mục tiêu (Target) | Trách nhiệm chính |
| :--- | :--- | :--- | :--- |
| **Thành viên 1** | Trưởng nhóm / Kỹ sư dữ liệu | 20% điểm | Thiết lập Cluster, Hadoop HDFS. Tiền xử lý dữ liệu (ETL) bằng Spark RDD & DataFrame. Xây dựng Data Pipeline hoàn chỉnh. |
| **Thành viên 2** | Chuyên viên Phân tích | 30% điểm Báo cáo GĐ 1 | Trực quan hóa dữ liệu (EDA), phân bố giờ mua, view/cart. Viết Báo cáo cơ sở lý thuyết (GĐ 1). Xây dựng kịch bản báo cáo Business Insights. |
| **Thành viên 3** | Kỹ sư Học máy | 25% điểm Mô hình xử lý | Code thuật toán Lọc cộng tác (Spark MLlib ALS). Đánh giá RMSE, tinh chỉnh tham số (Hyperparameter tuning) trên cụm Big Data. |
| **Thành viên 4** | Kỹ sư Giao diện | 25% Ứng dụng + 10% Trình bày | Code Ứng dụng Demo (Streamlit/Gradio) hiển thị sản phẩm gợi ý. Xử lý logic khởi đầu lạnh (Cold-start). Viết báo cáo GĐ 2 và Slide. |

---

## 🚀 Công nghệ sử dụng
- **Lưu trữ dữ liệu:** Hadoop HDFS
- **Xử lý Big Data:** Apache Spark (RDD, DataFrame), Spark MLlib
- **Mô hình AI:** Collaborative Filtering (ALS - Alternating Least Squares)
- **Giao diện Web:** Streamlit
- **Ngôn ngữ:** Python

---

## 📑 Cấu trúc báo cáo cuối kỳ
1. **CHƯƠNG 1:** TỔNG QUAN (Vấn đề TMĐT, RetailRocket Dataset).
2. **CHƯƠNG 2:** KỸ THUẬT LƯU TRỮ (Cấu trúc Cluster, Hadoop HDFS).
3. **CHƯƠNG 3:** XỬ LÝ DỮ LIỆU LỚN VỚI APACHE SPARK (Tiền xử lý với RDD/DataFrame).
4. **CHƯƠNG 4:** KỸ THUẬT LỌC CỘNG TÁC (Collaborative Filtering - Áp dụng thuật toán ALS).
5. **CHƯƠNG 5:** TRỰC QUAN HÓA VÀ XÂY DỰNG ỨNG DỤNG DEMO (Biểu đồ & Giao diện Streamlit).
6. **CHƯƠNG 6:** TỔNG KẾT.

---
*README.md được tạo dựa trên bản Kế hoạch triển khai và Phân công công việc thực tế của nhóm.*
