# FILE: logger_config.py
import logging
from datetime import datetime
from pathlib import Path

# ロガーの取得
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 既存のハンドラを削除
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# ログディレクトリの作成
log_dir = Path(__file__).parent.parent / "log"
log_dir.mkdir(parents=True, exist_ok=True)

# ログファイルの名前を実行開始の日時に設定
log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
log_filepath = log_dir / log_filename

# ファイルハンドラの作成
file_handler = logging.FileHandler(log_filepath)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

# ロガーにファイルハンドラを追加
logger.addHandler(file_handler)
