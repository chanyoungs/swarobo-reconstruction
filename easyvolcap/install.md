# EasyVolCap Installation Guide
```bash
# System dependencies
sudo apt-get update && sudo apt-get install libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev libgl1-mesa-dev ffmpeg

# Python dependencies
conda create -n ev python=3.10 -y
conda activate ev

pip install --pre torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu128
pip install "git+https://github.com/facebookresearch/pytorch3d.git"
cd ~/SWAROBO/EasyVolcap
pip install -v -e . 

# conda install -c conda-forge libstdcxx-ng

ln -sf /usr/lib/x86_64-linux-gnu/libstdc++.so.6 \
       $CONDA_PREFIX/lib/libstdc++.so.6
```

# Run
```bash
expname=actor1_4_subseq
data_root=data/enerf_outdoor/actor1_4_subseq
# Render ENeRFi with pretrained model
evc-test -c configs/exps/enerfi/enerfi_${expname}.yaml,configs/specs/spiral.yaml,configs/specs/ibr.yaml runner_cfg.visualizer_cfg.save_tag=${expname} exp_name=enerfi_dtu

# Render ENeRFi with GUI
evc-gui -c configs/exps/enerfi/enerfi_${expname}.yaml exp_name=enerfi_dtu val_dataloader_cfg.dataset_cfg.ratio=0.5 # 2.5 FPS on 3060
```