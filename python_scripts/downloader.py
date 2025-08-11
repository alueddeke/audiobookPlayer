import requests
import os
from pydub import AudioSegment
import subprocess
import argparse

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def download_mp3(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    return False

def combine_mp3_files(input_files, output_file, max_file_size=1024 * 1024 * 1024):  # 1 GB
    print(f"Combining {len(input_files)} files...")
    combined = AudioSegment.empty()
    part_num = 1
    combined_files = []
    
    for file in input_files:
        print(f"Adding {file}...")
        audio = AudioSegment.from_mp3(file)
        combined += audio
        
        # Check if the combined audio exceeds the maximum file size
        if len(combined.raw_data) >= max_file_size:
            part_output_file = f"{os.path.splitext(output_file)[0]}_part{part_num}.mp3"
            print(f"Exporting part {part_num} to {part_output_file}...")
            combined.export(part_output_file, format="mp3", bitrate="192k")
            combined_files.append(part_output_file)
            
            # Start a new combined file for the next part
            combined = AudioSegment.empty()
            part_num += 1

    # Export the final part if any audio remains
    if len(combined.raw_data) > 0:
        part_output_file = f"{os.path.splitext(output_file)[0]}_part{part_num}.mp3"
        print(f"Exporting final part {part_num} to {part_output_file}...")
        combined.export(part_output_file, format="mp3", bitrate="192k")
        combined_files.append(part_output_file)
    
    print("All parts combined and exported.")
    return combined_files

def download_mp3_series(base_url, start, file_format="{:02d}.mp3"):
    input_files = []
    i = start
    while True:
        filename = f"audio_{i:02d}.mp3"
        url = f"{base_url}{file_format.format(i)}"
        
        print(f"Attempting to download: {url}")
        if download_mp3(url, filename):
            input_files.append(filename)
            print(f"Downloaded: {filename}")
            i += 1
        else:
            print(f"Failed to download: {filename}")
            print("Reached the end of the series.")
            break

    return input_files

def main():
    parser = argparse.ArgumentParser(description="Download and combine MP3 files.")
    parser.add_argument("--combine-only", action="store_true", help="Only combine existing files without downloading")
    args = parser.parse_args()

    if not check_ffmpeg():
        print("FFmpeg is not installed. Please install it using 'brew install ffmpeg' and try again.")
        exit(1)

    print(f"Current working directory: {os.getcwd()}")

    base_url = "https://ipaudio5.com/wp-content/uploads/STARR/40k/The%20First%20Heretic/"
    start = 0
    output_file = "combined_audio.mp3"

    if args.combine_only:
        input_files = sorted([f for f in os.listdir() if f.startswith("audio_") and f.endswith(".mp3")])
        if not input_files:
            print("No audio files found in the current directory.")
            return
    else:
        input_files = download_mp3_series(base_url, start)

    if input_files:
        combined_files = combine_mp3_files(input_files, output_file)
        
        if not args.combine_only:
            # Clean up individual files
            for file in input_files:
                os.remove(file)
            print("Individual files cleaned up.")
    else:
        print("No files were downloaded or found. Please check the URL and try again.")

if __name__ == "__main__":
    main()
