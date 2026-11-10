# Tether — single Python process serving the API and the static frontend.
# SQLite lives on the /data volume. No build step, no node.
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /data var/uploads
ENV TETHER_DB=/data/tether.db TETHER_DATA=/data/var LLM_MODE=replay DEMO_MODE=true PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python3 -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health').status==200 else 1)"
CMD ["python3", "run.py"]
