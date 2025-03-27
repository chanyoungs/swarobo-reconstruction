INPUT=/media/chanyoungs/DATA1/SWAROBO-Data/blender/sampling_1
DATA=$(INPUT)-jpeg
COLMAP=$(DATA)-colmap
SAVE_DRIVE=/media/chanyoungs/DATA1/SWAROBO
OUTPUT_DIR=$(SAVE_DRIVE)/outputs

jpeg:
	python utils/batch_img_converter.py \
	--in-dir $(INPUT) \
	--out-dir $(DATA)

process:
	ns-process-data images --data $(DATA) --output-dir $(COLMAP)	

DB_COLMAP=$(COLMAP)/database.db
process-multicamera:
	mkdir $(COLMAP) -p
	colmap feature_extractor \
		--image_path    $(DATA) \
		--database_path $(DB_COLMAP) \
		--ImageReader.single_camera_per_image 1
		# --ImageReader.single_camera_per_folder 1

	colmap exhaustive_matcher \
		--database_path $(DB_COLMAP)

	colmap mapper \
		--database_path $(DB_COLMAP) \
		--image_path    $(DATA) \
		--output_path   $(COLMAP)

	ns-process-data images \
		--data $(DATA) \
		--output-dir $(COLMAP) \
		--skip-colmap \
		--colmap-model-path $(COLMAP)/0 \
		--no-use-single-camera-mode

CONFIG=/home/chanyoungs/Documents/SWAROBO/swarobo/outputs/2_3_4-jpeg-colmap/splatfacto/2024-11-19_154853/config.yml
view:
	ns-viewer --load-config $(CONFIG)

splatfacto:
	ns-train splatfacto-big \
	--pipeline.model.cull_alpha_thresh=0.005 \
	--pipeline.model.continue_cull_post_densification=False \
	--pipeline.model.use_scale_regularization=True \
	--viewer.quit-on-train-completion=True \
	--vis viewer+tensorboard \
	--output-dir $(OUTPUT_DIR) \
	--data $(COLMAP)

splatfacto-long:
	ns-train splatfacto-big \
	--pipeline.model.cull_alpha_thresh=0.005 \
	--pipeline.model.continue_cull_post_densification=False \
	--pipeline.model.use_scale_regularization=True \
	--viewer.quit-on-train-completion=True \
	--vis viewer+tensorboard \
	--max-num-iterations=100000 \
	--steps-per-save=10000 \
	--save-only-latest-checkpoint=False \
	--output-dir $(OUTPUT_DIR) \
	--data $(COLMAP)

splatfacto-mcmc:
# export MAX_JOBS=1
	ns-train splatfacto-mcmc \
	--viewer.quit-on-train-completion=True \
	--vis viewer+tensorboard \
	--max-num-iterations=30000 \
	--steps-per-save=1000 \
	--save-only-latest-checkpoint=False \
	--output-dir $(OUTPUT_DIR) \
	--data $(COLMAP)

nerfacto:
	ns-train nerfacto \
	--data $(COLMAP)

# DB=$(GLOMAP)/database.db

glomap:
	mkdir $(GLOMAP) -p
	colmap feature_extractor \
		--image_path    $(DATA) \
		--database_path $(DB) \
		--ImageReader.single_camera_per_folder 1
	colmap exhaustive_matcher \
		--database_path $(DB)
	glomap mapper \
		--database_path $(DB) \
		--image_path    $(DATA) \
		--output_path   $(GLOMAP)

colmap-vis:
	colmap gui \
	--import_path $(COLMAP)/0 \
	--database_path $(DB_COLMAP) \
	--image_path    $(DATA)

glomap-vis:
	colmap gui \
	--import_path $(GLOMAP)/0 \
	--database_path $(DB) \
	--image_path    $(DATA)

glomap_mapper:
	glomap mapper \
		--database_path $(DB) \
		--image_path    $(DATA) \
		--output_path   $(GLOMAP)

glomap_resume:
	glomap mapper_resume \
		--image_path $(DATA) \
		--input_path $(GLOMAP)/0 \
		--output_path $(GLOMAP)

# DATA=/media/chanyoungs/DATA1/SWAROBO-Data/drone_captures_05.11.24/1106-2-jpeg-camera-2_3_4-3dgs/images
# GLOMAP=/media/chanyoungs/DATA1/SWAROBO-Data/drone_captures_05.11.24/1106-2-jpeg-camera-2_3_4-3dgs/sparse
# glomap_process:
# 	ns-process-data images \
# 	--data $(DATA) \
# 	--output-dir $(GLOMAP) \
# 	--skip-colmap \
# 	--colmap-model-path $(GLOMAP)/0 \
# 	--no-use-single-camera-mode