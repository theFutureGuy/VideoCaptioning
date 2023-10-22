from flask import Flask, render_template, request, redirect
from VideoSubtitleProcessor import VideoSubtitleProcessor
import os

app = Flask(__name__, template_folder='templates')


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


processor = VideoSubtitleProcessor(target_language='es')

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
        processor.process_video(filename)

        processing_done = True

        return render_template('index.html', processing_done=processing_done)

if __name__ == '__main__':
    app.run(debug=True)
