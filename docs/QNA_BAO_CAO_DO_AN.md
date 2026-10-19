# BỘ CÂU HỎI ÔN TẬP BẢO VỆ ĐỒ ÁN BIG DATA (HỆ KHUYẾN NGHỊ SẢN PHẨM)

Tài liệu này tổng hợp lại toàn bộ những câu hỏi fen đã thắc mắc trong quá trình làm đồ án, được phân loại theo từng nhóm chủ đề để fen dễ dàng ôn tập và trả lời phản biện với thầy cô.

---

## PHẦN 1: KIẾN TRÚC HỆ THỐNG (HADOOP & SPARK)

**Câu 1: Dự án này đã thực sự chạy trên Hadoop và Spark chưa? Lúc nào dùng HDFS, lúc nào dùng Spark?**
- **Trả lời:** Đồ án đã được chạy hoàn toàn trên môi trường phân tán (Docker). 
- **HDFS** được dùng ở pha tiền xử lý (chứa file gốc 1.4GB và file Parquet đã làm sạch).
- **Spark Cluster** được dùng để chạy script ETL dọn rác và chạy thuật toán AI nặng đô (ALS) sinh ra Model.

**Câu 2: Khi đã có kết quả cuối cùng (có Model) thì có dùng HDFS và Spark nữa không?**
- **Trả lời:** 
  - **HDFS thì KHÔNG:** Giai đoạn phục vụ web (Streamlit) đòi hỏi phản hồi mili-giây, nên Web app không chọc vào HDFS nữa.
  - **Spark thì CÓ:** Nhưng là chạy thư viện PySpark cục bộ (Spark Local) bên trong Streamlit để load cái Model đã lưu trên ổ cứng lên RAM, phục vụ tính toán nhân ma trận gợi ý realtime cho user.

**Câu 3: Tại sao lại dùng 1 Namenode và dữ liệu chia làm bao nhiêu block?**
- **Trả lời:** Do giới hạn tài nguyên của máy tính cá nhân, cấu hình 1 Namenode (quản lý metadata) và 1 Datanode (lưu trữ thực tế) là cấu hình giả lập phân tán tối ưu nhất. Với file `events.csv` nặng khoảng 1.4GB và kích thước block mặc định của HDFS là 128MB, hệ thống đã tự động băm file này ra thành khoảng 12 blocks để lưu trữ.

---

## PHẦN 2: TIỀN XỬ LÝ DỮ LIỆU & ĐỊNH DẠNG PARQUET (ETL)

**Câu 4: Quá trình làm sạch dữ liệu (lọc) diễn ra như thế nào?**
- **Trả lời:** Spark sử dụng thuật toán Hashing phân tán để phát hiện và xóa các dòng trùng lặp. Tiếp đó dùng hàm `dropna()` để loại bỏ các dòng bị thiếu (Null) ở các cột quan trọng như ID người dùng, ID sản phẩm.

**Câu 5: Tại sao file gốc có rất nhiều cột mà sau khi làm sạch chỉ còn đúng 3 cột `|visitorid|itemid|rating|`?**
- **Trả lời:** 
  1. Yêu cầu của thuật toán: Thuật toán ALS chỉ chấp nhận đầu vào là 3 cột số (User, Item, Rating). Không thể tính toán với chữ hay ngày tháng.
  2. Tạo ma trận: Ta quy đổi hành vi ẩn (view=1, cart=2, transaction=3) rồi cộng dồn lại thành cột `rating`. 3 cột này tạo thành "Ma trận tương tác" (User-Item Interaction Matrix) làm xương sống cho AI học "gu" khách hàng.

**Câu 6: Tại sao lại lưu kết quả xuống HDFS bằng định dạng Parquet thay vì CSV?**
- **Trả lời:** CSV lưu theo chiều ngang (đọc rất chậm). Parquet lưu theo chiều dọc (Column-based) và nén rất chặt. Khi Spark cần 3 cột để train AI, nó chỉ bốc đúng 3 cột đó lên, bỏ qua các cột thừa, giúp dung lượng giảm một nửa và tốc độ truy xuất nhanh gấp 10-50 lần so với CSV.

**Câu 7: File Parquet có phải là cái bảng được in ra trên terminal (`df.show()`) không?**
- **Trả lời:** Cái bảng trên terminal là kết quả sau khi Spark đã "giải mã" file lên RAM để con người dễ đọc. Bản chất file Parquet trên ổ cứng HDFS là các file nhị phân (binary) được nén chặt, nếu mở bằng Notepad sẽ chỉ thấy ký tự giun dế mã hóa không đọc được.

**Câu 8: Truy vấn (xem) file Parquet trên HDFS bằng cách nào?**
- **Trả lời:** Cách chuyên nghiệp nhất là chui vào Spark Master (`docker exec -it spark-master /spark/bin/pyspark`), load file lên bằng lệnh `df = spark.read.parquet(...)` rồi gọi `df.show(10)` để in bảng ra màn hình.

---

## PHẦN 3: THUẬT TOÁN AI & HUẤN LUYỆN (MODEL TRAINING)

**Câu 9: Thuật toán ALS là gì? Nó có phải thuật toán của Big Data không?**
- **Trả lời:** ALS (Alternating Least Squares) là một thuật toán Lọc cộng tác (Collaborative Filtering) sinh ra dành riêng cho Big Data, được tích hợp sẵn trong thư viện Spark MLlib để phân tích song song trên cụm nhiều máy tính. 

**Câu 10: Kết quả sau khi training là gì? Hai cái ma trận dùng để làm gì?**
- **Trả lời:** 
  - Quá trình training ALS băm bảng tương tác khổng lồ thành 2 ma trận nhỏ nhắn: Ma trận User (Đại diện cho "gu") và Ma trận Item (Đại diện cho "thuộc tính").
  - Khi cần gợi ý cho một khách, hệ thống web (Streamlit) chỉ việc đem 2 ma trận này nhân với nhau (Tích vô hướng - Dot Product). Ra được các "Điểm dự đoán". Điểm nào cao nhất thì lấy sản phẩm đó gợi ý ra màn hình.

---

## PHẦN 4: LỖI THƯỜNG GẶP (TROUBLESHOOTING)

**Câu 11: Lỗi `FileNotFoundError: /tmp/.../tmpx_o0acfp` khi ấn nút Gợi ý trên Streamlit là gì?**
- **Trả lời:** Do Streamlit cache SparkSession sống quá lâu, trong khi macOS lại có cơ chế dọn rác tự động xoá mất thư mục tạm của PySpark trong `/tmp/`. Giải pháp là cấu hình lại `.config("spark.local.dir", "./.spark_temp")` để ép Spark dùng thư mục tĩnh trong project, không cho macOS xoá nữa.

**Câu 12: Lỗi `executable file not found in $PATH` khi chạy pyspark trên Docker?**
- **Trả lời:** Do Image Spark không nạp đường dẫn pyspark vào biến môi trường. Cần phải gõ rõ đường dẫn tuyệt đối: `docker exec -it spark-master /spark/bin/pyspark`.

**Câu 13: Lỗi `IndentationError: unexpected indent` khi dán code vào PySpark?**
- **Trả lời:** Do khi copy dán bị dư các dấu cách (space) ở đầu dòng. Ngôn ngữ Python rất nhạy cảm với khoảng trắng ở đầu dòng. Cần gõ lệnh sát lề trái.

--- 
*Tài liệu được tổng hợp bởi AI hỗ trợ đồ án - Chúc fen bảo vệ điểm A!*
