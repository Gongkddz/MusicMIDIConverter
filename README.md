# MusicMIDIConverter
将音频文件转换为指定格式，并从转换后的音频文件中识别出音高曲线和歌词。然后将音高曲线转换为MIDI音符，将歌词转换为拼音，并将生成的MIDI文件导出。主要使用了pydub、pyaudio、aubio、os、numpy、pypinyin和midiutil等库来实现这些功能。
## 依赖库

- pydub
- pyaudio
- numpy
- midiutil
- scipy
- pypinyin
- librosa

## 依然存在的问题
- 音高识别不准确
- 生成的midi格式错乱
- 无法安装aubio库
