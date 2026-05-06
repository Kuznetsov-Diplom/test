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

# Установка из твоего local GitLab Package Registry (project ID=1)
RUN pip install --upgrade pip && \
    pip install --extra-index-url "http://gitlab.local/api/v4/projects/1/packages/pypi/simple/" --trusted-host gitlab.local -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]