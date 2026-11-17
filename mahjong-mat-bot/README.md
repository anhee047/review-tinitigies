# Mahjong mat design bot

Bot Telegram nhận yêu cầu → gọi Codex CLI tạo 3 phương án thảm Mahjong → gửi ảnh lại.

## Chạy (trên máy đã cài Codex CLI và đã đăng nhập)
```bash
cd mahjong-mat-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # điền TELEGRAM_BOT_TOKEN và ALLOWED_USER_IDS
python bot.py
```

## Dùng
- `/design thảm mahjong hoa mẫu đơn, nền xanh ngọc, viền vàng`
- Gửi ảnh kèm caption `/design ...` để Codex dùng ảnh làm tham chiếu.

## Bảo mật
- Chỉ ID trong `ALLOWED_USER_IDS` mới ra lệnh được; người khác bị bỏ qua.
- Token để trong `.env` (đã ignore), không dán vào chat.
- `--full-auto` cho Codex tự sửa file trong thư mục job; chạy bot trên máy riêng, không dùng máy chứa dữ liệu nhạy cảm.

## Chưa kiểm chứng
- Codex CLI của bạn có tạo được ảnh hay không (tùy phiên bản/model/gói). Thử `codex exec "tạo ảnh PNG 1024x1024 hình hoa" ` trước.
- Cách Codex ghi ảnh ra file (có thể phải chỉnh prompt trong `bot.py` cho khớp project quilling card).
- Kích thước/DPI theo nhà in thảm thật: sửa `prompts/mahjong_mat_spec.md`.
