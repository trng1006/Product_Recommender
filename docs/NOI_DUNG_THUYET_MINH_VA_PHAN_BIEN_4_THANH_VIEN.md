# NỘI DUNG THUYẾT MINH & BỘ CÂU HỎI PHẢN BIỆN CHO 4 THÀNH VIÊN
**Đồ án:** Hệ Khuyến Nghị Sản Phẩm Dựa Trên Apache Spark & Hadoop HDFS  
**Học phần:** Nhập môn Big Data (Mã HP: 01200057 - HUIT)  

---

## THÀNH VIÊN 1: HẠ TẦNG PHÂN TÁN HADOOP HDFS
> **Mục tiêu:** Chứng minh hệ thống được lưu trữ phân tán thực thụ, hiểu rõ cơ chế quản lý file lớn của HDFS.

### 1. Nhiệm vụ trong bài báo cáo & Thuyết minh:
1. **Giới thiệu bài toán dữ liệu lớn:**
   - Đặc tính 3V của tập dữ liệu RetailRocket: Volume (1.4 GB log clickstream), Variety (log sự kiện json/csv), Velocity (tương tác thời gian thực của người dùng).
2. **Kiến trúc Master-Worker của Hadoop HDFS:**
   - **NameNode:** Quản lý không gian tên (Namespace), cây thư mục, lưu trữ metadata trong bộ nhớ RAM, ghi nhận nhật ký giao dịch qua `FsImage` và `EditLog`. Tuyệt đối không lưu dữ liệu thô!
   - **DataNodes:** Lưu trữ các khối dữ liệu thực tế (Blocks) trên ổ đĩa vật lý, định kỳ gửi tín hiệu sống Heartbeat (3 giây/lần) và Block Report về NameNode.
3. **Cơ chế phân khối dữ liệu (Block Management):**
   - Kích thước block mặc định: 128 MB.
   - File `events.csv` nặng 1.4 GB được NameNode băm thành 12 khối logic ($1.4 \text{ GB} / 128 \text{ MB} \approx 12 \text{ blocks}$).
   - Cấu hình hệ số nhân bản `dfs.replication = 2`: Tổng cộng có 24 khối vật lý được phân bổ xen kẽ trên DataNode 1 và DataNode 2.
4. **Quá trình Ghi dữ liệu phân tán (HDFS Write Pipeline):**
   - Client gửi yêu cầu ghi tới NameNode $\rightarrow$ NameNode kiểm tra quyền và cấp danh sách DataNodes phù hợp $\rightarrow$ Client mở luồng ghi (stream) dữ liệu đến DataNode 1 $\rightarrow$ DataNode 1 tự động nhân bản (pipeline) sang DataNode 2.

### 2. Bộ câu hỏi phản biện giáo viên hay hỏi & Câu trả lời chuẩn:
* **Hỏi:** *Tại sao lại chọn Block size 128MB mà không phải 4KB như hệ điều hành thông thường?*
  * **Trả lời:** Trong Big Data, block size lớn (128MB hoặc 256MB) nhằm giảm thiểu thời gian tìm kiếm đầu đọc (Seek Time) của ổ đĩa vật lý, tối ưu hóa tốc độ truyền tuần tự (Transfer Rate). Ngoài ra, block lớn giúp giảm số lượng bản ghi chỉ mục metadata mà NameNode phải lưu trữ trên RAM, tránh nghẽn bộ nhớ NameNode khi số lượng file tăng lên hàng triệu.
* **Hỏi:** *Nếu 1 DataNode bị sập (down) giữa chừng thì dữ liệu có bị mất không? Hệ thống xử lý thế nào?*
  * **Trả lời:** Không bị mất dữ liệu vì hệ thống đã cấu hình `Replication Factor = 2`. Khi DataNode 1 ngừng gửi Heartbeat sau khoảng 10 phút, NameNode xác định node này đã chết và tự động ra lệnh cho DataNode 2 sao chép các block còn lại sang node hoạt động khác để đảm bảo duy trì đủ hệ số bản sao.

---

## THÀNH VIÊN 2: XỬ LÝ DỮ LIỆU PHÂN TÁN VÀ SPARK ETL
> **Mục tiêu:** Làm chủ tư duy tính toán phân tán trong bộ nhớ (In-Memory), cơ chế Transformations và Shuffle.

### 1. Nhiệm vụ trong bài báo cáo & Thuyết minh:
1. **Kiến trúc tính toán của Apache Spark:**
   - Spark Driver, Spark Master, Spark Worker, Executor, Cores/Slots và cơ chế phân phối Task.
2. **Phân biệt Narrow Transformation và Wide Transformation:**
   - **Narrow:** `dropna()`, quy đổi điểm bằng `withColumn()` $\rightarrow$ Thực thi trực tiếp trên RAM của từng Worker, không phát sinh giao tiếp mạng giữa các node.
   - **Wide:** `dropDuplicates()`, `groupBy("visitorid", "itemid").agg()` $\rightarrow$ Buộc các Workers phải trao đổi phân vùng dữ liệu qua mạng vật lý (Shuffle Operation).
