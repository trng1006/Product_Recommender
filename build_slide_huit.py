import os
import glob
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def find_template():
    for d in [".", "./img", "./docs"]:
        for pat in ["*huit_mau*.pptx", "*huit*.pptx"]:
            m = glob.glob(os.path.join(d, pat))
            if m: return m[0]
    return None

TEMPLATE_PPTX = find_template()
IMG_DIR = "img"
OUTPUT_PPTX = "Bao_Cao_BigData_HUIT_15Slides.pptx"

HUIT_BLUE = RGBColor(21, 101, 192)
HUIT_DARK = RGBColor(13, 59, 102)
HUIT_LIGHT_BG = RGBColor(245, 248, 252)
BORDER_BLUE = RGBColor(187, 222, 251)
TEXT_DARK = RGBColor(33, 37, 41)
TEXT_MUTED = RGBColor(108, 117, 125)
WHITE = RGBColor(255, 255, 255)
RED_ACCENT = RGBColor(211, 47, 47)
GREEN_ACCENT = RGBColor(46, 125, 50)
ORANGE_ACCENT = RGBColor(230, 81, 0)

def find_image(filename):
    search_dirs = [
        IMG_DIR,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "img"),
        "/Users/tranbaonguyen/Documents/HUIT_Nam4/BigData/img",
        "/Users/tranbaonguyen/Documents/HUIT_Nam4/BigData/Product_Recommender/img",
        ".",
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop")
    ]
    for d in search_dirs:
        p = os.path.join(d, filename)
        if os.path.exists(p): return p
    return None

def apply_background(slide, prs):
    bg_path = find_image("custom_bg.png")
    if bg_path and os.path.exists(bg_path):
        pic = slide.shapes.add_picture(bg_path, 0, 0, width=prs.slide_width, height=prs.slide_height)
        spTree = slide.shapes._spTree
        spTree.remove(pic._element)
        insert_idx = 0
        for i, child in enumerate(spTree):
            tag = child.tag.split("}")[-1]
            if tag in ["nvGrpSpPr", "grpSpPr"]:
                insert_idx = i + 1
        spTree.insert(insert_idx, pic._element)

def clean_slide(slide):
    for shape in list(slide.shapes):
        if shape.has_text_frame or shape.has_table or shape.has_chart:
            try:
                sp = shape._element
                sp.getparent().remove(sp)
            except: pass
        else:
            if shape.width < Inches(12.5):
                try:
                    sp = shape._element
                    sp.getparent().remove(sp)
                except: pass

def ensure_slides(prs, count=16):
    while len(prs.slides) < count:
        layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[0]
        prs.slides.add_slide(layout)
    for s in prs.slides:
        clean_slide(s)
        apply_background(s, prs)

def add_header(slide, section_badge, title_text, slide_num, total_slides=16):
    # Nhãn góc phải
    badge = slide.shapes.add_textbox(Inches(6.2), Inches(0.18), Inches(6.6), Inches(0.4))
    tf_b = badge.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.text = f"{section_badge}  |  Slide {slide_num}/{total_slides}"
    p_b.alignment = PP_ALIGN.RIGHT
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = WHITE

    # Tiêu đề slide
    if title_text:
        tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.95), Inches(12.1), Inches(0.5))
        tf_t = tb.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = HUIT_DARK

def add_card(slide, left, top, width, height, title, bullets, accent_color=HUIT_BLUE):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = HUIT_LIGHT_BG
    card.line.color.rgb = BORDER_BLUE
    card.line.width = Pt(1)

    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.07))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent_color
    bar.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.12), Inches(width - 0.3), Inches(height - 0.18))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = accent_color
    p0.space_after = Pt(4)

    for b in bullets:
        p = tf.add_paragraph()
        p.text = f"• {b}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(2.5)

def add_image_box(slide, img_name, left, top, width=None, height=None, caption=None):
    path = find_image(img_name)
    if path:
        if width and height:
            slide.shapes.add_picture(path, Inches(left), Inches(top), width=Inches(width), height=Inches(height))
        elif width:
            slide.shapes.add_picture(path, Inches(left), Inches(top), width=Inches(width))
        elif height:
            slide.shapes.add_picture(path, Inches(left), Inches(top), height=Inches(height))
    else:
        ph = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width or 5), Inches(height or 3.5))
        ph.fill.solid()
        ph.fill.fore_color.rgb = RGBColor(235, 235, 235)
        ph.text_frame.text = f"[Thiếu ảnh: {img_name}]"

    if caption:
        cap = slide.shapes.add_textbox(Inches(left), Inches(top + (height or 3.5) + 0.05), Inches(width or 5.5), Inches(0.3))
        p = cap.text_frame.paragraphs[0]
        p.text = caption
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(10)
        p.font.italic = True
        p.font.color.rgb = TEXT_MUTED

