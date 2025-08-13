# DaVinci Resolve Workflow for Image Sequence Export

1. Add clips to media pool.
1. Add clips to timeline.
1. Go to the Color page.

    - Select clips and group them in current group.
    - Use split-screen mode to compare clips.
    - Apply Lift, Gamma, Gain adjustments in individual clip/group post-clip settings.

1. Go to the Edit page.

    - Trim clips.
    - Create compound clip.

1. With the compound clip selected, go to the Fusion page.
    - Add `Saver` node in between `MediaIn` and `MediaOut`.
    - Choose file name by clicking `File` -> Browse button.
        - Choose directory and set file name as .png and file type as `All Files`.
    - In `Settings`, set:
        ```
        Blend = (comp. CurrentTime % N == 0) and 1 or 0
        ```
        where `N` should be replaced with the number of frames to skip(e.g. 24).
    - Then on the top menu, click `Fusion` -> `Render All Savers`.
