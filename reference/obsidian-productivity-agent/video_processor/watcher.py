#!/usr/bin/env python3
"""
Video file watcher and transcription processor using faster-whisper
"""
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from faster_whisper import WhisperModel
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Video file extensions to watch
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg'}

class VideoTranscriptionHandler(FileSystemEventHandler):
    def __init__(self, watch_dir, output_dir, model_name):
        self.watch_dir = Path(watch_dir)
        self.output_dir = Path(output_dir)
        self.processing_files = set()
        self.known_files = set()

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Watching directory: {self.watch_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Loading Whisper model: {model_name}")

        # Initialize faster-whisper model
        # Using CPU with int8 quantization for better performance
        self.model = WhisperModel(model_name, device="cpu", compute_type="int8")

        logger.info("Model loaded successfully")

        # Process any existing video files in the watch directory
        self.process_existing_files()

        # Track known files to detect new ones
        self.update_known_files()

    def update_known_files(self):
        """Update the set of known files in the watch directory"""
        self.known_files = set()
        for video_ext in VIDEO_EXTENSIONS:
            for video_file in self.watch_dir.glob(f"*{video_ext}"):
                self.known_files.add(video_file.name)

    def check_if_already_processed(self, video_path):
        """Check if this video has already been processed"""
        output_path = self.output_dir / f"{video_path.stem}.md"
        return output_path.exists()

    def process_existing_files(self):
        """Process any video files that already exist in the watch directory"""
        logger.info("Checking for existing video files...")
        found_files = []

        for video_ext in VIDEO_EXTENSIONS:
            for video_file in self.watch_dir.glob(f"*{video_ext}"):
                found_files.append(video_file)

        if found_files:
            logger.info(f"Found {len(found_files)} existing video file(s)")
            for video_file in found_files:
                if self.check_if_already_processed(video_file):
                    logger.info(f"Skipping already processed file: {video_file.name}")
                else:
                    logger.info(f"Processing existing file: {video_file.name}")
                    self.process_video(video_file)
        else:
            logger.info("No existing video files found")

    def on_created(self, event):
        logger.debug(f"File created event: {event.src_path}")

        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's a video file
        if file_path.suffix.lower() not in VIDEO_EXTENSIONS:
            logger.debug(f"Not a video file: {file_path.name}")
            return

        logger.info(f"New video file detected: {file_path.name}")

        # Wait for file to be fully written
        self.wait_for_file_ready(file_path)

        # Process the file
        self.process_video(file_path)

    def on_modified(self, event):
        """Handle file modification events (useful for copied files)"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's a video file
        if file_path.suffix.lower() not in VIDEO_EXTENSIONS:
            return

        # Check if this is a new file we haven't seen before
        if file_path.name not in self.known_files:
            logger.info(f"New video file detected via modification: {file_path.name}")
            self.known_files.add(file_path.name)

            # Wait for file to be fully written
            self.wait_for_file_ready(file_path)

            # Process the file
            self.process_video(file_path)

    def on_moved(self, event):
        logger.debug(f"File moved event: {event.dest_path}")

        if event.is_directory:
            return

        dest_path = Path(event.dest_path)

        # Check if it's a video file
        if dest_path.suffix.lower() not in VIDEO_EXTENSIONS:
            return

        logger.info(f"Video file moved in: {dest_path.name}")
        self.known_files.add(dest_path.name)

        # Wait for file to be ready
        self.wait_for_file_ready(dest_path)

        # Process the file
        self.process_video(dest_path)

    def wait_for_file_ready(self, file_path, timeout=30):
        """Wait for a file to be fully written by checking if its size is stable"""
        logger.info(f"Waiting for file to be ready: {file_path.name}")
        last_size = -1
        stable_count = 0

        for _ in range(timeout):
            try:
                current_size = file_path.stat().st_size
                if current_size == last_size:
                    stable_count += 1
                    if stable_count >= 2:  # File size stable for 2 seconds
                        logger.info(f"File is ready: {file_path.name}")
                        return True
                else:
                    stable_count = 0
                last_size = current_size
            except Exception as e:
                logger.debug(f"Error checking file size: {e}")

            time.sleep(1)

        logger.warning(f"Timeout waiting for file to be ready: {file_path.name}")
        return False

    def process_video(self, video_path):
        """Process a video file for transcription"""
        # Check if already processing
        if video_path in self.processing_files:
            logger.info(f"Already processing: {video_path.name}")
            return

        # Check if already processed (output exists)
        if self.check_if_already_processed(video_path):
            logger.info(f"Already processed (output exists): {video_path.name}")
            return

        try:
            self.processing_files.add(video_path)
            logger.info(f"Starting transcription for: {video_path.name}")

            # Extract audio from video to WAV format
            wav_path = self.extract_audio(video_path)

            if not wav_path or not wav_path.exists():
                logger.error(f"Failed to extract audio from {video_path.name}")
                return

            # Transcribe the audio using faster-whisper
            transcription = self.transcribe_audio_faster(wav_path, video_path.stem)

            if transcription:
                # Save transcription to markdown
                self.save_transcription(video_path, transcription)

            # Clean up temporary WAV file
            try:
                wav_path.unlink()
                logger.info(f"Cleaned up temporary WAV file: {wav_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary WAV file: {e}")

        except Exception as e:
            logger.error(f"Error processing {video_path}: {e}")
        finally:
            self.processing_files.discard(video_path)

    def extract_audio(self, video_path):
        """Extract audio from video file to WAV format using ffmpeg"""
        try:
            # Create temporary WAV file path
            wav_path = self.output_dir / f"{video_path.stem}_temp.wav"

            # FFmpeg command to extract audio as 16kHz mono WAV
            cmd = [
                'ffmpeg',
                '-i', str(video_path),
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit little endian
                '-ar', '16000',  # 16kHz sampling rate
                '-ac', '1',  # Mono
                '-y',  # Overwrite output
                str(wav_path)
            ]

            logger.info(f"Extracting audio from {video_path.name}...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None

            logger.info(f"Audio extracted successfully to {wav_path.name}")
            return wav_path

        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return None

    def transcribe_audio_faster(self, wav_path, video_name):
        """Transcribe audio using faster-whisper"""
        try:
            logger.info(f"Starting transcription with faster-whisper for {video_name}...")

            # Transcribe with faster-whisper
            segments, info = self.model.transcribe(
                str(wav_path),
                beam_size=5,
                language="en",  # Set to None for auto-detection
                word_timestamps=False,
                vad_filter=True,  # Voice activity detection to remove silence
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # Collect all segments into text
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "

            transcription = transcription.strip()

            if transcription:
                logger.info(f"Transcription completed for {video_name}")
                logger.info(f"Detected language: {info.language} with probability {info.language_probability:.2f}")
                return transcription
            else:
                logger.warning(f"Empty transcription for {video_name}")
                return None

        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None

    def save_transcription(self, video_path, transcription):
        """Save transcription to markdown file"""
        try:
            # Simple filename - just video name with .md extension
            md_filename = f"{video_path.stem}.md"
            md_path = self.output_dir / md_filename

            # Create markdown content
            content = f"""## Metadata
- **Source File**: {video_path.name}
- **File Size**: {video_path.stat().st_size / (1024*1024):.2f} MB

## Transcription

{transcription}
"""

            # Write markdown file
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Transcription saved to: {md_path}")

        except Exception as e:
            logger.error(f"Error saving transcription: {e}")

def main():
    # Get environment variables
    watch_dir = os.environ.get('WATCH_DIR', '/watch')
    output_dir = os.environ.get('OUTPUT_DIR', '/output')
    whisper_model = os.environ.get('WHISPER_MODEL', 'base.en')
    polling_interval = float(os.environ.get('POLLING_INTERVAL', '2.0'))

    # Validate paths
    watch_path = Path(watch_dir)
    if not watch_path.exists():
        logger.error(f"Watch directory does not exist: {watch_dir}")
        sys.exit(1)

    # Create event handler and observer
    event_handler = VideoTranscriptionHandler(
        watch_dir=watch_dir,
        output_dir=output_dir,
        model_name=whisper_model
    )

    # Use PollingObserver instead of regular Observer for better Docker volume compatibility
    observer = PollingObserver(timeout=polling_interval)
    observer.schedule(event_handler, watch_dir, recursive=False)

    # Start watching
    observer.start()
    logger.info(f"Video watcher started (polling mode, interval={polling_interval}s)")
    logger.info(f"Monitoring {watch_dir} for video files...")
    logger.info("Waiting for new files to be added...")

    # Also run a periodic check for new files as a backup
    last_check = time.time()
    check_interval = 10  # Check every 10 seconds

    try:
        while True:
            time.sleep(1)

            # Periodic check for new files
            current_time = time.time()
            if current_time - last_check > check_interval:
                last_check = current_time

                # Check for new files
                for video_ext in VIDEO_EXTENSIONS:
                    for video_file in watch_path.glob(f"*{video_ext}"):
                        if video_file.name not in event_handler.known_files:
                            logger.info(f"Periodic check found new file: {video_file.name}")
                            event_handler.known_files.add(video_file.name)
                            event_handler.process_video(video_file)

    except KeyboardInterrupt:
        observer.stop()
        logger.info("Video watcher stopped.")

    observer.join()

if __name__ == "__main__":
    main()