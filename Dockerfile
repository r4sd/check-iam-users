FROM python:3.12-slim

WORKDIR /app

# 依存関係をインストール
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .[dev]

# ソースコードをコピー
COPY . .

# デフォルトコマンド
CMD ["pytest", "-v"]
