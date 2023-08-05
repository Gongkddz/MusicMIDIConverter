import pydub
import pydub.playback
import pyaudio
import aubio
import os
import numpy as np
from pypinyin import pinyin, Style
from midiutil import MIDIFile


def convert_audio_format(audio_file, output_format):
    sound = pydub.AudioSegment.from_file(audio_file)
    output_file = os.path.splitext(audio_file)[0] + '.' + output_format
    sound.export(output_file, format=output_format)
    return output_file


def get_pitch_curve(audio_file):
    downsample = 1
    samplerate = 44100 // downsample

    win_s = 4096 // downsample
    hop_s = 512 // downsample

    s = aubio.source(audio_file, samplerate, hop_s)
    samplerate = s.samplerate

    tolerance = 0.8
    pitch_o = aubio.pitch("yin", win_s, hop_s, samplerate)
    pitch_o.set_tolerance(tolerance)

    pitches = []
    confidences = []

    total_frames = 0
    while True:
        samples, read = s()
        pitch = pitch_o(samples)[0]
        confidence = pitch_o.get_confidence()

        if confidence < 0.8:
            pitch = 0

        pitches += [pitch]
        confidences += [confidence]

        total_frames += read
        if read < hop_s:
            break

    return pitches


def recognize_lyrics(audio_file):
    sound = pydub.AudioSegment.from_file(audio_file)
    lyrics = sound.export(format="wav")

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
    pinyin_lyrics = pinyin(lyrics, style=Style.NORMAL)
    return pinyin_lyrics


if __name__ == "__main__":
    audio_file = "your_audio_file.mp3"

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

    # 导出midi文件
    export_midi(midi_file, "output.midi")