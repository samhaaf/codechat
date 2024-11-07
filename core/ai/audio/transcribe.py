import os
import subprocess
import json
import time
from threading import Thread, Lock
from .utils import record_audio, join_audio_files

def transcribe_audio(audio_path, output_path=None, model='medium'):
    if output_path is None:
        output_path = '/tmp/' + os.path.basename(audio_path).rsplit('.', 1)[0] + '.json'
    command = ['whisper', '-m', model, '-o', output_path, audio_path]

    process = subprocess.Popen(command, stderr=subprocess.PIPE)
    _, stderr = process.communicate()

    if process.returncode != 0:
        print("Error running command:", stderr.decode())
        raise subprocess.CalledProcessError(process.returncode, command)

    return read_transcription(output_path)


def read_transcription(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    for transcription in data.get('transcription', []):
        if 'text' in transcription:
            return transcription['text']
    return ''


def transcribe_live_recording(kill_flag, full_transcription=[''], folder_name=None):
    if folder_name is None:
        folder_name = f'/tmp/whisper/{time.time()}'

    recording_folder = os.path.join(folder_name, 'recordings')
    transcription_folder = os.path.join(folder_name, 'transcriptions')

    os.makedirs(recording_folder)
    os.makedirs(transcription_folder)

    recording_length = 2
    join_n = 3
    model = 'medium'

    recording_thread = Thread(
        target=record_audio,
        args=(recording_folder, kill_flag, recording_length)
    )
    recording_thread.start()

    files = {}
    transcriptions = dict()  # Dictionary to store transcriptions for each file
    consecutive_files = []

    def _update_transcriptions():

        # Check for consecutive files and join if needed
        if len(consecutive_files) == join_n:
            print('Joining:', consecutive_files)
            join_audio_files(*consecutive_files)
            del consecutive_files[:]

        for name in os.listdir(recording_folder):
            files.setdefault(name, {
                'start_time': float(name.split('/')[-1].split('_')[0]),
                'duration': int(name.split('/')[-1].split('_')[1].split('.')[0]),
                'recording_path': os.path.join(recording_folder, name),
                'transcription_path': os.path.join(transcription_folder, name)[:-4] + '.json',
            })

        process_order = sorted(
            files.keys(),
            key=lambda f: (files[f]['start_time'], files[f]['duration'])
        )

        # Start first with small files and then do bigger ones (they're a luxury)
        for name in process_order:
            if name in transcriptions:
                continue

        # Transcribe and store in the dictionary
            print('Transcribing:', name)
            transcription = transcribe_audio(
                audio_path=files[name]['recording_path'],
                output_path=files[name]['transcription_path'],
                model=model
            )
            transcriptions[name] = transcription

            # smaller consecutive functions get joined
            if files[name]['duration'] == recording_length:
                consecutive_files.append(files[name]['recording_path'])

            # We want to update the transcription quickly, so we only process 1
            return True

    def _update_full_transcription():
        if len(transcriptions) == 0:
            return
        paths = sorted(
            transcriptions.keys(),
            key=lambda f: (files[f]['start_time'], -files[f]['duration'])
        )
        full_text = ""
        current_time = current_time = files[paths[0]]['start_time']
        tmp = []
        while len(paths):
            file = files[paths[0]]
            if current_time <= file['start_time']:
                full_text += transcriptions[paths[0]].strip() + " "
                current_time += file['duration']
                tmp.append(paths[0])
            del paths[0]
        full_transcription[0] = full_text
        print('Join order:', tmp)

    # Keep checking the folder for new files and transcribe them
    while not kill_flag.is_set():

        # Get the transcriptions for all files we have so far
        if _update_transcriptions():

            # Build the full transcription using the helper function
            _update_full_transcription()

    recording_thread.join()

    # Do the update one last time now that the thread is joined
    _update_transcriptions()
    _update_full_transcription()
