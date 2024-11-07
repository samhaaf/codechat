import pyaudio
from pydub import AudioSegment
import os
import time

def record_audio(folder_name, kill_flag, seconds_per_file=5):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    print("recording...")
    start_time = time.time()
    save_count = 0

    while not kill_flag.is_set():
        frames = []
        for i in range(0, int(RATE / CHUNK * seconds_per_file)):
            data = stream.read(CHUNK)
            frames.append(data)

        # Combine frames into a pydub.AudioSegment object
        byte_data = b''.join(frames)
        audio_segment = AudioSegment(
            byte_data,
            frame_rate=RATE,
            sample_width=audio.get_sample_size(FORMAT),
            channels=CHANNELS
        )

        # Save to file
        filename = os.path.join(folder_name, f"{start_time+(save_count*seconds_per_file)}_{seconds_per_file}.wav")
        audio_segment.export(filename, format='wav')

        save_count += 1

    print("finished recording")



def join_audio_files(*audio_files):
    combined = AudioSegment.empty()
    dir_name = os.path.dirname(audio_files[0])
    first_epoch = audio_files[0].split('/')[-1].split('_')[0]
    total_duration = 0
    for file in audio_files:
        duration = int(file.split('/')[-1].split('_')[1].split('.')[0])
        assert os.path.dirname(file) == dir_name, "All files should be from the same directory"
        audio = AudioSegment.from_wav(file)
        combined += audio
        total_duration += duration
    combined.export(f"{dir_name}/{first_epoch}_{total_duration}.wav", format='wav')


def split_audio_file(dir_name, file_name, split_time):
    audio = AudioSegment.from_wav(os.path.join(dir_name, file_name))
    first_half, second_half = audio[:split_time * 1000], audio[split_time * 1000:]
    original_epoch, original_duration = file_name.split('_')
    original_duration = original_duration.split('.')[0]
    first_half.export(os.path.join(dir_name, f"{original_epoch}_{split_time}.wav"), format='wav')
    second_half.export(os.path.join(dir_name, f"{int(original_epoch) + split_time}_{int(original_duration) - split_time}.wav"), format='wav')
