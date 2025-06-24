cd ~/SWAROBO/EasyVolcap
expname=actor1_4_subseq
data_root=data/enerf_outdoor/actor1_4_subseq
# Render ENeRFi with pretrained model
evc-test -c configs/exps/enerfi/enerfi_${expname}.yaml,configs/specs/spiral.yaml,configs/specs/ibr.yaml runner_cfg.visualizer_cfg.save_tag=${expname} exp_name=enerfi_dtu