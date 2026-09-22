FROM python:3.12-slim

WORKDIR /app

COPY simulator/requirements.txt ./simulator/requirements.txt
RUN pip install --no-cache-dir -r simulator/requirements.txt

COPY simulator ./simulator
COPY shared/contracts ./shared/contracts

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "simulator.main"]