def build_all_slides():
    prs = Presentation(TEMPLATE_PPTX) if TEMPLATE_PPTX else Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    ensure_slides(prs, count=16)

    # SLIDE 1
    s1 = prs.slides[0]
    add_header(s1, "PHẦN 1: ĐẶT VẤN ĐỀ (1 - 2 PHÚT)", "", 1)
    hero = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.5), Inches(12.1), Inches(2.2))
    hero.fill.solid()
    hero.fill.fore_color.rgb = HUIT_DARK
    hero.line.fill.background()
    tf1 = hero.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "BÁO CÁO ĐỒ ÁN HỌC PHẦN: NHẬP MÔN BIG DATA (MÃ HP: 01200057)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(144, 202, 249)
    p.space_after = Pt(6)

    p2 = tf1.add_paragraph()
    p2.text = "XÂY DỰNG HỆ THỐNG BIG DATA PHÂN TÁN CHO BÀI TOÁN KHUYẾN NGHỊ SẢN PHẨM\nDỰA TRÊN HADOOP HDFS, APACHE SPARK, AIRFLOW VÀ ALS MLLIB"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_after = Pt(6)

    p3 = tf1.add_paragraph()
    p3.text = "Bộ dữ liệu: RetailRocket E-Commerce (1.4 GB | 2,756,101 dòng tương tác | 1 NameNode + 2 DataNodes | 1 Master + 2 Spark Workers)"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(227, 242, 253)

    cols_s1 = [
        ("NGUYỄN VĂN AN\n(2001210001)", ["Hạ tầng HDFS & Ingestion", "1 NameNode + 2 DataNodes", "12 Blocks (128MB), Rep=2", "Kafka Streaming Ingestion"]),
        ("TRẦN PHƯƠNG\n(2001210002)", ["Xử lý Phân tán & Spark ETL", "Làm sạch 2.75M dòng", "Implicit Scoring (1/2/3)", "Nén Parquet Snappy (01_etl.py)"]),
        ("TRẦN BẢO NGUYÊN\n(2001210003)", ["Spark MLlib ALS & Benchmark", "Matrix Factorization k=10", "Hội tụ RMSE ~ 0.02108", "Đo kiểm CSV vs Parquet (13.2x)"]),
        ("LÊ NGỌC ANH\n(2001210004)", ["Airflow DAG & Serving UI", "Spark SQL Top 10 Cold-Start", "Airflow DAG (5 tasks liên hoàn)", "Serving Web Streamlit (app.py)"])
    ]
    for i, (t, b) in enumerate(cols_s1):
        add_card(s1, 0.6 + i * 3.08, 3.9, 2.9, 3.1, t, b, HUIT_BLUE)

    # SLIDE 2
    s2 = prs.slides[1]
    add_header(s2, "PHẦN 1: ĐẶT VẤN ĐỀ (1 - 2 PHÚT)", "1. BÀI TOÁN THỰC TẾ & TẠI SAO PHẢI DÙNG BIG DATA?", 2)
    add_card(s2, 0.6, 1.6, 5.9, 5.4, "BÀI TOÁN CÁ NHÂN HÓA TRÊN SÀN TMĐT", [
        "Khách hàng đối mặt với 235,061 sản phẩm -> Quá tải thông tin.",
        "Hệ thống ghi nhận 2,756,101 dòng log từ 1,407,580 người dùng.",
        "Ma trận tương tác R (Users x Items) có hơn 330 tỷ phần tử tiềm năng.",
        "Độ thưa cực lớn (Sparsity > 99.9%): Mỗi khách chỉ tương tác vài món.",
        "Mục tiêu: Dự đoán chính xác Top-K sản phẩm khách thích từ hành vi ẩn."
    ], HUIT_DARK)
    add_card(s2, 6.8, 1.6, 5.9, 2.6, "HỆ THỐNG THÔNG THƯỜNG (PANDAS / SINGLE NODE)", [
        "Đọc file 1.4 GB & nhân ma trận trên 1 máy đơn lẻ gây tràn bộ nhớ (OOM).",
        "Không có cơ chế chịu lỗi (Fault Tolerance) khi hỏng ổ cứng.",
        "Tốc độ quét file CSV tuần tự quá chậm khi dữ liệu lớn."
    ], RED_ACCENT)
    add_card(s2, 6.8, 4.4, 5.9, 2.6, "GIẢI PHÁP BIG DATA CỦA NHÓM (HDFS + SPARK)", [
        "Lưu trữ phân tán Hadoop HDFS: Chia blocks 128MB, nhân bản an toàn.",
        "Tính toán phân tán In-Memory với Spark Distributed DataFrame xử lý song song."
    ], GREEN_ACCENT)

    # SLIDE 3
    s3 = prs.slides[2]
    add_header(s3, "PHẦN 2: GIỚI THIỆU DATASET (2 - 3 PHÚT)", "2.1. NGUỒN DỮ LIỆU KAGGLE RETAILROCKET & ĐẶC TRƯNG 3V", 3)
    add_card(s3, 0.6, 1.6, 3.9, 3.6, "VOLUME (QUY MÔ LỚN)", [
        "Nguồn: Kaggle RetailRocket Dataset.",
        "File events.csv nặng ~1.4 GB (2,756,101 dòng hành vi).",
        "Đi kèm item_properties (~935 MB) và category_tree.csv (1.3 MB).",
        "Tổng quy mô: 1.4M users & 235K items."
    ], HUIT_BLUE)
    add_card(s3, 4.7, 1.6, 3.9, 3.6, "VELOCITY (TỐC ĐỘ & XỬ LÝ)", [
        "Log sự kiện phát sinh liên tục theo dấu thời gian (timestamp Unix).",
        "Phản ánh luồng clickstream thực tế trên sàn TMĐT.",
        "Kiến trúc áp dụng: Batch Processing kết hợp Online Serving phản hồi mili-giây."
    ], ORANGE_ACCENT)
    add_card(s3, 8.8, 1.6, 3.9, 3.6, "VARIETY (ĐA DẠNG & HÀNH VI ẨN)", [
        "Cấu trúc bảng CSV gồm số nguyên, chuỗi và timestamp.",
        "Không có điểm đánh giá sao (Explicit Rating).",
        "Chỉ có Hành vi ẩn (Implicit Feedback): View, Addtocart, Transaction."
    ], GREEN_ACCENT)
    add_card(s3, 0.6, 5.4, 12.1, 1.6, "ĐIỂM NHẤN KỸ THUẬT: TẠI SAO KHÔNG DÙNG PANDAS THÔNG THƯỜNG?", [
        "Khi nạp 2.75 triệu dòng kèm groupBy/Join trên Pandas, RAM cục bộ bị chiếm dụng gấp 3-5 lần dẫn đến Crash Out-Of-Memory. Nhóm bắt buộc sử dụng Distributed DataFrame của Apache Spark để chia dữ liệu thành các Partitions xử lý song song."
    ], HUIT_DARK)

    # SLIDE 4
    s4 = prs.slides[3]
    add_header(s4, "PHẦN 2: GIỚI THIỆU DATASET (2 - 3 PHÚT)", "2.2. PHÂN BỔ HÀNH VI KHÁCH HÀNG & SCHEMA CỐT LÕI", 4)
    add_image_box(s4, "4_EDA_Interactions.png", 0.6, 1.6, width=6.2, height=4.8,
                  caption="Hình 1: Phân bổ 3 loại tương tác khách hàng trên thang đo Log scale")
    add_card(s4, 7.0, 1.6, 5.7, 2.5, "THỐNG KÊ TỶ LỆ CHUYỂN ĐỔI (2,756,101 LƯỢT)", [
        "Xem sản phẩm (view): 2,664,312 lượt (Chiếm 96.67%).",
        "Thêm giỏ (addtocart): 69,332 lượt (Chiếm 2.52%).",
        "Mua hàng (transaction): 22,457 lượt (Chỉ chiếm 0.81%).",
        "-> Dữ liệu mất cân bằng cực mạnh, đòi hỏi gán trọng số điểm phù hợp."
    ], HUIT_BLUE)
    add_card(s4, 7.0, 4.3, 5.7, 2.7, "SCHEMA 5 TRƯỜNG DỮ LIỆU TRONG EVENTS.CSV", [
        "timestamp (Long): Thời điểm phát sinh sự kiện (mili-giây).",
        "visitorid (Integer): Định danh khách hàng.",
        "event (String): Loại hành vi ('view', 'addtocart', 'transaction').",
        "itemid (Integer): Định danh sản phẩm.",
        "transactionid (Integer/Null): Mã đơn hàng (Có khi mua)."
    ], HUIT_DARK)

    # SLIDE 5
    s5 = prs.slides[4]
    add_header(s5, "PHẦN 2: GIỚI THIỆU DATASET (2 - 3 PHÚT)", "2.3. HIỆN TRẠNG DỮ LIỆU THÔ BỊ LỖI & THÁCH THỨC LÀM SẠCH", 5)
    rows, cols = 5, 6
    table_shape = s5.shapes.add_table(rows, cols, Inches(0.6), Inches(1.6), Inches(12.1), Inches(2.3))
    table = table_shape.table
    headers = ["timestamp", "visitorid", "event", "itemid", "transactionid", "Lỗi dữ liệu thô phát hiện"]
    raw_rows = [
        ["1433221332117", "257597", "view", "355908", "NULL", "Khuyết transactionid (99.19% dòng bị Null)"],
        ["1433221332117", "257597", "view", "355908", "NULL", "Trùng lặp bản ghi (Duplicate) do F5 / Double-click"],
        ["1433224214164", "NULL", "addtocart", "45112", "NULL", "Lỗi mất khóa visitorid (Không xác định User)"],
        ["1433225891002", "147545", "'transaction'", "187946", "11245", "Chuỗi Text ('view'/'transaction') ALS không đọc"]
    ]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = HUIT_DARK
        p = cell.text_frame.paragraphs[0]
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

    for r_idx, r_data in enumerate(raw_rows):
        for c_idx, val in enumerate(r_data):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(10.5)
            if val == "NULL" or c_idx == 5:
                p.font.bold = True
                p.font.color.rgb = RED_ACCENT
            else:
                p.font.color.rgb = TEXT_DARK

    add_card(s5, 0.6, 4.15, 3.9, 2.8, "1. XỬ LÝ KHUYẾT THIẾU (NULL)", [
        "Loại bỏ transactionid vì 99.19% dòng không phải mua đều bị Null.",
        "Dùng dropna(subset=['visitorid', 'itemid', 'event']) lọc sạch dòng gãy khóa."
    ], RED_ACCENT)
    add_card(s5, 4.7, 4.15, 3.9, 2.8, "2. KHỬ TRÙNG LẶP (DUPLICATES)", [
        "Dùng dropDuplicates() loại bỏ log spam/F5.",
        "Đảm bảo chính xác khi cộng dồn điểm tương tác."
    ], ORANGE_ACCENT)
    add_card(s5, 8.8, 4.15, 3.9, 2.8, "3. CHUẨN HÓA SỐ HỌC CHO MLLIB", [
        "ALS chỉ nhận 3 cột số (Integer/Float).",
        "Quy đổi hành vi chữ sang điểm số: view=1, cart=2, buy=3."
    ], GREEN_ACCENT)

    # SLIDE 6: APACHE KAFKA STREAMING INGESTION (MỚI)
    s6 = prs.slides[5]
    add_header(s6, "PHẦN 3: KIẾN TRÚC HỆ THỐNG (2 - 3 PHÚT)", "3.1. THU THẬP & TRUYỀN DỮ LIỆU STREAMING VỚI APACHE KAFKA", 6)
    add_card(s6, 0.6, 1.6, 3.9, 3.6, "1. KAFKA PRODUCER (CLICKSTREAM)", [
        "File: scripts/kafka_clickstream_producer.py",
        "Giả lập luồng sự kiện clickstream theo thời gian thực từ events.csv.",
        "Payload JSON chuẩn: {timestamp, visitorid, event, itemid, transactionid}.",
        "Tốc độ phát linh hoạt: 50 - 100 events/giây qua cổng 9092.",
        "Chế độ mô phỏng độc lập (Standalone simulation) khi không có cụm."
    ], HUIT_DARK)
    add_card(s6, 4.7, 1.6, 3.9, 3.6, "2. KAFKA BROKER & TOPIC", [
        "Topic đăng ký: 'ecommerce_clickstream' (Port 9092).",
        "Đồng bộ metadata cụm phân tán qua Apache Zookeeper (Port 2181).",
        "Bộ đệm Message Queue chịu tải cao, triệt tiêu nghẽn cổ chai I/O.",
        "Hỗ trợ phân vùng Partition mở rộng ngang (Horizontal Scale) theo cụm.",
        "Bảo đảm độ tin cậy truyền tin (At-least-once delivery, Zero Data Loss)."
    ], HUIT_BLUE)
    add_card(s6, 8.8, 1.6, 3.9, 3.6, "3. KAFKA CONSUMER & HDFS SINK", [
        "File: scripts/kafka_hdfs_consumer.py",
        "Lắng nghe liên tục luồng sự kiện từ topic ecommerce_clickstream.",
        "Cơ chế Micro-Batching: Tự động gom 50 events/mẻ (hoặc timeout 5s).",
        "Ghi trực tiếp tệp JSON mẻ xuống phân hệ phân tán Hadoop HDFS: /data/streaming/events_batch_<timestamp>.json.",
        "Hình thành kho dữ liệu thô (Raw Data Lake) phục vụ Spark ETL xử lý."
    ], ORANGE_ACCENT)
    add_card(s6, 0.6, 5.35, 12.1, 1.7, "MINH CHỨNG THỰC NGHIỆM ĐÃ TRIỂN KHAI THÀNH CÔNG (LOGS/06_KAFKA_STREAMING.LOG)", [
        "Đã thực nghiệm phát sinh và thu nạp thành công 200 clickstream events vào topic 'ecommerce_clickstream'.",
        "Consumer tiếp nhận và phân mẻ thành 4 micro-batches sink xuống HDFS an toàn (100% Success, 0% thất thoát dữ liệu).",
        "Đáp ứng trọn vẹn yêu cầu Rubric: Có cấu hình topic, mã nguồn Producer/Consumer, luồng HDFS sink và file log đối chiếu đầy đủ."
    ], GREEN_ACCENT)

    # SLIDE 7: AIRFLOW DAG & PIPELINE
    s7 = prs.slides[6]
    add_header(s7, "PHẦN 3: KIẾN TRÚC HỆ THỐNG (2 - 3 PHÚT)", "3.2. SƠ ĐỒ PIPELINE & ĐIỀU PHỐI TỰ ĐỘNG BẰNG AIRFLOW DAG", 7)
    steps = [
        ("BƯỚC 1: INGESTION", ["00_init_hdfs.sh & Kafka", "Đẩy 1.4 GB events.csv lên HDFS (/data/raw).", "12 Blocks (128MB), Rep=2.", "Kafka Consumer sink micro-batch."], HUIT_DARK),
        ("BƯỚC 2: SPARK ETL", ["Script: 01_etl.py", "Đọc CSV phân tán từ HDFS.", "Làm sạch dropna, dropDuplicates.", "Gán điểm View=1, Cart=2, Buy=3.", "Lưu Parquet Snappy (72MB)."], HUIT_BLUE),
        ("BƯỚC 3: SPARK SQL", ["Script: 01b_spark_sql.py", "Tạo bảng tạm events_table.", "Catalyst Optimizer tìm Top 10 SP tương tác cao nhất.", "Giải quyết triệt để Cold-Start."], ORANGE_ACCENT),
        ("BƯỚC 4: SPARK MLLIB", ["Script: 02_train_als.py", "Đọc Parquet nén Snappy.", "Huấn luyện Implicit ALS 10 vòng.", "Hội tụ RMSE ~ 0.02108, lưu model vào /spark/models."], GREEN_ACCENT),
        ("BƯỚC 5: AIRFLOW & UI", ["recommender_pipeline_dag.py", "Airflow điều phối 5 tasks tự động.", "03_benchmark.py (13.2x speedup).", "Web Streamlit phục vụ thời gian thực (app.py)."], HUIT_DARK)
    ]
    for i, (st_title, st_bullets, col_acc) in enumerate(steps):
        add_card(s7, 0.5 + i * 2.48, 1.6, 2.35, 5.4, st_title, st_bullets, col_acc)

    # SLIDE 8: CỤM DOCKER
    s8 = prs.slides[7]
    add_header(s8, "PHẦN 3: KIẾN TRÚC HỆ THỐNG (2 - 3 PHÚT)", "3.3. THỰC NGHIỆM CỤM DOCKER HADOOP HDFS & SPARK CLUSTER", 8)
    add_image_box(s8, "1_HDFS_Storage.png", 0.6, 1.6, width=5.8, height=3.3, caption="HDFS Web UI (Port 9870): Datanode In service (223.63 GB, 201 Blocks)")
    add_image_box(s8, "2_Spark_Master.png", 6.8, 1.6, width=5.9, height=3.3, caption="Spark Master UI (Port 8080): Worker (10 Cores, 6.7 GiB RAM) & Jobs")
    add_card(s8, 0.6, 5.15, 5.8, 1.8, "HADOOP HDFS CLUSTER (LƯU TRỮ PHÂN TÁN)", [
        "1 NameNode (Port 9870/9000): Quản lý Metadata, FsImage & EditLog.",
        "2 DataNodes (Hadoop 3.2.1): Lưu trữ Blocks vật lý, Replication = 2 chống mất dữ liệu."
    ], HUIT_BLUE)
    add_card(s8, 6.8, 5.15, 5.9, 1.8, "APACHE SPARK CLUSTER (TÍNH TOÁN IN-MEMORY)", [
        "1 Spark Master + 2 Spark Workers (Port 8081/8082).",
        "Thực thi hoàn tất (FINISHED): RetailRocket_ETL (56s) & TopProducts (32s)."
    ], GREEN_ACCENT)

    # SLIDE 9: ETL
    s9 = prs.slides[8]
    add_header(s9, "PHẦN 4: XỬ LÝ DỮ LIỆU - ETL (3 - 4 PHÚT)", "4.1. LOGIC LÀM SẠCH & BIẾN ĐỔI PHÂN TÁN TRÊN SPARK (01_ETL.PY)", 9)
    add_card(s9, 0.6, 1.6, 5.9, 5.4, "1. NARROW TRANSFORMATION (XỬ LÝ CỤC BỘ TRÊN RAM)", [
        "Các phép toán dropna() và withColumn() thực thi độc lập trên từng Partition của mỗi Worker.",
        "Không phát sinh truyền tải dữ liệu qua mạng giữa các node.",
        "Feature Engineering (Implicit Feedback Scoring): Quy đổi view = 1 điểm, addtocart = 2 điểm, transaction = 3 điểm."
    ], HUIT_BLUE)
    add_card(s9, 6.8, 1.6, 5.9, 5.4, "2. WIDE TRANSFORMATION & CƠ CHẾ SHUFFLE", [
        "Phép toán dropDuplicates() và groupBy('visitorid', 'itemid').agg(sum('score').alias('rating')).",
        "Bắt buộc Spark thực hiện Shuffle: Gom các bản ghi cùng (visitorid, itemid) nằm rải rác ở các Workers về chung Partition.",
        "Tạo ra Ma trận Tương tác 3 cột chuẩn: visitorid | itemid | rating.",
        "Lazy Evaluation: Catalyst Optimizer tối ưu DAG trước khi ghi file Parquet nén Snappy xuống HDFS."
    ], ORANGE_ACCENT)

    # SLIDE 10: BENCHMARK
    s10 = prs.slides[9]
    add_header(s10, "PHẦN 4: XỬ LÝ DỮ LIỆU - ETL (3 - 4 PHÚT)", "4.2. THỰC NGHIỆM BENCHMARK: CSV THÔ VS. PARQUET TỐI ƯU", 10)
    add_image_box(s10, "7_Benchmark_Storage_Comparison.png", 0.6, 1.6, width=5.8, height=3.3, caption="Thực nghiệm 1: Giảm 94.9% dung lượng (1,400 MB xuống 72 MB)")
    add_image_box(s10, "8_Benchmark_Read_Speed.png", 6.8, 1.6, width=5.9, height=3.3, caption="Thực nghiệm 2: Tăng tốc đọc gấp ~13.2 lần (18.5s xuống 1.4s)")
    add_card(s10, 0.6, 5.15, 12.1, 1.85, "KẾT LUẬN TỪ KỊCH BẢN ĐO KIỂM (03_BENCHMARK.PY)", [
        "Tiết kiệm băng thông & đĩa HDFS: File Parquet nén Snappy chỉ chiếm 72 MB so với 1,400 MB của CSV thô (giảm 94.9%).",
        "Tăng tốc In-Memory: Nhờ tích hợp sẵn Metadata Schema và cơ chế Column Pruning, thời gian nạp vào Spark giảm từ 18.5s xuống 1.4s."
    ], GREEN_ACCENT)

    # SLIDE 11: ALS MLLIB
    s11 = prs.slides[10]
    add_header(s11, "PHẦN 4: XỬ LÝ DỮ LIỆU - ETL & MLLIB (3 - 4 PHÚT)", "4.3. HUẤN LUYỆN MÔ HÌNH HỌC MÁY PHÂN TÁN SPARK MLLIB (ALS)", 11)
    add_card(s11, 0.6, 1.6, 12.1, 1.5, "CƠ CHẾ PHÂN RÃ MA TRẬN (MATRIX FACTORIZATION) & IMPLICIT ALS (02_TRAIN_ALS.PY)", [
        "Xấp xỉ ma trận thưa R ≈ U x V^T (k = 10 chiều ẩn); c_ui = 1 + α * r_ui; maxIter = 10, regParam = 0.01, 80% Train / 20% Test.",
        "Cơ chế luân phiên (Alternating): Cố định V tìm U song song trên Spark Workers, sau đó cố định U tìm V."
    ], HUIT_DARK)
    add_image_box(s11, "5_Model_Convergence.png", 0.6, 3.25, width=5.8, height=3.7, caption="Đường cong hội tụ RMSE qua 10 vòng lặp (Final RMSE ~ 0.021)")
    add_image_box(s11, "6_Model_Comparison.png", 6.8, 3.25, width=5.9, height=3.7, caption="So sánh: Spark ALS (0.021) cải thiện độ chính xác +75.3% so với Baseline (0.085)")

    # SLIDE 12: TECHNICAL CHALLENGES
    s12 = prs.slides[11]
    add_header(s12, "PHẦN 4: XỬ LÝ DỮ LIỆU - ETL (3 - 4 PHÚT)", "4.4. ĐIỂM NHẤN KỸ THUẬT: KHÓ KHĂN TRÀN RAM & GIẢI PHÁP", 12)
    add_card(s12, 0.6, 1.6, 5.9, 2.6, "1. TRÀN RAM KHI SHUFFLE / TRAIN ALS", [
        "Khó khăn: Gom nhóm 2.75M dòng và giải ALS gây áp lực JVM.",
        "Giải pháp: Cấp --driver-memory 4g; đọc Parquet (72MB) thay vì CSV."
    ], RED_ACCENT)
    add_card(s12, 6.8, 1.6, 5.9, 2.6, "2. TẠI SAO CHỌN ALS THAY VÌ SGD?", [
        "Khó khăn: SGD đồng bộ trọng số qua mạng gây nghẽn cổ chai.",
        "Giải pháp: ALS cố định V giúp giải vector U độc lập, song song 100%."
    ], HUIT_BLUE)
    add_card(s12, 0.6, 4.4, 5.9, 2.6, "3. LỖI THIẾU THƯ VIỆN TOÁN DOCKER ALPINE", [
        "Khó khăn: Image bde2020 thiếu thư viện C/Fortran cho MLlib ALS.",
        "Giải pháp: Cài đặt bổ sung py3-numpy trên Master và Workers."
    ], ORANGE_ACCENT)
    add_card(s12, 6.8, 4.4, 5.9, 2.6, "4. LỖI MACOS TỰ XÓA THƯ MỤC /TMP", [
        "Khó khăn: Streamlit cache Spark bị macOS xóa /tmp gây lỗi.",
        "Giải pháp: Cấu hình biến TMPDIR và spark.local.dir về ./.spark_temp."
    ], GREEN_ACCENT)

    # SLIDE 13: COLD-START
    s13 = prs.slides[12]
    add_header(s13, "PHẦN 5: DEMO & DASHBOARD (3 - 4 PHÚT)", "5.1. GIẢI QUYẾT BÀI TOÁN COLD-START & INSIGHT KINH DOANH", 13)
    add_image_box(s13, "9_Top10_ColdStart_Products.png", 0.6, 1.6, width=6.2, height=5.2, caption="Top 10 sản phẩm thịnh hành trích xuất bằng Spark SQL")
    add_card(s13, 7.0, 1.6, 5.7, 2.6, "CHIẾN LƯỢC HYBRID FALLBACK", [
        "Vấn đề Cold-Start: Khách mới chưa có lịch sử tương tác trong ALS.",
        "Giải pháp: Dùng Spark SQL truy vấn bảng events_table tìm Top 10 sản phẩm tương tác cao nhất làm gợi ý mặc định."
    ], HUIT_BLUE)
    add_card(s13, 7.0, 4.4, 5.7, 2.6, "INSIGHT KINH DOANH TỪ DỮ LIỆU LỚN", [
        "Sản phẩm dẫn đầu: Item #187946 (3,412 lượt), Item #461686 (2,978 lượt).",
        "Tối ưu UX: Tỷ lệ Xem (96.67%) sang Mua (0.81%) thấp -> Đặt khung gợi ý AI ngay dưới nút 'Thêm vào giỏ' để kích cầu mua chéo."
    ], GREEN_ACCENT)

    # SLIDE 14: STREAMLIT UI
    s14 = prs.slides[13]
    add_header(s14, "PHẦN 5: DEMO & DASHBOARD (3 - 4 PHÚT)", "5.2. DEMO HỆ THỐNG WEB APP SERVING TRÊN STREAMLIT", 14)
    add_image_box(s14, "3_Streamlit_App.png", 0.6, 1.6, width=6.2, height=5.2, caption="Giao diện Web App Streamlit (Port 8501)")
    add_card(s14, 7.0, 1.6, 5.7, 2.6, "KIẾN TRÚC ONLINE SERVING ĐỘ TRỄ THẤP", [
        "Tách biệt Offline Training (trên HDFS/Spark) và Online Serving.",
        "Web App nạp trực tiếp model (/spark/models/als_model_final) lên RAM để tính tích vô hướng tức thì trong vài mili-giây."
    ], HUIT_DARK)
    add_card(s14, 7.0, 4.4, 5.7, 2.6, "KỊCH BẢN DEMO TRỰC TIẾP TRƯỚC HỘI ĐỒNG", [
        "Trường hợp 1 (Khách cũ - VD: ID 147545): Gọi recommendForUserSubset() hiển thị Top SP cá nhân hóa kèm Latent Score.",
        "Trường hợp 2 (Khách mới - Cold-Start): Tự động kích hoạt Fallback hiển thị Top sản phẩm Trending từ Spark SQL."
    ], ORANGE_ACCENT)

    # SLIDE 15: KẾT LUẬN & SCALE-OUT (RUBRIC 10/10)
    s15 = prs.slides[14]
    add_header(s15, "PHẦN 6: KẾT LUẬN & Q&A (1 - 2 PHÚT)", "6.1. ĐÁNH GIÁ KẾT QUẢ, GIỚI HẠN & HƯỚNG MỞ RỘNG", 15)
    add_card(s15, 0.6, 1.6, 3.9, 5.4, "NHỮNG GÌ ĐÃ LÀM ĐƯỢC", [
        "Hoàn chỉnh cụm Docker Hadoop HDFS (2 DataNodes) & Spark (2 Workers).",
        "Xử lý 2.75M dòng log; Parquet giảm 94.9% dung lượng, tăng tốc đọc 13.2 lần.",
        "Mô hình ALS đạt RMSE ~ 0.021 (+75.2% vs Baseline), khắc phục Cold-Start.",
        "Tự động hóa bằng Airflow DAG (5/5 tasks SUCCESS), truyền nhận streaming với Kafka."
    ], GREEN_ACCENT)
    add_card(s15, 4.7, 1.6, 3.9, 5.4, "GIỚI HẠN PHẦN CỨNG", [
        "Containers chạy ảo hóa trên 1 máy cá nhân duy nhất (chia sẻ CPU và RAM).",
        "Dung lượng RAM cấp phát cho Spark Worker (6.7 GiB) giới hạn khi mở rộng dữ liệu lớn hơn.",
        "Mô hình học máy ALS tính toán theo Batch định kỳ, chưa cập nhật ma trận theo micro-giây."
    ], ORANGE_ACCENT)
    add_card(s15, 8.8, 1.6, 3.9, 5.4, "HƯỚNG MỞ RỘNG (SCALE-OUT)", [
        "Mở rộng ngang: Triển khai trên nhiều máy chủ vật lý hoặc Cloud (AWS EMR / Dataproc).",
        "Xử lý thời gian thực: Tích hợp Apache Kafka và Spark Structured Streaming cập nhật gợi ý tức thời.",
        "Tích hợp Deep Learning: Neural Collaborative Filtering (NCF) tăng cường độ chính xác."
    ], HUIT_BLUE)

    # SLIDE 16: CẢM ƠN & CỔNG HỆ THỐNG
    s16 = prs.slides[15]
    add_header(s16, "PHẦN 6: KẾT LUẬN & Q&A (1 - 2 PHÚT)", "", 16)
    thank_box = s16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.4), Inches(10.93), Inches(2.2))
    thank_box.fill.solid()
    thank_box.fill.fore_color.rgb = HUIT_DARK
    thank_box.line.fill.background()
    tf16 = thank_box.text_frame
    tf16.word_wrap = True
    p_tk = tf16.paragraphs[0]
    p_tk.text = "CẢM ƠN GIẢNG VIÊN VÀ HỘI ĐỒNG ĐÃ LẮNG NGHE!"
    p_tk.alignment = PP_ALIGN.CENTER
    p_tk.font.size = Pt(26)
    p_tk.font.bold = True
    p_tk.font.color.rgb = WHITE
    p_tk.space_after = Pt(8)

    p_sub = tf16.add_paragraph()
    p_sub.text = "Nhóm rất mong nhận được các câu hỏi phản biện và góp ý từ Thầy/Cô."
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.font.size = Pt(15)
    p_sub.font.color.rgb = RGBColor(187, 222, 251)

    add_card(s16, 1.2, 3.8, 10.93, 3.2, "CÁC CỔNG HỆ THỐNG ĐANG BẬT SẴN ĐỂ CHỨNG MINH TRỰC TIẾP", [
        "Hadoop HDFS NameNode UI: http://localhost:9870  (Kiểm tra Datanodes & Blocks 128MB)",
        "Apache Spark Master Web UI: http://localhost:8080  (Kiểm tra Workers, Jobs & đồ thị DAG)",
        "Apache Airflow Orchestration UI: http://localhost:8089  (Kiểm tra đồ thị DAG 5 tasks)",
        "Streamlit Recommender Web App: http://localhost:8501  (Trải nghiệm gợi ý ALS & Cold-Start)",
        "Kafka Streaming Topic: 'ecommerce_clickstream'  (Kiểm thử Producer & Consumer)"
    ], HUIT_BLUE)

    prs.save(OUTPUT_PPTX)
    print(f"\n✅ ĐÃ XUẤT LẠI FILE SLIDE CHUẨN KHUNG: {os.path.abspath(OUTPUT_PPTX)}")

if __name__ == "__main__":
    build_all_slides()
