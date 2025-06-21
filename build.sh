#!/bin/bash
echo "[+] Building optimized docker image..."
docker buildx build --output type=image,compression=zstd -t moodlemate .
echo "[+] Optimized docker image built successfully."
