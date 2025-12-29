# revcdos

[revcDOS](https://dos.zone/revcdos) is a browser port of reVC created by the DOS.Zone Team. It was previously an exclusive game hosted on the DOS.Zone website; however, after receiving a DMCA request from EBRAND, we decided to make the binaries public. You may now host it locally or on your own website, but you must follow these requirements:


* You must credit DOS.Zone Team as the authors of the port and provide a link to this page.
* You must keep the cloud save functionality enabled.
* You must keep the logo in the menu (Vice City by DOS.Zone Team).

The game consist of 2 parts:
* 1st binaries it self
* 2nd compatible data

You can download binaries from Releases section of this repository.

The binary distribution contains:

* `game.js` — the game module launcher
* `GamepadEmulator.js` — touch and gamepad controls
* `idbfs.js` — a script for managing IndexedDB
* `jsdos-cloud-sdk.js` — a script that supports cloud saves
* `index.js` / `index.wasm` — the WebAssembly module of revcDOS
* `preload_files.list` — a list of resource files that are loaded at startup
* `host.html` — an example page for local testing
* `index.html` — the game page embedded into `host.html`

First, you need to obtain data compatible with revcDOS. You can do this easily using the provided script.
The only thing you need is the original GTA: Vice City game data.

## Data compile (Docker)

This Docker image provides an environment to compile revcDOS data using the `revcdos-data-compile.py` script. The image includes ffmpeg, ffprobe, Python 3, Wine, and 7z.

### Prerequisites

- Docker installed on your system
- Input folder on your host system containing the original game data
- Output folder path on your host system (will be created by the script)

### Building the Image

To build the Docker image, run:

```bash
docker build -t revcdos-compile .
```

### Usage

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

### Troubleshooting

- **Permission errors**: Make sure Docker has permission to access your input/output directories
- **Wine errors**: If you encounter Wine-related issues, ensure that the `adf2mp3.exe` file is present in the `src/` directory
- **Output folder exists**: Make sure the output folder doesn't already exist, as the script will fail if it does

## Testing revcDOS locally

Now that you have compatible data, you need to serve the binary folder and open `host.html` in your browser. Then select the folder containing the compatible resources, and it should work.

## Deploing on a website

revcDOS is a completely asynchronous game. From time to time, it will request additional files as they are needed. Therefore, deploying it on a website requires two steps:

1. Provide the resources required to start the game (approximately 50 MB).
2. Provide the remaining resources on demand, as they are requested.

Both steps are controlled in `game.js`:

**1.** `Module.initFS` — you must populate the Emscripten filesystem with the files listed in `preload_files.list`. In our reference implementation (`host.html`), we use a simple `postMessage` protocol to handle this.

**2.** `Module.getAsyncUrl` — you must implement this function and provide a URL from which the game can download the file passed as the first argument. In our implementation, we also use a simple `postMessage` protocol for this.

That’s it!

## Need help?

Feel free to ask in our [TG Channel](https://t.me/gamebase54) or create an issue.


