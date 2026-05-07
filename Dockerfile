# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# === Системные зависимости (кэшируется) ===
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxcb1 \
    libx11-6 \
    libxau6 \
    libxdmcp6 \
    libxcb-render0 \
    libxcb-shm0 \
    && rm -rf /var/lib/apt/lists/*

# === Python зависимости (кэшируется pip + extra-index) ===
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --extra-index-url "http://gitlab.local/api/v4/projects/1/packages/pypi/simple/" \
                --trusted-host gitlab.local \
                -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--logger.level=info"]