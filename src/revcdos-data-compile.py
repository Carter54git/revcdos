from sys import exit, argv
from struct import unpack, pack

from shutil import copy2, rmtree
from os import makedirs, remove, listdir
from os.path import join, exists, splitext, dirname, isdir, getsize, basename

from subprocess import check_output
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

if len(argv) < 3:
    print("Usage: python revcdos-data-compile.py <input_folder> <output_folder>")
    exit(1)

sizes_by_ext = {}
input_folder = argv[1]
output_folder = argv[2]
zip = join(output_folder, basename(output_folder) + '.zip')
adf2mp3 = join(dirname(__file__), "adf2mp3.exe")
fontfile = join(dirname(__file__), "sansation.ttf")
fronten1 = join(dirname(__file__), "fronten1.txd")

if not isdir(input_folder):
    print(f"Error: Input folder '{input_folder}' does not exist.")
    exit(1)

if exists(output_folder):
    print(f"Warning: Output folder '{output_folder}' already exists.")
    if exists(join(output_folder, "vc-assets")):
        rmtree(join(output_folder, "vc-assets"))
    if exists(zip):
        remove(zip)

def copy_directory_recursive(src, dst):
    if not exists(dst):
        makedirs(dst)
    
    sizes_lock = Lock()

    def process_file(src_path, dst_path):
        file, ext = splitext(dst_path)
        ext = ext.lower()

        if (".git" in ext or ".exe" in ext or ".dll" in ext or ".mpg" in ext or "temp.mp3" in src_path):
            return
        elif ext == ".adf":
            print(f"Minifying {src_path}")
            ext = "(.adf).mp3"
            check_output(["wine", adf2mp3, src_path, dst_path + ".big"], text=True)
            check_output([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", dst_path + ".big", 
                "-ar", "22050", "-ac", "2", "-f", "mp3", dst_path
            ], text=True)
            remove(dst_path + ".big")
        elif ext == ".mp3":
            print(f"Minifying {src_path}")
            check_output([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", src_path, 
                "-ar", "22050", "-ac", "2", "-f", "mp3", dst_path
            ], text=True)
        elif ext == ".wav":
            print(f"Minifying {src_path}")
            ext = "(.wav).mp3"
            check_output([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", src_path, 
                "-ar", "22050", "-ac", "2", "-f", "mp3", dst_path
            ], text=True)
        elif ext == ".img":
            img_size = getsize(src_path)
            dir_path = src_path.replace(".img", ".dir").replace(".IMG", ".DIR")

            if not exists(dir_path) or dir_path == src_path:
                raise Exception(f"No DIR file found for {src_path}")

            with open(dir_path, 'rb') as dirf, open(src_path, 'rb') as imgf:
                while True:
                    entry = dirf.read(32) # 4 + 4 + 24
                    if len(entry) == 0:
                        break

                    if len(entry) < 32:
                        raise Exception("Unexpected end of file, rest: " + str(len(entry)))

                    offset_sectors, size_sectors, name = unpack("<II24s", entry)
                    name = name.split(b"\0", 1)[0].decode("ascii", errors="ignore")
                    offset = offset_sectors * 2048
                    size = size_sectors * 2048

                    if offset + size > img_size:
                        print(f"[!] Skipping invalid entry: {name}")
                        continue

                    imgf.seek(offset)
                    data = imgf.read(size)

                    makedirs(dst_path, exist_ok=True)
                    out_path = join(dst_path, name.lower())
                    with open(out_path, "wb") as outf:
                        outf.write(data)
            return
        elif ext == ".raw":
            print(f"Minifying {src_path}")
            if src_path.lower().endswith("sfx.raw"):
                def_path = src_path.replace("sfx.raw", "sfx.sdt").replace("sfx.RAW", "sfx.SDT")
                def_dst_path = dst_path.replace("sfx.raw", "sfx.sdt")

                if not exists(def_path) or def_path == src_path:
                    raise Exception(f"No sfx.SDT found for {src_path}")

                with open(def_path, 'rb') as deff, open(src_path, 'rb') as sfxf:
                    samples = []
                    i = 0
                    while True:
                        sample_data = deff.read(20)
                        
                        if len(sample_data) == 0:
                            break

                        if len(sample_data) < 20:
                            raise Exception("Unexpected end of file, rest: " + str(len(sample_data)))
                        
                        offset, size, frequency, loop_start, loop_end = unpack('<IIIIi', sample_data)
                        
                        samples.append({
                            'index': i,
                            'offset': offset,
                            'size': size,
                            'frequency': frequency,
                            'loop_start': loop_start,
                            'loop_end': loop_end,
                            'raw': sfxf.read(size)
                        })
                        i += 1

                def process_sample(sample):
                    i = sample['index']
                    raw = sample['raw']
                    print(f"Minifying sample sfx.raw/{i}")

                    rawfile = join(dst_path, str(i) + ".raw")
                    with open(rawfile, 'wb') as rf:
                        rf.write(raw)
                    
                    mp3file = join(dst_path, str(i) + ".mp3")
                    check_output([
                        "ffmpeg", "-hide_banner", "-loglevel", "error", 
                        "-y", "-f", "s16le", "-ar", str(sample['frequency']), 
                        "-i", rawfile, mp3file
                    ], text=True)
                    
                    sample["mp3_frequency"] = check_output([
                        "ffprobe", "-v", "quiet", "-select_streams", "a:0",
                        "-show_entries", "stream=sample_rate", "-of", "default=noprint_wrappers=1:nokey=1",
                        mp3file
                    ], text=True).strip()

                    remove(rawfile)
                
                print(f"Found {len(samples)} samples in {def_path}, convering...")
                makedirs(dst_path, exist_ok=True)
                with ThreadPoolExecutor() as executor:
                    futures = []
                    for sample in samples:
                        futures.append(executor.submit(process_sample, sample))

                    for future in futures:
                        future.result()

                with open(def_dst_path, "wb") as f:
                    for i, sample in enumerate(samples):
                        f.write(pack('<IIIIi', sample['offset'], sample['size'], int(sample['mp3_frequency']), sample['loop_start'], sample['loop_end']))
                
                return
        else:
            copy2(src_path, dst_path)

        with sizes_lock:
            if exists(dst_path):
                sizes_by_ext[ext] = sizes_by_ext.get(ext, 0) + getsize(dst_path)

    with ThreadPoolExecutor() as executor:
        futures = []
        for item in listdir(src):
            src_path = join(src, item)
            dst_path = join(dst, item)
            dst_path = dst_path.lower()

            if isdir(src_path):
                copy_directory_recursive(src_path, dst_path)
            else:
                futures.append(executor.submit(process_file, src_path, dst_path))
                
        for future in futures:
            future.result()

copy_directory_recursive(input_folder, join(output_folder, "vc-assets", "local"))
makedirs(join(output_folder, "vc-assets", "local", "fonts"), exist_ok=False)
copy2(fontfile, join(output_folder, "vc-assets", "local", "fonts", basename(fontfile)))
copy2(fronten1, join(output_folder, "vc-assets", "local", "models", basename(fronten1)))

print(f"Copied {input_folder} to {output_folder}")

print("\nFile sizes by extension:")
for ext, size in sorted(sizes_by_ext.items(), key=lambda x: x[1], reverse=True):
    if size >= 1024 * 1024:  # Only show if >= 1MB
        print(f"{ext}: {size / (1024 * 1024):.2f} MB")

check_output(["7z", "a", "-tzip", zip, "./*"], cwd=output_folder)
print(f"Created zip archive: {zip}")

