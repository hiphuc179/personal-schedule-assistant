# Personal Schedule Assistant

Ứng dụng quản lý lịch trình cá nhân sử dụng Python và Streamlit, tích hợp xử lý ngôn ngữ tự nhiên tiếng Việt (NLP) để tự động trích xuất sự kiện và thói quen.

## Tính năng

- Quản lý sự kiện và thói quen cá nhân
- Tích hợp AI/NLP để thêm sự kiện bằng tiếng Việt tự nhiên
- Nhắc nhở sự kiện sắp diễn ra (có âm thanh)
- Xuất/nhập dữ liệu dưới dạng JSON để sao lưu hoặc phục hồi
- Giao diện trực quan, dễ sử dụng

## Yêu cầu hệ thống

- Python >= 3.8
- pip

## Hướng dẫn cài đặt

### 1. Tạo môi trường ảo

```bash
python -m venv venv
```

Kích hoạt môi trường ảo:

- **Windows (PowerShell):**
  ```bash
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```bash
  .\venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 2. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

## Hướng dẫn chạy ứng dụng

```bash
streamlit run main.py
```

Sau khi chạy, truy cập địa chỉ hiển thị trên terminal (thường là http://localhost:8501).

## Backup & Khôi phục dữ liệu

- **Xuất dữ liệu:** Sử dụng sidebar để tải file backup JSON.
- **Nhập dữ liệu:** Sử dụng sidebar để upload file JSON và nhập dữ liệu vào hệ thống.


---

> Đồ án chuyên ngành - Ứng dụng quản lý lịch trình cá nhân tích hợp AI/NLP tiếng Việt.
