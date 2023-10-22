from flask import Flask, render_template, request, redirect, url_for
from VideoSubtitleProcessor import VideoSubtitleProcessor
import os



app = Flask(__name__, template_folder='templates')

# Path to the directory where video files are uploaded
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Path to the directory where output videos will be stored
OUTPUT_DIR = 'output_videos'

processor = VideoSubtitleProcessor()

@app.route('/')
def index():
    return render_template('index.html', processing_done=False)

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Get the selected target language from the form
        target_language = request.form.get('target_language')

        processed_video_path = processor.process_video(filename, target_language, output_dir=OUTPUT_DIR)

        # Provide a link to download the processed video
        return render_template('index.html', processing_done=True, video_path=processed_video_path)

if __name__ == '__main__':
    app.run(debug=True)
