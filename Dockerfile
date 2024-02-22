FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
# RUN set -xe \
#     && apt-get update -y \
#     && apt-get install -y python3-pip
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]