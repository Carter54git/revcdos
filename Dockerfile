FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV WINEARCH=win32

RUN dpkg --add-architecture i386

# Install ffmpeg, ffprobe, python3, wine, and 7z
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3 \
    wine \
    p7zip-full \
    && rm -rf /var/lib/apt/lists/*

RUN wineboot --init || true

# Set working directory
WORKDIR /app

# Copy the src directory with all required files
COPY src/ /app/src/

# Make the Python script executable
RUN chmod +x /app/src/revcdos-data-compile.py

# Set the entrypoint so arguments can be passed
ENTRYPOINT ["python3", "src/revcdos-data-compile.py"]

