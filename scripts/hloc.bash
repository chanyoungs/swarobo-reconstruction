DATA=/media/chanyoungs/DATA1/SWAROBO-Data/drone_captures_05.11.24/preprocessed/regained/all-named-jpeg-camera-per-image
COLMAP=$DATA-hloc

# ns-process-data images \
# --data $DATA \
# --output-dir $COLMAP \
# --skip-image-processing \
# --matching-method exhaustive \
# --sfm_tool hloc \
# --no-use-single-camera-mode \
# --no-same-dimensions \
# --feature-type disk \
# --matcher-type disk+lightglue \
# --matching-method exhaustive

ns-train splatfacto-big \
--pipeline.model.cull_alpha_thresh=0.005 \
--pipeline.model.continue_cull_post_densification=False \
--pipeline.model.use_scale_regularization=True \
--viewer.quit-on-train-completion=True \
--vis viewer+tensorboard \
--data $COLMAP