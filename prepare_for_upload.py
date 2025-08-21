#!/usr/bin/env python3
"""
Script to prepare existing audio files for Google Drive upload.
Since files are already optimal size, we'll use them directly as segments.
"""

import os
import json
from datetime import datetime
from pydub import AudioSegment
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def prepare_for_upload():
    """Prepare existing files for upload."""
    
    temp_folder = "temp_well_of_ascension"
    if not os.path.exists(temp_folder):
        logger.error(f"Temp folder {temp_folder} not found!")
        return False
    
    # Get all audio files
    audio_files = []
    for i in range(1, 27):
        filename = f"audio_{i:02d}.mp3"
        filepath = os.path.join(temp_folder, filename)
        if os.path.exists(filepath):
            audio_files.append(filepath)
    
    logger.info(f"Found {len(audio_files)} audio files")
    
    if not audio_files:
        logger.error("No audio files found!")
        return False
    
    # Create segment info for each file
    segment_info = []
    
    for i, file in enumerate(audio_files):
        try:
            audio = AudioSegment.from_mp3(file)
            duration_minutes = len(audio) / 1000 / 60
            size_mb = len(audio.raw_data) / 1024 / 1024
            
            # Create a copy with a better name for upload
            segment_filename = f"well_of_ascension_segment_{i+1:02d}.mp3"
            
            logger.info(f"Preparing segment {i+1}: {duration_minutes:.1f} minutes, {size_mb:.1f} MB")
            
            # Copy file with new name
            import shutil
            shutil.copy2(file, segment_filename)
            
            segment_info.append({
                "segment": i + 1,
                "file": segment_filename,
                "duration_minutes": round(duration_minutes, 2),
                "size_mb": round(size_mb, 2),
                "original_files": [f"{i+1:02d}"]
            })
            
        except Exception as e:
            logger.error(f"❌ Error processing {file}: {e}")
    
    # Create table of contents
    toc = {
        "book_title": "Well Of Ascension",
        "created_date": datetime.now().isoformat(),
        "total_segments": len(segment_info),
        "segments": segment_info,
        "note": "Files used directly as segments (no combination needed - each file is ~72 minutes)"
    }
    
    toc_filename = "well_of_ascension_toc.json"
    with open(toc_filename, 'w') as f:
        json.dump(toc, f, indent=2)
    
    logger.info(f"📋 Created table of contents: {toc_filename}")
    logger.info(f"✅ Successfully prepared {len(segment_info)} segments for upload")
    
    return True

if __name__ == "__main__":
    prepare_for_upload()
