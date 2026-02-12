# Video Transcription Processor

A Docker-based application that automatically watches for video files and transcribes them using Whisper.cpp.

## Features

- **Automatic Video Detection**: Watches a specified folder for new video files (MP4, MKV, AVI, MOV, etc.)
- **Audio Extraction**: Uses FFmpeg to extract audio from video files
- **Fast Transcription**: Utilizes Whisper.cpp (C++ implementation) for high-performance transcription
- **Markdown Output**: Saves transcriptions as formatted Markdown documents
- **Docker Best Practices**: Runs as non-root user, multi-stage build, proper layer caching

## Supported Video Formats

- MP4, MKV, AVI, MOV, WMV, FLV, WEBM, M4V, MPG, MPEG

## Prerequisites

- Docker and Docker Compose
- Video files to transcribe
- Sufficient disk space for video processing

## Installation

### Using Docker Compose (Recommended)

1. Update your `.env` file with the paths:
```bash
# Video Processor Configuration
VIDEO_WATCH_DIR=/path/to/your/video/folder
VIDEO_OUTPUT_DIR=/path/to/your/output/folder
```

2. The service is already configured in the main `docker-compose.yml`. Simply run:
```bash
docker-compose up -d video-processor
```

### Standalone Docker

1. Build the image:
```bash
cd video_processor
docker build -t video-transcriber .
```

2. Run the container:
```bash
docker run -d \
  --name video-transcriber \
  -v /path/to/watch:/watch \
  -v /path/to/output:/output \
  -e WATCH_DIR=/watch \
  -e OUTPUT_DIR=/output \
  video-transcriber
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WATCH_DIR` | Directory to watch for video files | `/watch` |
| `OUTPUT_DIR` | Directory to save transcriptions | `/output` |
| `WHISPER_MODEL` | Path to Whisper model file | `/models/ggml-base.en.bin` |
| `WHISPER_BIN` | Path to Whisper binary | `/usr/local/bin/whisper` |

### Whisper Models

The default build uses the `base.en` model (English-only, ~140MB). You can modify the Dockerfile to use different models:

- `tiny.en` - Fastest, least accurate (~39MB)
- `base.en` - Good balance (default, ~140MB)
- `small.en` - Better accuracy (~466MB)
- `medium.en` - High accuracy (~1.5GB)
- `large` - Best accuracy, multilingual (~2.9GB)

To change the model, modify this line in the Dockerfile:
```dockerfile
RUN ./models/download-ggml-model.sh base.en
```

## Usage

1. Place video files in your configured watch directory
2. The service will automatically detect new video files
3. Processing includes:
   - Audio extraction to WAV format
   - Transcription using Whisper.cpp
   - Saving results as Markdown documents
4. Check the output directory for transcription files named: `{video_name}_{timestamp}.md`

## Output Format

Transcriptions are saved as Markdown files with the following structure:

```markdown
# Video Transcription: example.mp4

## Metadata
- **Source File**: example.mp4
- **File Path**: /watch/example.mp4
- **Transcription Date**: 2024-01-25 14:30:00
- **File Size**: 125.50 MB

## Transcription

[Transcribed text content here]

---
*Transcribed using Whisper.cpp*
```

## Monitoring

View logs:
```bash
docker-compose logs -f video-processor
```

Check processing status:
```bash
docker exec video-transcriber ls -la /output
```

## Performance Notes

- Whisper.cpp is significantly faster than the Python implementation
- Processing speed depends on:
  - Video length
  - Model size
  - Available CPU cores
  - System RAM
- The container uses 4 threads by default (adjustable in `watcher.py`)

## Troubleshooting

### Container won't start
- Verify the watch and output directories exist
- Check directory permissions

### No transcriptions appearing
- Check logs: `docker-compose logs video-processor`
- Ensure video files are in supported formats
- Verify FFmpeg is working: `docker exec video-transcriber ffmpeg -version`

### Slow processing
- Consider using a smaller Whisper model
- Increase thread count in `watcher.py`
- Ensure sufficient system resources

### Permission issues
- The container runs as non-root user `appuser`
- Ensure mounted directories are accessible

## Development

To modify the watcher behavior:

1. Edit `watcher.py`
2. Rebuild the image: `docker-compose build video-processor`
3. Restart the service: `docker-compose restart video-processor`

## Security Considerations

- Runs as non-root user
- Minimal base image (debian-slim)
- No unnecessary packages installed
- Isolated file system access through volume mounts

## License

This project uses:
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) - MIT License
- [FFmpeg](https://ffmpeg.org/) - LGPL/GPL License
- Python Watchdog - Apache 2.0 License