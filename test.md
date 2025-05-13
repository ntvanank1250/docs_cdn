📌 Hàm: send_billing_ttvh_metrics_internal
🎯 Mục đích
Hàm này được sử dụng để thu thập và gửi dữ liệu thống kê băng thông CDN theo từng tên miền của khách hàng nội bộ (đặc biệt là các video và hình ảnh) đến Kafka, phục vụ cho việc tính phí dịch vụ CDN theo mô hình thanh toán nội bộ.

🧩 Tính năng chính
Lấy dữ liệu băng thông từ ngày hôm trước.
Phân loại dữ liệu thành: video và hình ảnh.
Gửi dữ liệu tới Kafka topic theo định dạng chuẩn để xử lý tiếp.
Lưu nhật ký hoạt động vào file log.
🔧 Cấu hình yêu cầu
Biến cấu hình trong app.config:
KAFKA_BILLING_SERVER
Địa chỉ server Kafka.
KAFKA_BILLING_SECURITY_PROTOCOL
Giao thức bảo mật (ví dụ: SASL_SSL).
KAFKA_BILLING_SASL_MECHANISM
Cơ chế xác thực SASL (ví dụ: PLAIN).
KAFKA_BILLING_USERNAME
Username SASL để kết nối Kafka.
KAFKA_BILLING_PASSWORD
Mật khẩu SASL để kết nối Kafka.
KAFKA_TOPIC_BILLING_METRICS
Topic Kafka nơi sẽ nhận message.
TENANT_ID_BILLING_METRICS
ID tenant nội bộ dùng cho thanh toán.

🗂️ Cấu trúc dữ liệu đầu ra (payload)
Mỗi bản ghi được gửi đi có dạng:
