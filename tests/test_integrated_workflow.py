#!/usr/bin/env python3
"""
Test script to simulate the integrated workflow using existing downloaded files.
This tests the new integrated logic without re-downloading.
"""

import os
import json
from datetime import datetime
from pydub import AudioSegment
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_audio_files(downloaded_files):
    """Analyze downloaded audio files to determine if combining is needed."""
    if not downloaded_files:
        return False, "No files to analyze"
    
    total_duration = 0
    total_size = 0
    sample_count = min(3, len(downloaded_files))  # Check first 3 files
    
    logger.info(f"🔍 Analyzing {sample_count} sample files...")
    
    for i in range(sample_count):
        try:
            audio = AudioSegment.from_mp3(downloaded_files[i])
            duration_minutes = len(audio) / 1000 / 60
            size_mb = len(audio.raw_data) / 1024 / 1024
            
            total_duration += duration_minutes
            total_size += size_mb
            
            logger.info(f"  File {i+1}: {duration_minutes:.1f} minutes, {size_mb:.1f} MB")
            
        except Exception as e:
            logger.warning(f"Could not analyze {downloaded_files[i]}: {e}")
    
    avg_duration = total_duration / sample_count
    avg_size = total_size / sample_count
    
    logger.info(f"📊 Average: {avg_duration:.1f} minutes, {avg_size:.1f} MB per file")
    
    # If files are already 60+ minutes or 150MB+, no need to combine
    if avg_duration >= 60 or avg_size >= 150:
        logger.info("✅ Files are already optimal size - skipping combination")
        return False, f"Files average {avg_duration:.1f} minutes, {avg_size:.1f} MB"
    else:
        logger.info("📦 Files are small - combining recommended")
        return True, f"Files average {avg_duration:.1f} minutes, {avg_size:.1f} MB"

def test_integrated_workflow():
    """Test the integrated workflow using existing files."""
    
    temp_folder = "temp_well_of_ascension"
    if not os.path.exists(temp_folder):
        logger.error(f"Temp folder {temp_folder} not found!")
        return False
    
    # Get all audio files
    downloaded_files = []
    for i in range(1, 27):
        filename = f"audio_{i:02d}.mp3"
        filepath = os.path.join(temp_folder, filename)
        if os.path.exists(filepath):
            downloaded_files.append(filepath)
    
    logger.info(f"Found {len(downloaded_files)} audio files")
    
    if not downloaded_files:
        logger.error("No audio files found!")
        return False
    
    # Step 1: Analyze files to determine if combining is needed
    should_combine, analysis_msg = analyze_audio_files(downloaded_files)
    
    # Step 2: Process files based on analysis
    if should_combine:
        logger.info("📦 Combining files into optimal segments...")
        # This would call the combine_audio_files function
        logger.info("(Combining logic would run here)")
    else:
        # Use original files as segments - prepare them for upload
        logger.info("📁 Files are already optimal size - preparing for upload...")
        segment_files = []
        segment_info = []
        
        for i, file in enumerate(downloaded_files):
            try:
                audio = AudioSegment.from_mp3(file)
                duration_minutes = len(audio) / 1000 / 60
                size_mb = len(audio.raw_data) / 1024 / 1024
                
                # Create a copy with a better name for upload
                segment_filename = f"well_of_ascension_segment_{i+1:02d}.mp3"
                
                logger.info(f"Preparing segment {i+1}: {duration_minutes:.1f} minutes, {size_mb:.1f} MB")
                
                # Copy file with new name
                shutil.copy2(file, segment_filename)
                
                segment_files.append(segment_filename)
                segment_info.append({
                    "segment": i + 1,
                    "file": segment_filename,
                    "duration_minutes": round(duration_minutes, 2),
                    "size_mb": round(size_mb, 2),
                    "original_files": [file.split('_')[-1].replace('.mp3', '')]
                })
                
            except Exception as e:
                logger.error(f"❌ Error preparing {file}: {e}")
    
    # Step 3: Create table of contents
    toc = {
        "book_title": "Well Of Ascension",
        "created_date": datetime.now().isoformat(),
        "total_segments": len(segment_info),
        "segments": segment_info,
        "processing_note": "Files were combined into larger segments" if should_combine else "Files used directly as segments (no combination needed)"
    }
    
    toc_filename = "well_of_ascension_toc.json"
    with open(toc_filename, 'w') as f:
        json.dump(toc, f, indent=2)
    
    logger.info(f"📋 Created table of contents: {toc_filename}")
    logger.info(f"✅ Successfully prepared {len(segment_files)} segments for upload")
    
    # Step 4: Simulate upload (would call Google Drive upload functions)
    logger.info("☁️ Files are ready for Google Drive upload")
    logger.info("📁 Upload would create: audiobooks/Well Of Ascension/")
    logger.info(f"📁 With {len(segment_files)} segment files and 1 TOC file")
    
    return True

if __name__ == "__main__":
    test_integrated_workflow()
