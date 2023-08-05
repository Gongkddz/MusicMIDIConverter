import pydub
import pydub.playback
import pyaudio
import os
import numpy as np
from midiutil import MIDIFile
from scipy.signal import argrelextrema
from pypinyin import pinyin, Style
import librosa


def convert_audio_format(audio_file, output_format):
    sound = pydub.AudioSegment.from_file(audio_file)
    output_file = os.path.splitext(audio_file)[0] + '.' + output_format
    sound.export(output_file, format = output_format)
    return output_file


def get_pitch_curve(audio_file):
    sound = pydub.AudioSegment.from_file(audio_file)
    samples = np.array(sound.get_array_of_samples())
    sample_rate = sound.frame_rate

    downsample = 1
    samplerate = sample_rate // downsample

    win_s = 4096 // downsample
    hop_s = 512 // downsample

    pitches = []
    confidences = []

    total_frames = 0
    samples_length = len(samples)
    while total_frames + hop_s < samples_length:
        current_frame = total_frames / hop_s
        current_sample = int(current_frame * hop_s)
        current_samples = samples[current_sample:current_sample + hop_s]

        pitch = calculate_pitch(current_samples, sample_rate)
        confidence = calculate_confidence(current_samples)

        if confidence < 0.8 or pitch <= 0:  # 添加条件过滤无效的音高
            pitch = 0

        pitches.append(pitch)
        confidences.append(confidence)

        total_frames += hop_s

    return pitches


def calculate_pitch(samples, sample_rate):
    autocorr = np.correlate(samples, samples, mode = 'full')
    autocorr = autocorr[len(autocorr) // 2:]

    peaks = argrelextrema(autocorr, np.greater)[0]

    if len(peaks) == 0:
        return 0

    pitch_period = peaks[0] / sample_rate
    pitch = 1 / pitch_period

    return pitch


def calculate_confidence(samples):
    energy = np.sum(np.square(samples))
    if energy <= 0:  # 添加错误处理代码，处理能量为零或负值的情况
        return 0

    log_energy = np.log(energy)
    if np.isinf(log_energy):  # 添加错误处理代码，处理log无效值
        return 0

    confidence = log_energy / np.log(len(samples))

    return confidence


def recognize_lyrics(audio_file):
    sound = pydub.AudioSegment.from_file(audio_file)
    lyrics = sound.export(format = "wav")

    return lyrics


def convert_pitch_to_midi(pitches):
    midi_file = MIDIFile(1)
    track = 0
    channel = 0
    time = 0
    duration = 1

    for pitch in pitches:
        if pitch != 0:
            note = int(69 + 12 * np.log2(pitch / 440))
            midi_file.addNote(track, channel, note, time, duration, 100)
        time += 1

    return midi_file


def export_midi(midi_file, output_file):
    with open(output_file, 'wb') as file:
        midi_file.writeFile(file)


def convert_lyrics_to_pinyin(lyrics):
    lyrics = str(lyrics)
    pinyin_lyrics = pinyin(lyrics, style = Style.NORMAL)
    return pinyin_lyrics


def calculate_bpm(audio_file):
    y, sr = librosa.load(audio_file)
    tempo, beat_frames = librosa.beat.beat_track(y = y, sr = sr)
    return round(tempo, 2)


if __name__ == "__main__":
    audio_file = r"C:\Users\admin\OneDrive - Optimistrans\桌面\祖龙吟\【言和】祖龙吟【桂月 & 熊】【和声付】_01_主旋律.wav"

    # 转换音频格式
    converted_audio_file = convert_audio_format(audio_file, "wav")

    # 识别音高曲线
    pitch_curve = get_pitch_curve(converted_audio_file)

    # 识别歌词
    lyrics = recognize_lyrics(converted_audio_file)

    # 将音高转换为midi音符
    midi_file = convert_pitch_to_midi(pitch_curve)

    # 将歌词转换为拼音
    pinyin_lyrics = convert_lyrics_to_pinyin(lyrics)

    # 计算曲速
    bpm = calculate_bpm(converted_audio_file)

    print("BPM:", bpm)

    # 导出midi文件
    export_midi(midi_file, "output.mid")
