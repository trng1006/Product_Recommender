# 🎨 DESIGN RULES - HỆ KHUYẾN NGHỊ SẢN PHẨM (STREAMLIT UI)

Tài liệu này lưu trữ các nguyên tắc thiết kế (Design Tokens) và luật UI/UX áp dụng cho giao diện của Đồ án Big Data, nhằm đảm bảo tính nhất quán và tuân thủ tuyệt đối quy định môn học.

## 1. Nguyên tắc cốt lõi (Core Principles)
- **Chuẩn Rubric:** Chỉ dùng **Streamlit** (Python). Nghiêm cấm sử dụng React, Vue, hay các framework Frontend phức tạp.
- **Phong cách Minimalist:** Tối giản, sang trọng, mang hơi hướng của các Local Brand cao cấp.
- **Kiến trúc SPA (Single Page Application):** Dùng `st.session_state` để chuyển trang (Trang chủ <-> Chi tiết) mượt mà gọn gàng trong 1 file `main.py`, không cần tách folder `pages/` rườm rà.

## 2. Bảng màu (Color Palette & Tokens)
Sử dụng tone màu Warm Monochrome (Trắng kem/Xám than) để tạo chiều sâu thay vì Trắng/Đen cơ bản:
- **Background (Nền toàn trang):** `#F7F7F9` (Xám trắng nhẹ nhàng)
- **Surface (Nền thẻ sản phẩm):** `#FFFFFF` (Trắng tinh, giúp ảnh nổi bật)
- **Primary Action (Nút Thêm vào giỏ):** `#000000` (Đen tuyền, chữ trắng)
- **Secondary Action (Nút Xem chi tiết):** `#F3F4F6` (Xám nhạt)
- **Typography (Màu chữ):** `#111827` (Xám than đậm, dễ đọc)

## 3. Typography & CSS Inject
- **Font-family:** Hệ font mặc định của Apple (`-apple-system`, `BlinkMacSystemFont`, `San Francisco`).
- **Heading:** Trọng lượng đậm (Font-weight `700-800`), ép sát chữ (letter-spacing `-1px`) để tạo form hiện đại.
- Ẩn hoàn toàn Hamburger menu (`#MainMenu`) và Footer mặc định của Streamlit.

## 4. UI Components (Các thành phần giao diện)
- **Product Card (Thẻ sản phẩm):**
  - Bo góc (Border-radius): `16px` cho card, `12px` cho ảnh.
  - Hover Effect: Khi rê chuột vào thẻ, nổi nhẹ lên trên `translateY(-8px)` kèm đổ bóng `box-shadow`.
- **Buttons (Nút bấm):**
  - Bo góc `8px`. Hiệu ứng hover đổi màu background mượt (`transition: 0.2s`).
  - Nút Primary dùng `type="primary"`, Nút Secondary dùng mặc định.

## 5. Đặc tả UX cho Hệ Khuyến Nghị (Recommendation Flow)
- **Vị trí "Điểm Vàng":** Danh sách sản phẩm gợi ý KHÔNG đặt dàn trải ở cuối trang. Được đặt ngay bên dưới "Thông tin sản phẩm & Nút thêm vào giỏ hàng" ở cột bên phải.
- **Layout lưới:** Sử dụng 3 cột (`st.columns(3)`), giới hạn hiển thị 3 thẻ gợi ý để tỷ lệ ảnh vuông 1:1 không bị vỡ trên khung dọc hẹp.
- **Logic Trải nghiệm (Fallback):**
  - Hiển thị rõ thông báo màu Vàng (`st.info`) hoặc Xanh (`st.success`) để báo cáo viên/giáo viên nhận diện được AI đang chạy.
  - Nếu User mới (Cold Start) ➡️ Gợi ý Top Trending.
  - Nếu User cũ ➡️ Gợi ý cá nhân hóa từ ALS Model.
