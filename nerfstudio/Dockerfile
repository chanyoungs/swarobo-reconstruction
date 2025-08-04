# Use the official PyTorch image as a base
FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-devel

# Set the working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3.10 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install tiny-cuda-nn with the correct CUDA architecture
RUN TCNN_CUDA_ARCHITECTURES=120 pip install git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch

# Install nerfstudio
RUN git clone https://github.com/nerfstudio-project/nerfstudio.git && \
    cd nerfstudio && \
    pip install -e .

# Set the entrypoint
ENTRYPOINT ["/bin/bash"]
