FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . .
# 运行环境设置
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
EXPOSE 8000
