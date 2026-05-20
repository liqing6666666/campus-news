FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
COPY server.py scraper.py sites.py cache.py ./
EXPOSE 8001
CMD ["python", "server.py", "--sse"]