3. **Feature Engineering cho hành vi ẩn (Implicit Feedback):**
   - Không thể dùng thang điểm đánh giá 1-5 sao vì người dùng TMĐT chỉ để lại hành vi lướt web.
   - Quy đổi trọng số tin cậy: View = 1 điểm, Add to Cart = 2 điểm, Transaction (Mua hàng) = 3 điểm.
4. **Tối ưu hóa lưu trữ với định dạng Apache Parquet:**
   - Cấu trúc lưu trữ theo cột (Columnar Storage) thay vì theo dòng (Row-based) của CSV.
   - Nén Snappy: Tiết kiệm I/O đĩa cứng, nén file từ 1.4 GB xuống còn ~70 MB.
   - Hỗ trợ *Column Pruning* (chỉ đọc đúng các cột cần thiết) và *Predicate Pushdown* (lọc điều kiện ngay tại tầng storage trước khi kéo lên RAM).

### 2. Bộ câu hỏi phản biện giáo viên hay hỏi & Câu trả lời chuẩn:
* **Hỏi:** *Shuffle trong Spark là gì và tại sao phép toán GroupBy lại gây tốn chi phí nhất trong script ETL?*
  * **Trả lời:** Shuffle là quá trình phân phối lại dữ liệu giữa các phân vùng (partitions) trên toàn bộ các Worker node qua mạng máy tính. Khi thực hiện `groupBy("visitorid", "itemid")`, các dòng dữ liệu có cùng ID có thể đang nằm ở Worker 1 và Worker 2 khác nhau. Spark buộc phải ghi dữ liệu tạm ra đĩa, truyền qua mạng và gom về đúng Executor phụ trách khóa đó, gây nghẽn I/O đĩa và băng thông mạng.
* **Hỏi:** *Lazy Evaluation trong Spark hoạt động như thế nào trong script ETL của nhóm?*
  * **Trả lời:** Khi gọi các hàm như `.withColumn()`, `.dropna()`, `.groupBy()`, Spark không hề tính toán ngay mà chỉ ghi nhận kế hoạch thực thi vào đồ thị có hướng DAG (Lineage Graph). Chỉ đến khi gặp một **Action** cụ thể (ở đây là `.write.parquet(...)`), Spark Catalyst Optimizer mới tối ưu hóa toàn bộ chuỗi biến đổi và kích hoạt các Executors thực thi thực sự.

---

## THÀNH VIÊN 3: HỌC MÁY PHÂN TÁN (SPARK MLLIB) & THUẬT TOÁN ALS
> **Mục tiêu:** Nắm chắc bản chất toán học của Matrix Factorization, cơ chế giải song song trên Spark Cluster.

### 1. Nhiệm vụ trong bài báo cáo & Thuyết minh:
1. **Bài toán Hệ Khuyến Nghị & Ma trận thưa (Sparse Matrix):**
   - Ma trận tương tác $R$ có kích thước $1,407,580 \text{ Users} \times 235,061 \text{ Items}$.
   - Độ thưa (Sparsity) > 99.9% (mỗi khách hàng chỉ tương tác với số ít sản phẩm).
2. **Kỹ thuật Phân rã ma trận (Matrix Factorization):**
   - Giả định sở thích của User và đặc tính của Item được biểu diễn qua $k$ chiều không gian ẩn (Latent Factors, cấu hình $k = 10$).
   - Xấp xỉ ma trận: $R \approx U \times V^T$, với $U \in \mathbb{R}^{m \times k}$ và $V \in \mathbb{R}^{n \times k}$.
3. **Thuật toán Alternating Least Squares (ALS) với Implicit Feedback:**
   - Nhận thức: Tần suất tương tác $r_{ui}$ biểu thị độ tin cậy ($c_{ui} = 1 + \alpha r_{ui}$), còn sở thích nhị phân $p_{ui} = 1$ nếu $r_{ui} > 0$, ngược lại $p_{ui} = 0$.
   - Hàm mất mát:
     $$\mathcal{L} = \sum_{u, i} c_{ui} (p_{ui} - u_u^T v_i)^2 + \lambda \left( \sum_u \|u_u\|_2^2 + \sum_i \|v_i\|_2^2 \right)$$
   - Cơ chế luân phiên (Alternating): Do hàm phi tuyến với cả $U$ và $V$, thuật toán cố định $V$ để giải hệ phương trình bình phương tối thiểu tuyến tính tìm $U$ tối ưu, sau đó cố định $U$ để giải tìm $V$. Lặp lại 10 vòng lặp (maxIter=10).
4. **Đánh giá mô hình & Siêu tham số:**
   - `rank`: Số chiều đặc trưng ẩn (10 chiều).
   - `maxIter`: Số vòng lặp hội tụ (10 vòng, RMSE đạt ~0.021).
   - `regParam`: Hệ số phạt chuẩn hóa $L_2$ ($\lambda = 0.01$) để tránh Overfitting.

