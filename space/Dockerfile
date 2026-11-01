# llama-server from the official image (recent enough for Qwen3.5), Gradio on top.
FROM ghcr.io/ggml-org/llama.cpp:server-b11706 AS llama

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libcurl4 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=llama /app /opt/llama
ENV LD_LIBRARY_PATH=/opt/llama

# Spaces run the container as uid 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
COPY --chown=user app.py examples.json ./
EXPOSE 7860
CMD ["python", "app.py"]
