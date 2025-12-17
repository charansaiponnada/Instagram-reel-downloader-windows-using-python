# Instagram Reel Downloader - New Features

## Updates Made

### 1. **Audio Download Feature**
- Added a checkbox option: **"Download audio separately (MP3)"**
- When enabled, the app will extract audio from downloaded reels using FFmpeg
- Audio files are saved with the same shortcode name as the video (e.g., `ABC123.mp3`)
- The app gracefully handles cases where FFmpeg is not installed with helpful instructions

### 2. **Caption/Description Display**
- Added a new **"Reel Caption / Description"** text box
- Displays the caption/description of each reel as it's being downloaded
- The text box is read-only and updates in real-time during downloads
- Shows "No caption available" if the reel has no caption

### 3. **UI Improvements**
- Increased window size to `900x800` to accommodate new features
- Reorganized layout to include the new caption display section
- Added helpful tooltips for the audio checkbox

## Requirements

### For Audio Extraction
To use the audio download feature, you need to install **FFmpeg**:
- **Windows**: Download from https://ffmpeg.org/download.html
- **Mac**: Install via Homebrew: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

The app will automatically check if FFmpeg is installed and provide installation instructions if needed.

## How to Use

1. **Download Videos Only** (Original behavior):
   - Enter reel URLs
   - Leave "Download audio separately (MP3)" unchecked
   - Click "Download Reels"

2. **Download Videos + Extract Audio**:
   - Enter reel URLs
   - Check "Download audio separately (MP3)"
   - Click "Download Reels"
   - Both MP4 and MP3 files will be saved

3. **View Caption/Description**:
   - As reels are being processed, their caption will automatically appear in the "Reel Caption / Description" box
   - The caption text box updates for each reel being downloaded

## File Structure

- `insta-downloader-gui.py` - Main application with new features
- `reels_download/` - Default download folder for videos and audio
- All files (videos and audio) are saved with the reel's shortcode as the filename

## Notes

- Audio extraction requires FFmpeg to be installed and available in system PATH
- The app maintains backward compatibility with existing download functionality
- All error handling is thread-safe for stable performance
