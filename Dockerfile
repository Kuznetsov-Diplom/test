FROM python:3.11-slim

WORKDIR /app

# Полный набор системных библиотек для OpenCV + MediaPipe в slim-образе
RUN apt-get update && apt-get install -y \
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

COPY requirements.txt .

# Установка из local GitLab Package Registry
RUN pip install --upgrade pip && \
    pip install --extra-index-url "http://gitlab.local/api/v4/projects/1/packages/pypi/simple/" \
                --trusted-host gitlab.local -r requirements.txt

COPY . .

EXPOSE 8501

# Добавил info-логирование, чтобы сразу видеть, что приложение стартовало
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--logger.level=info"]