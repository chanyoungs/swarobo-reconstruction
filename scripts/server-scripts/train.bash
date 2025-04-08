OUTPUT_DIR=/home/chan/outputs
source ~/miniconda3/etc/profile.d/conda.sh
conda activate nerfstudio

DATA_DIR=$1
PROCESS_DATA_BOOL=$2
SAMPLING_DENSITY=$3

if [ "$PROCESS_DATA_BOOL" = "True" ]; then
    ns-process-data images --data $DATA_DIR --output-dir ${DATA_DIR}_colmap --no-gpu
    DATA_DIR=${DATA_DIR}_colmap
fi

if [ -n "$SAMPLING_DENSITY" ]; then
    python ~/server-scripts/image_sampling.py --data_dir $DATA_DIR --sampling_density $SAMPLING_DENSITY
fi

ns-train splatfacto-mcmc \
--viewer.quit-on-train-completion=True \
--vis viewer+tensorboard \
--max-num-iterations=30000 \
--steps-per-save=1000 \
--save-only-latest-checkpoint=False \
--output-dir $OUTPUT_DIR \
--data $DATA_DIR