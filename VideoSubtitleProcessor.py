# VideoSubtitleProcessor.py

import os
import subprocess
import speech_recognition as sr
from googletrans import Translator

class VideoSubtitleProcessor:
    def __init__(self, target_language='es'):
        self.target_language = target_language

    def set_target_language(self, target_language):
        self.target_language = target_language

    # Other methods as described earlier...

    def process_video(self, input_video, target_language=None):
        if target_language:
            self.set_target_language(target_language)
        base_name = os.path.splitext(input_video)[0]
        audio_path = f'{base_name}.wav'
        recognized_text_path = f'{base_name}_recognized.txt'
        translated_text_path = f'{base_name}_translated.txt'
        srt_path = f'{base_name}.srt'
        output_video = f'{base_name}_output.mp4'

        # Step 1: Extract audio from the video
        self.extract_audio(input_video, audio_path)

        # Step 2: Perform speech recognition on audio
        self.recognize_speech(audio_path, recognized_text_path)

        # Step 3: Translate recognized text
        self.translate_text(recognized_text_path, translated_text_path)

        # Step 4: Save translated text as an SRT file
        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write("1\n00:00:00,000 --> 00:00:05,000\n" + translated_text_path)

        # Step 5: Merge SRT with the original video
        self.merge_srt_with_video(input_video, srt_path, output_video)

        # Clean up temporary files
        os.remove(audio_path)
        os.remove(recognized_text_path)
        os.remove(translated_text_path)
        os.remove(srt_path)
