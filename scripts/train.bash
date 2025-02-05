screen -S train
screen -dr train

OUTPUT_DIR=/home/chan/outputs
conda activate nerfstudio

ns-train splatfacto-mcmc \
--viewer.quit-on-train-completion=True \
--vis viewer+tensorboard \
--max-num-iterations=30000 \
--steps-per-save=1000 \
--save-only-latest-checkpoint=False \
--output-dir $OUTPUT_DIR \
--data $1