### 2. Bộ câu hỏi phản biện giáo viên hay hỏi & Câu trả lời chuẩn:
* **Hỏi:** *Tại sao lại dùng thuật toán ALS của Spark MLlib mà không dùng Gradient Descent (SGD)?*
  * **Trả lời:** SGD cập nhật từng bước một, rất khó song song hóa hiệu quả trên cụm nhiều máy tính vì các worker phải liên tục đồng bộ trọng số. Ngược lại, trong ALS, khi cố định $V$, việc giải tối ưu cho từng vector người dùng $u_u$ hoàn toàn độc lập với nhau, cho phép Spark chia nhỏ hàng triệu User thành các Partition và tính toán song song tuyệt đối trên các Worker mà không cần chờ đợi nhau.
* **Hỏi:** *Mô hình của nhóm dùng Implicit Feedback thì chỉ số RMSE có ý nghĩa chính xác như Explicit Feedback (chấm sao) không?*
  * **Trả lời:** Trong Implicit Feedback, giá trị dự đoán không phải là điểm sao từ 1 đến 5 mà là mức độ tin cậy ưu tiên của người dùng đối với món hàng (preference confidence). Chỉ số RMSE ở đây đo lường mức độ hội tụ của hàm mất mát qua các vòng lặp. Để đánh giá chất lượng gợi ý thực tế trên sàn TMĐT, nhóm sử dụng thêm phương pháp đánh giá Top-K Recommendation.

---

## THÀNH VIÊN 4: SERVING, COLD-START & BENCHMARK HIỆU NĂNG
> **Mục tiêu:** Đo đạc thực nghiệm định lượng, giải quyết bài toán khởi động lạnh và kết nối luồng giá trị của Big Data.

### 1. Nhiệm vụ trong bài báo cáo & Thuyết minh:
1. **Giải quyết bài toán Cold-Start (Khởi động lạnh):**
   - Khi một người dùng mới tinh xuất hiện, mô hình ALS không có vector ẩn $u_u$ để nhân ma trận.
   - Giải pháp Hybrid: Sử dụng Spark SQL (`01b_spark_sql_top_products.py`) tổng hợp Top 10 sản phẩm thịnh hành nhất toàn sàn để gợi ý mặc định (Popularity-based fallback).
2. **Cơ chế Serving (Inference Architecture):**
   - Phân định rõ ràng: **Offline Training** (chạy hàng loạt trên Spark Cluster, mất vài phút) vs **Online Serving** (tính tích vô hướng Dot Product $u_u \cdot v_i$ trong mili-giây trên Streamlit).
3. **Thực nghiệm Đo đạc Hiệu năng Big Data (`03_benchmark.py`):**
   - **Benchmark 1 (Lưu trữ):** So sánh dung lượng CSV (1.4 GB) vs Parquet Snappy (~70 MB - giảm >90%).
   - **Benchmark 2 (Tốc độ nạp):** Đo thời gian đọc Spark CSV vs Parquet (Parquet nhanh hơn rõ rệt nhờ Columnar Scan).
   - **Benchmark 3 (Phân tích Spark UI):** Đưa ảnh chụp Spark Web UI (Port 8080/4040) vào báo cáo: Giải thích đồ thị DAG, số lượng Stages, số lượng Tasks phân bổ trên 2 Workers, lượng dữ liệu Shuffle Read/Write.

### 2. Bộ câu hỏi phản biện giáo viên hay hỏi & Câu trả lời chuẩn:
* **Hỏi:** *Tại sao khi làm giao diện web Streamlit, nhóm không cho web chọc thẳng vào HDFS để đọc dữ liệu?*
  * **Trả lời:** Vì HDFS và Spark được thiết kế cho xử lý khối lượng lớn theo lô (Batch Processing - High Throughput), độ trễ phản hồi tính bằng giây hoặc phút. Giao diện người dùng yêu cầu độ trễ phản hồi thấp (Low Latency - vài mili-giây). Do đó, mô hình và danh sách Top sản phẩm sau khi train trên Spark được trích xuất ra lưu trữ phục vụ (Serving Layer) để Web App suy diễn nhanh bằng tích vô hướng mà không làm nghẽn cụm HDFS.
* **Hỏi:** *Trong Spark UI, làm sao em biết một Job đã được phân tán trên cả 2 Worker?*
  * **Trả lời:** Trên Spark Master Web UI (cổng 8080), trong mục Application Detail, ta quan sát thấy 2 Executor ID tương ứng với 2 IP của `spark-worker` và `spark-worker-2`. Trong tab Stage Details (cổng 4040), danh sách Tasks được chia đều vào 2 Executors này và cả 2 đều ghi nhận thời gian tính toán CPU cũng như lượng Shuffle Data trao đổi qua lại.
