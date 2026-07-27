FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir python-telegram-bot==13.7 requests==2.31.0

COPY . .

CMD ["python", "vpn_bot/bot.py"]
