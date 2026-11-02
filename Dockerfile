FROM python:3.11-slim

WORKDIR /app

# Создаем директорию и права для непривилегированного пользователя HF
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R user:user /app

USER user

EXPOSE 7860

CMD ["python", "app.py"]
