#!/usr/bin/env python3
"""
Test script to analyze existing audio files
"""

import os
from pydub import AudioSegment
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_existing_files():
    """Analyze existing downloaded files."""
    
    temp_folder = "temp_well_of_ascension"
    if not os.path.exists(temp_folder):
        logger.error(f"Temp folder {temp_folder} not found!")
        return
    
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
        return
    
    # Analyze first 3 files
    total_duration = 0
    total_size = 0
    sample_count = min(3, len(audio_files))
    
    logger.info(f"🔍 Analyzing {sample_count} sample files...")
    
    for i in range(sample_count):
        try:
            audio = AudioSegment.from_mp3(audio_files[i])
            duration_minutes = len(audio) / 1000 / 60
            size_mb = len(audio.raw_data) / 1024 / 1024
            
            total_duration += duration_minutes
            total_size += size_mb
            
            logger.info(f"  File {i+1}: {duration_minutes:.1f} minutes, {size_mb:.1f} MB")
            
        except Exception as e:
            logger.warning(f"Could not analyze {audio_files[i]}: {e}")
    
    avg_duration = total_duration / sample_count
    avg_size = total_size / sample_count
    
    logger.info(f"📊 Average: {avg_duration:.1f} minutes, {avg_size:.1f} MB per file")
    
    # Determine if combining is needed
    if avg_duration >= 60 or avg_size >= 150:
        logger.info("✅ Files are already optimal size - NO COMBINING NEEDED")
        logger.info("📁 These files can be used directly as segments")
    else:
        logger.info("📦 Files are small - COMBINING RECOMMENDED")
        logger.info("🔧 Run the combine script to create larger segments")

if __name__ == "__main__":
    analyze_existing_files()
