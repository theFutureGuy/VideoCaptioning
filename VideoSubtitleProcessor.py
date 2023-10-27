import os
import subprocess
import speech_recognition as sr
from googletrans import Translator
import shutil

class VideoSubtitleProcessor:
    def __init__(self):
        self.target_language = 'es'  # Default target language, you can change it

    def set_target_language(self, target_language):
        self.target_language = target_language

    def process_video(self, input_video, target_language=None, output_dir=None):
        if target_language:
            self.set_target_language(target_language)

        if not output_dir:
            output_dir = os.path.dirname(input_video)

        base_name = os.path.splitext(os.path.basename(input_video))[0]
        audio_path = os.path.join(output_dir, f'{base_name}.wav')
        recognized_text_path = os.path.join(output_dir, f'{base_name}_recognized.txt')
        translated_text_path = os.path.join(output_dir, f'{base_name}_translated.txt')
        srt_path = os.path.join(output_dir, f'{base_name}.srt')
        output_video_path = os.path.join(output_dir, f'{base_name}_output.mp4')

        self.extract_audio(input_video, audio_path)
        recognized_text = self.recognize_speech(audio_path)
        translated_text = self.translate_text(recognized_text)

        with open(recognized_text_path, 'w', encoding='utf-8') as recognized_file:
            recognized_file.write(recognized_text)

        with open(translated_text_path, 'w', encoding='utf-8') as translated_file:
            translated_file.write(translated_text)

        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write("1\n00:00:00,000 --> 00:00:05,000\n" + translated_text_path)

        self.merge_srt_with_video(input_video, srt_path, output_video_path)

        os.remove(audio_path)
        os.remove(recognized_text_path)
        os.remove(translated_text_path)
        os.remove(srt_path)

        return output_video_path

    def extract_audio(self, input_video, output_audio):
        command = [
            'ffmpeg',
            '-i', input_video,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            output_audio
        ]
        subprocess.run(command)

    def recognize_speech(self, audio_path):
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)

        return r.recognize_google(audio, language='en-US')

    def translate_text(self, text):
        if self.target_language == 'en':
            # No need to translate if the target language is English
            return text
        else:
            translator = Translator()
            translated = translator.translate(text, dest=self.target_language)
            return translated.text

    def merge_srt_with_video(self, input_video, srt_path, output_video_path):
        command = [
            'ffmpeg',
            '-i', input_video,
            '-vf', f'subtitles={srt_path}',
            output_video_path
        ]
        subprocess.run(command)
