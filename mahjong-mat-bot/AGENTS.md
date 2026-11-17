# Mahjong mat designer (hướng dẫn cho Codex)

Mỗi job nằm trong một thư mục `jobs/<id>/`, có:
- `brief.md`: yêu cầu của khách (đọc kỹ trước khi làm)
- `refs/`: ảnh tham chiếu (nếu có)
- `output/`: nơi LƯU ẢNH KẾT QUẢ (PNG)

Quy tắc:
1. Đọc `brief.md` và `../../prompts/mahjong_mat_spec.md`, rồi tạo 3 phương án thiết kế khác nhau.
2. Lưu thành `output/v1.png`, `output/v2.png`, `output/v3.png`. Không ghi file ngoài thư mục job.
3. Nếu không tạo được ảnh, ghi lý do vào `output/error.txt` và dừng, không bịa kết quả.
4. Không đưa chữ dài vào ảnh (AI hay sai chính tả). Chỉ để họa tiết; chữ sẽ thêm sau.
