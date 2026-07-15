FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim

RUN useradd -m -s /bin/bash appuser

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY app.py ./
COPY templates/ ./templates/

ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER appuser

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]