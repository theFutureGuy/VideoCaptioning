import os
import subprocess
import speech_recognition as sr
from googletrans import Translator

class VideoSubtitleProcessor:
    def __init__(self, target_language='es'):
        self.target_language = target_language

    def set_target_language(self, target_language):
        self.target_language = target_language

    def process_video(self, input_video, target_language=None):
        if target_language:
            self.set_target_language(target_language)
        base_name = os.path.splitext(input_video)[0]
        audio_path = f'{base_name}.wav'
        recognized_text_path = f'{base_name}_recognized.txt'
        translated_text_path = f'{base_name}_translated.txt'
        srt_path = f'{base_name}.srt'
        output_video = f'{base_name}_output.mp4'

        self.extract_audio(input_video, audio_path)
        self.recognize_speech(audio_path, recognized_text_path)
        self.translate_text(recognized_text_path, translated_text_path)

        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write("1\n00:00:00,000 --> 00:00:05,000\n" + translated_text_path)

        self.merge_srt_with_video(input_video, srt_path, output_video)

        os.remove(audio_path)
        os.remove(recognized_text_path)
        os.remove(translated_text_path)
        os.remove(srt_path)

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

    def recognize_speech(self, audio_path, recognized_text_path):
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)

        recognized_text = r.recognize_google(audio, language='en-US')

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

    def merge_srt_with_video(self, input_video, srt_path, output_video):
        command = [
            'ffmpeg',
            '-i', input_video,
            '-vf', f'subtitles={srt_path}',
            output_video
        ]
        subprocess.run(command)
