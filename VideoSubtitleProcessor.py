import os
import subprocess
import shutil
import speech_recognition as sr
from googletrans import Translator
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

class VideoSubtitleProcessor:
    def __init__(self, target_language='es'):
        self.target_language = target_language

    def set_target_language(self, target_language):
        self.target_language = target_language

    def process_video(self, input_video, target_language=None, output_dir=None):
        if target_language:
            self.set_target_language(target_language)

        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(input_video), "output_videos")

        os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

        base_name = os.path.splitext(os.path.basename(input_video))[0]
        audio_path = os.path.join(output_dir, f'{base_name}.wav')
        recognized_text_path = os.path.join(output_dir, f'{base_name}_recognized.txt')
        translated_text_path = os.path.join(output_dir, f'{base_name}_translated.txt')
        srt_dir = os.path.join(output_dir, 'srt_frames')
        os.makedirs(srt_dir, exist_ok=True)  # Create the SRT frames directory

        self.extract_audio(input_video, audio_path)
        self.recognize_speech(audio_path, recognized_text_path)
        self.translate_text(recognized_text_path, translated_text_path)

        # Generate SRT subtitles for each frame
        self.generate_srt_frames(input_video, srt_dir)

        # Merge SRT frames with the video
        output_video = os.path.join(output_dir, f'{base_name}_output.mp4')
        self.merge_srt_with_video(input_video, srt_dir, output_video)

        os.remove(audio_path)
        os.remove(recognized_text_path)
        os.remove(translated_text_path)
        shutil.rmtree(srt_dir) 

        return output_video

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
        if self.target_language == 'en':
            shutil.copy(text_path, translated_text_path)
        else:
            translator = Translator()
            with open(text_path, 'r', encoding='utf-8') as text_file:
                text = text_file.read()

            translated = translator.translate(text, dest=self.target_language)
            translated_text = translated.text

            with open(translated_text_path, 'w', encoding='utf-8') as translated_file:
                translated_file.write(translated_text)

    def generate_srt_frames(self, input_video, srt_dir):
        clip = VideoFileClip(input_video)
        frame_rate = clip.fps

        translated_text_path = f'{os.path.splitext(input_video)[0]}_translated.txt'
        with open(translated_text_path, 'r', encoding='utf-8') as text_file:
            translated_text = text_file.read().splitlines()

        frame_duration = 1 / frame_rate

        for i, text in enumerate(translated_text):
            start_time = i * frame_duration
            end_time = (i + 1) * frame_duration
            srt_filename = os.path.join(srt_dir, f'{i:04d}.srt')

            with open(srt_filename, 'w', encoding='utf-8') as srt_file:
                srt_file.write(f"{i + 1}\n{self.format_time(start_time)} --> {self.format_time(end_time)}\n{text}")

    def merge_srt_with_video(self, input_video, srt_dir, output_video):
        temp_audio_file = 'temp_audio.wav'
        ffmpeg_extract_subclip(input_video, 0, 1, targetname=temp_audio_file)
        video_clip = VideoFileClip(input_video)
        audio_clip = VideoFileClip(temp_audio_file)
        audio_duration = audio_clip.duration

        clips = []

        for srt_file in sorted(os.listdir(srt_dir)):
            srt_path = os.path.join(srt_dir, srt_file)
            start_time, end_time, text = self.parse_srt(srt_path)

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

    def format_time(self, time):
        hours, remainder = divmod(time, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},000'

    def parse_srt(self, srt_path):
        with open(srt_path, 'r', encoding='utf-8') as srt_file:
            lines = srt_file.readlines()
            start_time, end_time = map(lambda x: x.strip(), lines[1].split("-->"))
            text = lines[2].strip()
        return start_time, end_time, text

if __name__ == "__main__":
    processor = VideoSubtitleProcessor(target_language='hi')  
    input_video = 'path/to/your/input_video.mp4'  
    output_video = processor.process_video(input_video)
    print(f"Processed video saved to: {output_video}")
