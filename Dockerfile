# Pythonイメージ
FROM python:3.10-slim

# 作業ディレクトリ
WORKDIR /app

# 依存ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Botファイルをコピー
COPY message_watcher.py .

# 実行
CMD ["python", "message_watcher.py"]
