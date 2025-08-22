# Check if input argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_ply_file>"
    exit 1
fi

# Replace backslashes with forward slashes in the input path
ply_path="${1//\\//}"

# Remove .ply extension and append _sogs for output directory
output_dir="${ply_path%.ply}_sogs"

C:/Users/chans/anaconda3/envs/torch128/Scripts/sogs-compress --ply "$ply_path" --output-dir "$output_dir"