# 📜 AI-GuideStone.md
*“Bia chỉ đường – Nguyên tắc nền tảng cho mọi tương tác với AI trợ lý trong project này”*

---

## 1. 🎯 Mục tiêu và phạm vi
- Đảm bảo AI luôn hoạt động đúng hướng khi phát triển hệ thống **tự động scale workload K8s ngoài giờ hành chính**.
- Mọi logic, quy trình và hành vi phải **tuân thủ URD** được cập nhật tại `urd_autoscale.md`.
- Áp dụng cho toàn bộ giai đoạn từ prototype → build → test → deploy thật.

---

## 2. 🧭 Tôn chỉ hành động

| Nguyên tắc | Mô tả |
|------------|-------|
| **Luôn luôn bám sát URD** | Đọc hiểu `urd_autoscale.md` từ GitHub repo trước khi bắt đầu bất kỳ tác vụ nào. |
| **Mỗi bước đều có xác nhận** | Hoàn thành 1 module → phải có: code, test, log kết quả → cập nhật vào URD. |
| **Luôn gợi ý cụ thể, không mơ hồ** | Không dùng “tuỳ bạn”, “có thể”, “có vẻ như”. Luôn có đề xuất rõ ràng. |
| **Tách dữ liệu & logic** | Khi xử lý giả lập → phân biệt dữ liệu thật (do user cung cấp) và phần xử lý logic tự động. |
| **Không skip test** | Dù logic đơn giản, cũng phải có test case kèm dữ liệu rõ ràng. |
| **Không “quên cập nhật URD”** | Mọi thay đổi logic/code/test đều phải được cập nhật URD kèm timestamp. |
| **Luôn minh bạch** | Phản hồi rõ ràng mọi hành vi đang làm, không được “tự tiện thông minh”. |

---

## 3. 🧩 Tệp/Dữ liệu AI phải đọc trước

| Tệp | Vai trò |
|-----|--------|
| `urd_autoscale.md` | URD tổng thể mô tả logic, flow, quy trình áp dụng |
| `conf/example.ctf` | File đầu vào test cho dry-run engine |
| `tests/test_dry_run_engine.py` | Kiểm thử logic xử lý rule |
| `.env` hoặc `config.py` | Biến môi trường và thông số điều khiển (Webex, Protected NS...) |

---

## 4. 🔐 Giới hạn quyền thao tác

- Không được phép chọc vào môi trường thật của user.
- Tất cả thao tác truy cập kubeconfig, gửi Webex… đều chạy **giả lập**, user sẽ thực thi thật nếu cần.
- Nếu cần môi trường thật, AI chỉ **gợi ý câu lệnh / thao tác**.

---

## 5. ✅ Chuỗi hành động chuẩn

> 1. Nhận repo → đọc toàn bộ file, bắt đầu từ `AI-GuideStone.md` và `urd_autoscale.md`.
> 2. Xác định module cần làm theo tiến trình URD.
> 3. Mỗi bước làm gồm:
>    - Viết module (`*.py`)
>    - Tạo test (`tests/`)
>    - Thực thi kiểm thử
>    - Ghi log kết quả
>    - Cập nhật `Progress Log` trong URD
> 4. Không skip test, không nhảy bước, không lược bớt.
> 5. Sau mỗi phần logic mới → đề xuất chỉnh URD nếu cần.

---

## 6. 📌 File/dữ liệu đặc biệt cần lưu ý

- `protected_namespaces.txt`: chứa namespace không được scale (đã có trong URD)
- Webex token, roomId: cần `.env` hoặc biến môi trường
- Mọi input đều dạng text file (không nhập tay trên giao diện)

---

## 7. 📅 Lịch sử cập nhật

| Ngày | Nội dung | Người cập nhật |
|------|----------|----------------|
| 2025-04-13 | Tạo file AI-GuideStone lần đầu | User |
| 2025-04-13 | Bổ sung logic protected namespace, tôn chỉ kiểm soát test | AI Assistant |

---

> *“Tôn chỉ này là gốc rễ. Mọi logic đều phát sinh từ đây và quay về đây.”*
