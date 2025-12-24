FROM python:3.12-slim
WORKDIR /app
COPY geometric_federated_runtime.py /app
RUN pip install --no-cache-dir numpy requests python-snappy
VOLUME ["/data"]
EXPOSE 8000
CMD ["python", "geometric_federated_runtime.py"]
