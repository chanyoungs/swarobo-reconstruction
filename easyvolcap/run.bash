cd ~/SWAROBO/EasyVolcap
expname=actor1_4_subseq
data_root=data/enerf_outdoor/actor1_4_subseq
# # Render ENeRFi with pretrained model
# evc-test -c configs/exps/enerfi/enerfi_${expname}.yaml,configs/specs/spiral.yaml,configs/specs/ibr.yaml runner_cfg.visualizer_cfg.save_tag=${expname} exp_name=enerfi_dtu

# # Render ENeRFi with GUI
# evc-gui -c configs/exps/enerfi/enerfi_${expname}.yaml exp_name=enerfi_dtu val_dataloader_cfg.dataset_cfg.ratio=0.5 # 2.5 FPS on 3060
# Slightly worst quality, faster rendering
# evc-gui -c configs/exps/enerfi/enerfi_${expname}.yaml exp_name=enerfi_dtu val_dataloader_cfg.dataset_cfg.ratio=0.5 model_cfg.sampler_cfg.n_planes=32,8 model_cfg.sampler_cfg.n_samples=4,1 # 3.6 FPS on 3060

# Run the rendering server, append `configs/specs/server.yaml` to the config file list
evc-gui -c configs/exps/enerfi/enerfi_${expname}.yaml,configs/specs/server.yaml exp_name=enerfi_dtu val_dataloader_cfg.dataset_cfg.ratio=0.5 model_cfg.sampler_cfg.n_planes=32,8 model_cfg.sampler_cfg.n_samples=4,1