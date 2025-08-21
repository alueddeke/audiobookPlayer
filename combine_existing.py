#!/usr/bin/env python3
"""
Script to combine existing downloaded audio files into segments.
This uses the fixed audio combining logic from audiobook_scraper.py
"""

import os
import json
from datetime import datetime
from pydub import AudioSegment
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def combine_existing_files():
    """Combine existing downloaded files into segments."""
    
    # Check if temp folder exists
    temp_folder = "temp_well_of_ascension"
    if not os.path.exists(temp_folder):
        logger.error(f"Temp folder {temp_folder} not found!")
        return False
    
    # Get all audio files
    audio_files = []
    for i in range(1, 27):  # We know we have 26 files
        filename = f"audio_{i:02d}.mp3"
        filepath = os.path.join(temp_folder, filename)
        if os.path.exists(filepath):
            audio_files.append(filepath)
        else:
            logger.warning(f"Missing file: {filepath}")
    
    logger.info(f"Found {len(audio_files)} audio files to combine")
    
    if not audio_files:
        logger.error("No audio files found!")
        return False
    
    # Combine files using the fixed logic
    combined = AudioSegment.empty()
    current_segment = 1
    segment_files = []
    segment_info = []
    files_in_current_segment = []
    
    for i, file in enumerate(audio_files):
        try:
            logger.info(f"Adding {file} to segment {current_segment}")
            audio = AudioSegment.from_mp3(file)
            combined += audio
            files_in_current_segment.append(file.split('_')[-1].replace('.mp3', ''))
            
            # Check if we should create a new segment
            duration_minutes = len(combined) / 1000 / 60
            size_mb = len(combined.raw_data) / 1024 / 1024
            
            should_split = (
                duration_minutes >= 60 or  # 60 minutes
                size_mb >= 150 or  # 150MB
                i == len(audio_files) - 1  # Last file
            )
            
            if should_split:
                segment_filename = f"well_of_ascension_segment_{current_segment:02d}.mp3"
                logger.info(f"Creating segment {current_segment}: {segment_filename}")
                
                # Export with optimized settings
                combined.export(
                    segment_filename, 
                    format="mp3", 
                    bitrate="128k",
                    parameters=["-q:a", "2"]  # VBR quality setting
                )
                
                segment_files.append(segment_filename)
                
                # Record segment info
                final_duration = len(combined) / 1000 / 60
                final_size = os.path.getsize(segment_filename) / 1024 / 1024
                
                segment_info.append({
                    "segment": current_segment,
                    "file": segment_filename,
                    "duration_minutes": round(final_duration, 2),
                    "size_mb": round(final_size, 2),
                    "original_files": files_in_current_segment.copy()
                })
                
                # Start new segment
                combined = AudioSegment.empty()
                files_in_current_segment = []
                current_segment += 1
                
        except Exception as e:
            logger.error(f"❌ Error processing {file}: {e}")
    
    # Create table of contents
    toc = {
        "book_title": "Well Of Ascension",
        "created_date": datetime.now().isoformat(),
        "total_segments": len(segment_info),
        "segments": segment_info
    }
    
    toc_filename = "well_of_ascension_toc.json"
    with open(toc_filename, 'w') as f:
        json.dump(toc, f, indent=2)
    
    logger.info(f"📋 Created table of contents: {toc_filename}")
    logger.info(f"✅ Successfully created {len(segment_files)} segments")
    
    return True

if __name__ == "__main__":
    combine_existing_files()
