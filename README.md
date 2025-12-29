# revcdos-data-compile 

This Docker image provides an environment to compile revcdos data using the `revcdos-data-compile.py` script. The image includes ffmpeg, ffprobe, Python 3, Wine, and 7z.

## Prerequisites

- Docker installed on your system
- Input folder on your host system containing the original game data
- Output folder path on your host system (will be created by the script)

## Building the Image

To build the Docker image, run:

```bash
docker build -t revcdos-compile .
```

## Usage

The main command for running the container is:

```bash
docker run --rm -v /path/to/input:/input -v /path/to/output:/output revcdos-compile /input /output
```

### Parameters

- `--rm`: Automatically remove the container when it exits
- `-v /path/to/input:/input`: Mount your input folder to `/input` in the container
- `-v /path/to/output:/output`: Mount your output folder to `/output` in the container
- `revcdos-compile`: The name of the Docker image
- `/input /output`: The input and output folder paths inside the container

### Example

```bash
# Build the image
docker build -t revcdos-compile .

# Run the container with your folders
docker run --rm \
  -v /home/user/my-input-data:/input \
  -v /home/user/my-output-data:/output \
  revcdos-compile \
  /input /output
```

### Important Notes

1. **Input Folder**: The input folder on your host system must exist. The script will process all files in this folder.

2. **Wine**: The script uses Wine to run `adf2mp3.exe` for processing `.adf` files. Wine is pre-installed in the container.

3. **Dependencies**: The image includes:
   - ffmpeg and ffprobe for audio/video processing
   - Python 3 for running the script
   - Wine for running Windows executables
   - 7z for creating zip archives

4. **File Processing**: The script processes various file types:
   - `.adf` files: Converted to MP3 using Wine + adf2mp3.exe + ffmpeg
   - `.mp3` files: Minified/converted using ffmpeg
   - `.wav` files: Converted to MP3 using ffmpeg
   - `.img` files: Extracted using paired `.dir` files
   - `.raw` files: Processed and converted to MP3
   - Other files: Copied as-is

5. **Output**: After processing, the script creates a `output.zip` archive in the ouput folder, with contents of generated data.

## Troubleshooting

- **Permission errors**: Make sure Docker has permission to access your input/output directories
- **Wine errors**: If you encounter Wine-related issues, ensure that the `adf2mp3.exe` file is present in the `src/` directory
- **Output folder exists**: Make sure the output folder doesn't already exist, as the script will fail if it does

