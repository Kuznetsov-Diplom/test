FROM python:3.11-slim

WORKDIR /app

# Системные зависимости для OpenCV + webrtc
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Установка приватного пакета (работает и в CI, и локально)
ARG GITLAB_REGISTRY_TOKEN
RUN pip install --upgrade pip && \
    pip install \
    --extra-index-url "https://gitlab-ci-token:${GITLAB_REGISTRY_TOKEN}@gitlab.com/api/v4/projects/1/packages/pypi/simple/" \
    -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]