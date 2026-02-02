FROM python:3.10.14-slim

WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコードをコピー
COPY app/ ./app/

# 実行
CMD ["python", "app/message_watcher.py"]
