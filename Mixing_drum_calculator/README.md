# Mixing Drum Drive System Calculator ⚙️

Ứng dụng tính toán thiết kế hệ thống dẫn động thùng trộn - Hỗ trợ kỹ sư cơ khí từ bước chọn động cơ đến kiểm nghiệm bền bộ truyền.

## 🌟 Tính năng chính

Ứng dụng được thiết kế theo quy trình thiết kế máy chuẩn (Wizard-based), bao gồm:

- **UC01: Quản lý Dự án:** Tạo mới, lưu trữ và mở lại các dự án dưới dạng file JSON.
- **UC02: Nhập Thông số:** Validate dữ liệu đầu vào (Công suất, số vòng quay, tuổi thọ) bằng Pydantic.
- **UC03: Chọn Động cơ:** Tính toán công suất cần thiết, tra bảng động cơ catalog và phân bổ tỉ số truyền.
- **UC04: Thiết kế Bộ truyền Đai:** Tính toán bộ truyền đai thang (Loại B) theo tiêu chuẩn.
- **UC05: Thiết kế Hộp giảm tốc:** Tính toán bộ truyền bánh răng côn cấp nhanh (Kích thước hình học, kiểm bền uốn, tiếp xúc).
- **UC06: Xuất Báo cáo:** Xuất kết quả tính toán chi tiết ra file PDF và Excel.

## 🛠 Công nghệ sử dụng

- **Ngôn ngữ:** Python 3.10+
- **Giao diện:** PySide6 (Qt for Python)
- **Kiểm soát dữ liệu:** Pydantic v2 (Validation & Serialization)
- **Xuất bản:** openpyxl (Excel), reportlab (PDF)
- **Kiểm thử:** Pytest

## �‍🏫 Hướng dẫn Cài đặt & Chạy ứng dụng 

Sau khi giải nén file `.Zip` của nhóm,  vui lòng mở Terminal (Command Prompt hoặc PowerShell) tại đúng thư mục `Mixing_drum_calculator` và thực hiện các bước sau:

**Bước 1: Tạo môi trường ảo (Virtual Environment)** (Khuyến nghị để tránh xung đột thư viện ngoài)
```powershell
python -m venv venv
```

**Bước 2: Kích hoạt môi trường ảo**
* Trên **Windows** (CMD/PowerShell):
```powershell
.\venv\Scripts\activate hoặc .\venv\Scripts\Activate.ps1
```
* Trên **Mac/Linux**:
```bash
source venv/bin/activate
```

**Bước 3: Cài đặt các thư viện cần thiết**
```powershell
pip install -r requirements.txt
```

**Bước 4: Khởi động giao diện phần mềm**
```powershell
python main.py
```
Sau khi chạy, giao diện ứng dụng sẽ xuất hiện, cho phép thao tác nhập liệu và tính toán lần lượt từ UC01 đến UC06.

## 🧪 Kiểm thử (Testing)

Dự án đã được tích hợp hệ thống Unit Test bao phủ toàn bộ logic tính toán cốt lõi. Để chạy test:

```powershell
python -m pytest test/
```

## 📂 Cấu trúc thư mục

- `app/core/`: Logic tính toán kỹ thuật (độc lập với giao diện).
- `app/ui/`: Mã nguồn giao diện PySide6.
- `app/data/`: Catalog động cơ và các hằng số tiêu chuẩn (Module, đường kính đai...).
- `documents/`: Tài liệu hướng dẫn và công thức toán học gốc.
- `test/`: Các kịch bản kiểm thử tự động.

## ⚠️ Lưu ý kỹ thuật

- **Validation:** Toàn bộ thông số đầu vào được kiểm soát bởi Pydantic. Nếu nhập giá trị âm hoặc không hợp lệ, ứng dụng sẽ ngăn chặn việc chuyển bước.
- **Công thức:** Các công thức tính toán bánh răng côn trong `UC05` được xây dựng dựa trên giáo trình Chi tiết máy (Nguyễn Trọng Hiệp) và các tiêu chuẩn TCVN hiện hành.

---
**Phát triển bởi:** Nhóm 8 
**Mục đích:** Đồ án Đa ngành / Công cụ hỗ trợ thiết kế cơ khí.
