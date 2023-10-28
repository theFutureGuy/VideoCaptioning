from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from googletrans import Translator

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output_videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class VideoSubtitleProcessor:
    def __init__(self, input_video, target_language='es'):
        self.input_video = input_video
        self.target_language = target_language
        self.output_dir = os.path.join(OUTPUT_FOLDER, os.path.splitext(os.path.basename(input_video))[0])

    def process_video(self):
        # Extract audio from the video
        audio_path = os.path.join(self.output_dir, 'audio.wav')
        self.extract_audio(audio_path)

        # Recognize speech from the audio
        recognized_text_path = os.path.join(self.output_dir, 'recognized.txt')
        self.recognize_speech(audio_path, recognized_text_path)

        # Translate the recognized text to the target language
        translated_text_path = os.path.join(self.output_dir, f'translated_{self.target_language}.txt')
        self.translate_text(recognized_text_path, translated_text_path)

        # Generate SRT subtitles
        srt_filename = os.path.join(self.output_dir, f'subtitles_{self.target_language}.srt')
        self.generate_srt(translated_text_path, srt_filename)

        # Merge SRT subtitles with the video
        output_video = os.path.join(self.output_dir, 'output.mp4')
        self.merge_srt_with_video(output_video, srt_filename)
        return output_video

    def extract_audio(self, output_audio):
        video_clip = VideoFileClip(self.input_video)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio)

    def recognize_speech(self, audio_path, recognized_text_path):
        # Implement speech recognition here or use your preferred method
        # Replace the following lines with your recognition code
        recognized_text = "Recognized text from audio\nLine 2\nLine 3"
        with open(recognized_text_path, 'w', encoding='utf-8') as text_file:
            text_file.write(recognized_text)

    def translate_text(self, text_path, translated_text_path):
        translator = Translator()
        with open(text_path, 'r', encoding='utf-8') as text_file:
            text = text_file.read()

        translated = translator.translate(text, dest=self.target_language)
        translated_text = translated.text

        with open(translated_text_path, 'w', encoding='utf-8') as translated_file:
            translated_file.write(translated_text)

    def generate_srt(self, translated_text_path, srt_filename):
        with open(translated_text_path, 'r', encoding='utf-8') as text_file:
            lines = text_file.readlines()
            frame_duration = 2.0  # Adjust as needed

            with open(srt_filename, 'w', encoding='utf-8') as srt_file:
                for i, line in enumerate(lines):
                    start_time = i * frame_duration
                    end_time = (i + 1) * frame_duration
                    srt_file.write(f"{i+1}\n{self.format_time(start_time)} --> {self.format_time(end_time)}\n{line}\n\n")

    def merge_srt_with_video(self, output_video, srt_filename):
        temp_audio_file = 'temp_audio.wav'
        ffmpeg_extract_subclip(self.input_video, 0, 1, targetname=temp_audio_file)
        video_clip = VideoFileClip(self.input_video)
        audio_clip = VideoFileClip(temp_audio_file)
        audio_duration = audio_clip.duration

        clips = []

        with open(srt_filename, 'r', encoding='utf-8') as srt_file:
            lines = srt_file.readlines()
            for i in range(0, len(lines), 4):
                start_time, end_time, text = lines[i + 2].strip(), lines[i + 3].strip(), lines[i + 1].strip()
                start_time = self.parse_time(start_time)
                end_time = self.parse_time(end_time)
                if start_time < audio_duration:
                    sub_audio_clip = audio_clip.subclip(start_time, end_time)
                    sub_audio_clip = sub_audio_clip.volumex(0)
                    sub_video_clip = TextClip(text, fontsize=24, color='white', bg_color='black')
                    sub_video_clip = sub_video_clip.set_audio(sub_audio_clip)
                    clips.append(sub_video_clip)

        final_clip = CompositeVideoClip(clips)
        final_clip = final_clip.set_audio(audio_clip)

        final_clip.write_videofile(output_video, codec="libx264", audio_codec="aac")

        os.remove(temp_audio_file)

    def parse_time(self, time_str):
        hours, minutes, seconds = map(float, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    def format_time(self, time):
        hours, remainder = divmod(time, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},000"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            target_language = request.form['target_language']
            processor = VideoSubtitleProcessor(filename, target_language)
            output_video = processor.process_video()
            return redirect(url_for('download', filename=output_video))

    return render_template('index.html')

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    app.run(debug=True)
