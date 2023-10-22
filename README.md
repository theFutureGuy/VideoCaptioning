# Video Subtitle Processor

Video Subtitle Processor is a web application that allows users to upload videos for automated audio-to-text transcription and the generation of subtitled output videos using FFmpeg.

## Features

- **Video Processing**: Upload your video files for automated audio-to-text transcription.
- **Subtitle Generation**: Generate subtitled videos with translated text.
- **Download Output**: Get a download link for the processed video with subtitles.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python Dependencies**: Install the required Python packages using `pip`:
    ```
    pip install flask googletrans==3.1.1
    ```

- **FFmpeg**: Ensure you have FFmpeg installed on your system. You can download it from [FFmpeg website](https://ffmpeg.org/download.html).

## Setup

1. Clone the repository:
    ```
    git clone https://github.com/yourusername/VideoSubtitleProcessor.git
    cd VideoSubtitleProcessor
    ```

2. Run the Flask application:
    ```
    python app.py
    ```

3. Access the web application in your browser at `http://localhost:5000`.

## Usage

1. Choose a video file for processing and select your target language.
2. Click "Process Video" to initiate the transcription and translation.
3. Once processing is complete, you will receive a download link for the processed video.

- `app.py`: The Flask application code.
- `VideoSubtitleProcessor.py`: The video processing class code.
- `templates/`: A directory for HTML templates used in the Flask app.
- `uploads/`: The directory where the original input videos are stored.
- `output_videos/`: The directory where the processed output videos will be stored.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the FFmpeg community for providing the powerful FFmpeg tool.

## Author

- A Ashiq /(https://github.com/theFutureGuy)


# Still under construction but open for contribution.

