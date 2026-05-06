FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY .pypirc .

# Установка из твоего local GitLab Package Registry (project ID=1)
RUN pip install --upgrade pip && \
    pip install --extra-index-url "http://gitlab.local/api/v4/projects/1/packages/pypi/simple/" --trusted-host gitlab.local -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]