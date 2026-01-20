# Dockerfile to replicate GitHub Actions ubuntu-latest environment
# for debugging Flutter-Termux build issues

FROM ubuntu:24.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (matching GitHub Actions workflow)
RUN apt-get update && apt-get install -y \
    libfreetype-dev \
    ninja-build \
    git \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    xz-utils \
    pkg-config \
    build-essential \
    clang \
    lld \
    unzip \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# Setup depot_tools (matching newkdev/setup-depot-tools@v1.0.1)
RUN git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git /opt/depot_tools
ENV PATH="/opt/depot_tools:${PATH}"

# Install Android SDK Command Line Tools and NDK (matching GitHub Actions environment)
ENV ANDROID_HOME=/usr/local/lib/android/sdk
ENV ANDROID_SDK_ROOT=${ANDROID_HOME}
RUN mkdir -p ${ANDROID_HOME}/cmdline-tools && \
    curl -o /tmp/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip && \
    unzip /tmp/cmdline-tools.zip -d ${ANDROID_HOME}/cmdline-tools && \
    mv ${ANDROID_HOME}/cmdline-tools/cmdline-tools ${ANDROID_HOME}/cmdline-tools/latest && \
    rm /tmp/cmdline-tools.zip

ENV PATH="${ANDROID_HOME}/cmdline-tools/latest/bin:${PATH}"

# Install NDK version 27.2.12479018 (latest stable from Google)
RUN yes | sdkmanager --licenses && \
    sdkmanager "ndk;27.2.12479018"

ENV ANDROID_NDK=${ANDROID_HOME}/ndk/27.2.12479018
ENV ANDROID_NDK_HOME=${ANDROID_NDK}

# Create working directory
WORKDIR /build

# Copy project files
COPY . .

# Install Python requirements (ignore-installed to avoid conflicts with system packages)
RUN pip3 install --break-system-packages --ignore-installed -r requirements.txt

# Set environment to avoid interactive git prompts
ENV GIT_TERMINAL_PROMPT=0

# Default command - start interactive shell for debugging
CMD ["/bin/bash"]
