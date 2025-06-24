#!/bin/bash
CUDA=128
CUDA_TOOLKIT=12.8.0

# # Install miniconda
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh

# Setup miniconda
source ~/miniconda3/bin/activate
conda init --all

# Setup nerfstudio venv
conda create --name nerfstudio -y python=3.10
source $(conda info --base)/etc/profile.d/conda.sh
conda activate nerfstudio
python -m pip install --upgrade pip

# Install prerequisites
pip uninstall -y torch torchvision functorch tinycudann
pip install torch==2.1.2+cu$CUDA torchvision==0.16.2+cu$CUDA --extra-index-url https://download.pytorch.org/whl/cu$CUDA
conda install -y -c "nvidia/label/cuda-$CUDA_TOOLKIT" cuda-toolkit
pip install ninja git+https://github.com/NVlabs/tiny-cuda-nn/#subdirectory=bindings/torch

# Install nerfstudio
git clone https://github.com/nerfstudio-project/nerfstudio.git
cd nerfstudio
pip install --upgrade pip setuptools
pip install -e .
# pip install nerfstudio
# ns-install-cli
# Install COLMAP
conda install -y -c conda-forge colmap