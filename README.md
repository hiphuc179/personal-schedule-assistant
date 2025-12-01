# 🚀 TRỢ LÝ QUẢN LÝ LỊCH TRÌNH CÁ NHÂN (PERSONAL SCHEDULE ASSISTANT)

[cite_start]Đây là đồ án chuyên ngành (2025-2026) nhằm xây dựng một ứng dụng quản lý lịch trình cá nhân[cite: 23, 24]. [cite_start]Điểm đặc biệt của ứng dụng là khả năng **tích hợp xử lý ngôn ngữ tự nhiên tiếng Việt (NLP)** để tự động trích xuất thông tin sự kiện từ câu yêu cầu[cite: 29].

---

## I. TÍNH NĂNG CHÍNH (KEY FEATURES)

[cite_start]Ứng dụng đáp ứng các chức năng cơ bản và nâng cao sau[cite: 33]:

* [cite_start]**Nhập liệu thông minh:** Cho phép người dùng nhập câu tiếng Việt tự do (có thể thiếu dấu, viết tắt), hệ thống tự động phân tích[cite: 35].
* [cite_start]**Trích xuất NLP:** Tự động trích xuất Tên sự kiện, Thời gian bắt đầu/kết thúc, Địa điểm, và Thời gian nhắc nhở (Reminder)[cite: 33, 36].
* [cite_start]**Hệ thống nhắc nhở:** Kiểm tra định kỳ mỗi 60 giây và hiển thị pop-up khi đến giờ nhắc[cite: 33, 96].
* **Quản lý Habit (Giữ Lửa):** Phân loại thói quen lặp lại (Daily, Weekly) và tính năng giữ chuỗi (Streak Check-in).
* [cite_start]**Quản lý sự kiện:** Thêm, sửa, xóa, tìm kiếm, hiển thị lịch theo ngày/tuần/tháng[cite: 33].
* [cite_start]**Lưu trữ cục bộ:** Dữ liệu được lưu trữ an toàn dưới dạng SQLite[cite: 95].

---

## II. KIẾN TRÚC NLP (HYBRID MODEL)

[cite_start]Mô-đun xử lý ngôn ngữ (NLP Engine) được thiết kế theo mô hình **Rule-based (Regex + Dictionary)**, là một biến thể của kiến trúc Hybrid[cite: 71, 72].

| Thành phần | Mục đích | Công nghệ sử dụng |
| :--- | :--- | :--- |
| **Preprocessing** | Chuẩn hóa tiếng Việt, xử lý Teencode, tách từ. | [cite_start]Python `re`, `unicodedata`, `underthesea` (tách từ) [cite: 72, 76] |
| **Parsing Core** | Trích xuất các thực thể (Time, Location, Reminder). | [cite_start]**Rule-based (Custom Regex)**, `python-dateutil` [cite: 79, 72] |
| **Engine** | Hợp nhất, phân loại Intent (Event/Habit) và dọn rác câu. | Python |

---

## III. HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY ỨNG DỤNG

### 1. Chuẩn bị Môi trường

Bạn phải có Python 3.9+ và Git được cài đặt trên hệ thống.

```bash
# 1. Tạo môi trường ảo
python -m venv venv

# 2. Kích hoạt môi trường (Chọn lệnh phù hợp với hệ điều hành)
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate
2. Cài đặt Thư viện
Chạy lệnh sau để cài đặt tất cả dependencies (bao gồm Streamlit, python-dateutil, underthesea):

Bash

pip install -r requirements.txt


3. Chuẩn bị Cơ sở Dữ liệu (Database Setup)
Ứng dụng sử dụng SQLite để lưu trữ cục bộ.

Bạn cần xóa file data.db cũ (nếu có) để hệ thống tạo lại schema mới (vì chúng ta đã thêm cột Habit/Place).

Code sẽ tự động tạo file data.db mới khi chạy lần đầu.

4. Khởi động Ứng dụng Web
Chạy lệnh sau trong Terminal để khởi động Streamlit App:

Bash

streamlit run main.py