FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для OpenCV + MediaPipe + Streamlit-webrtc
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Build-arg для GitLab Package Registry (в CI передаём auth-URL)
ARG EXTRA_INDEX_URL="http://gitlab.local/api/v4/projects/1/packages/pypi/simple"

# Установка зависимостей
RUN pip install --upgrade pip && \
    pip install --extra-index-url "${EXTRA_INDEX_URL}" -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]