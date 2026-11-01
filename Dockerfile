FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    TERM=xterm-256color \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd --create-home appuser && chown appuser /app
USER appuser

COPY --chown=appuser . .

CMD ["python", "-m", "tictactoe"]
