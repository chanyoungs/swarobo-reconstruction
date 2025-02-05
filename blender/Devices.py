import cycles
import bpy
import sys

# blender -b file.blend -P Devices.py -o output_folder/frame_
# blender -b /home/chan/blender/car_drones.blend -P Devices.py -F PNG -x 1 -a -o /home/chan/blender/output_folder/frame_


# samples = 1
# bpy.context.scene.cycles.samples = samples
# bpy.context.scene.cycles.preview_samples

preferences = bpy.context.preferences
cycles_preferences = preferences.addons["cycles"].preferences
cycles_preferences.refresh_devices()

devices = cycles_preferences.devices

def list_enum(enum):
    return [opt[0] for opt in enum]


def print_devices():
    print("Devices:")
    for device in devices:
        print(f"   [{device.id}]<{device.type}> \"{device.name}\" Using: {device.use}")

    print(f"Compute device type: {cycles_preferences.compute_device_type}")
    print(f"Cycles device: {bpy.context.scene.cycles.device}")


def select_devices():
    if not devices:
        raise RuntimeError("Unsupported device type")
    
    for device in devices:
        device.use = True

    
    cycles_preferences.compute_device_type = "CUDA"
    bpy.context.scene.cycles.device = "GPU"

    # for device in devices:
    #     if "n" in input(f"[{device.id}]<{device.type}> \"{device.name}\" Use device? (Y/n): ").lower():
    #         device.use = False
    #     else:
    #         device.use = True

    
    # cycles_preferences.compute_device_type = input(f"Select the preferred compute device [{', '.join(list_enum(cycles.properties.enum_device_type))}]: ").upper()
    # bpy.context.scene.cycles.device = input(f"Select the compute device type [{', '.join(list_enum(cycles.properties.enum_devices))}]: ").upper()


def main():
    assert sys.stdin, "sys.stdin should be available (is the script running using the --python/-P argument?)"

    select_devices()
    print_devices()


if __name__ == "__main__":
    main()