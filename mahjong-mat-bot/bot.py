"""Bot Telegram: nhận yêu cầu thiết kế thảm Mahjong, gọi Codex CLI tạo ảnh, gửi lại."""
import asyncio
import logging
import os
import shlex
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
BASE = Path(__file__).parent
JOBS = BASE / "jobs"
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED = {int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()}
CODEX_CMD = shlex.split(os.getenv("CODEX_CMD", "codex exec --full-auto --skip-git-repo-check"))
TIMEOUT = int(os.getenv("CODEX_TIMEOUT", "600"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("mahjong-bot")
lock = asyncio.Semaphore(1)  # chỉ chạy 1 job Codex một lúc


def allowed(update: Update) -> bool:
    user = update.effective_user
    ok = user is not None and user.id in ALLOWED
    if not ok:
        log.warning("Từ chối user %s", user.id if user else None)
    return ok


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.message.reply_text(
        "Gửi: /design <mô tả thảm>\n"
        "Ví dụ: /design thảm mahjong phong cách hoa mẫu đơn, nền xanh ngọc, viền vàng\n"
        "Muốn kèm ảnh tham chiếu: gửi ảnh với caption bắt đầu bằng /design"
    )


async def design(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    msg = update.message
    text = (msg.text or msg.caption or "")
    desc = text.partition(" ")[2].strip()
    if not desc:
        await msg.reply_text("Thiếu mô tả. Ví dụ: /design thảm mahjong hoa sen, tông hồng pastel")
        return

    job_id = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4]
    job = JOBS / job_id
    (job / "output").mkdir(parents=True)
    (job / "refs").mkdir()
    if msg.photo:
        f = await msg.photo[-1].get_file()
        await f.download_to_drive(job / "refs" / "ref1.jpg")
    (job / "brief.md").write_text(f"# Yêu cầu khách\n\n{desc}\n", encoding="utf-8")

    await msg.reply_text(f"Đã nhận job {job_id}. Đang tạo 3 phương án, chờ vài phút...")
    prompt = (
        "Đọc AGENTS.md ở thư mục gốc dự án và brief.md trong thư mục hiện tại, "
        "rồi tạo 3 phương án thiết kế thảm Mahjong, lưu vào output/."
    )
    async with lock:
        try:
            proc = await asyncio.create_subprocess_exec(
                *CODEX_CMD, "-C", str(job), prompt,
                cwd=str(BASE),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
            )
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=TIMEOUT)
            (job / "codex.log").write_bytes(out or b"")
        except asyncio.TimeoutError:
            proc.kill()
            await msg.reply_text("Codex chạy quá thời gian, đã dừng. Thử lại với mô tả ngắn hơn.")
            return
        except FileNotFoundError:
            await msg.reply_text("Không tìm thấy lệnh codex trên máy chạy bot. Kiểm tra CODEX_CMD.")
            return

    err = job / "output" / "error.txt"
    images = sorted((job / "output").glob("*.png"))
    if not images:
        reason = err.read_text(encoding="utf-8") if err.exists() else "Codex không xuất ra ảnh nào."
        await msg.reply_text(f"Chưa có ảnh. {reason}\nXem log: jobs/{job_id}/codex.log")
        return
    for img in images:
        with img.open("rb") as fh:
            await msg.reply_document(fh, filename=img.name, caption=f"{job_id} / {img.name}")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("design", design))
    app.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex(r"^/design"), design))
    log.info("Bot chạy. Allowlist: %s", sorted(ALLOWED))
    app.run_polling()


if __name__ == "__main__":
    main()
