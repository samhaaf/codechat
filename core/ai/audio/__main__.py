import os
import threading
import time
from .transcribe import transcribe_live_recording, transcribe_audio

def main():
    folder_name = f"recordings/{time.time()}"
    kill_flag = threading.Event()
    full_transcription = ['']
    transcription_thread = threading.Thread(
        target=transcribe_live_recording,
        args=(kill_flag, full_transcription, folder_name)
    )
    transcription_thread.start()
    try:
        last_value = None
        while True:
            if last_value != full_transcription[0]:
                last_value = full_transcription[0]
                print()
                print(last_value)
                print()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Interrupt received, stopping recording...")
        kill_flag.set()
        transcription_thread.join()  # Wait for the thread to terminate
        print("Recording and transcription have stopped.")

if __name__ == "__main__":
    main()
