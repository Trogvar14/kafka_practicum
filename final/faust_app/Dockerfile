FROM python:3.9-slim

WORKDIR /opt/app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# сначала нужно только файл требований
COPY requirements.txt .

# 1) ставим faust-streaming без зависимостей, чтобы не притащило неверные версии
RUN pip install --no-cache-dir --no-deps faust-streaming==0.10.13

# 2) теперь ставим всё остальное, уже совместимое
RUN pip install --no-cache-dir -r requirements.txt

# копируем код
COPY app.py banctl.py ./

CMD ["bash","-lc","faust -A app worker -l info"]