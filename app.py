from flask import Flask, render_template, request, redirect
from VideoSubtitleProcessor import VideoSubtitleProcessor
import os

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output_videos'

processor = VideoSubtitleProcessor()

@app.route('/')
def index():
    return render_template('index.html', processing_done=False, video_path=None)

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
        target_language = request.form.get('target_language')
        output_video_path = processor.process_video(filename, target_language, app.config['OUTPUT_FOLDER'])

        return render_template('index.html', processing_done=True, video_path=output_video_path)

if __name__ == '__main__':
    app.run()
