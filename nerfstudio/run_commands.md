
Here is a good starting point:

```bash
ns-train splatfacto-big \
--pipeline.model.use-bilateral-grid True \
--pipeline.model.strategy mcmc \
--max-num-iterations 60000 \
--pipeline.model.cull_alpha_thresh 0.002 \
--pipeline.model.use_scale_regularization=True \
--data <data> \
--pipeline.model.rasterize_mode antialiased \
--logging.steps-per-log 200
```

Also, for large complex scenes, I have used this to increase max gaussians to 10million:
--pipeline.model.max-gs-num 10000000

I also suggest --pipeline.model.num-downscales 1 if you want full resolution photos for training

This is good if you want to run higher iterations like I shown above and want to let the gaussians split for longer. For example, double it for my 60000 steps.
--pipeline.model.stop-split-at INT │ stop splitting at this step (default: 15000)



