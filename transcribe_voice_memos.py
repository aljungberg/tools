import argparse
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# whisper.cpp timestamping annotation
pattern = re.compile(r'\[(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)\] (.*)')


def transcribe_file(args, m4a_file, prev_end_time):
    """Transcribe.

    Note that we assume `prev_end_time` is always the end time of the penultimate transcription chronologically. So you need to call this method with the files sorted by date and time. (When using the watch feature, we implicitly assume that every new file that appears is newer than the previous one, which would be true if you're recording voice memos on your phone and syncing them to your computer like I do.)
    """

    m4a_path = os.path.join(args.memos_path, m4a_file)

    transcript_file = os.path.splitext(m4a_file)[0] + '.txt'
    transcript_path = os.path.join(args.memos_path, transcript_file)

    # Check if transcription file exists and it is not older than the M4A file. This makes the script idempotent.
    if os.path.exists(transcript_path) and os.path.getmtime(transcript_path) > os.path.getmtime(m4a_path):
        # Make sure to update the prev_end_time as if we had transcribed the file.
        with open(transcript_path, 'r') as tf:
            lines = tf.readlines()
            last_line = lines[-1].strip()
            if last_line.endswith('.'):
                last_line = last_line[:-1]
            _, time_string = last_line.split("Memo ended at ")
            return datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")

    sys.stderr.write(f"Transcribing {m4a_file}...\n")

    # Parse date and time from the file name
    date_string = m4a_file.split("Recording ")[1].split(" at ")[0]
    time_string = m4a_file.split(" at ")[1].split(".m4a")[0]
    datetime_string = f"{date_string} {time_string}"
    recording_datetime = datetime.strptime(datetime_string, "%Y-%m-%d %H.%M.%S")

    # Convert M4A to temporary WAV file because whisper.cpp only supports wav. My files are named "Audio Recording 2023-07-17 at 13.16.43.m4a". So change this as needed for your own purposes, or use ctime.
    temp_wav_path = os.path.join(args.memos_path, "temp.wav")
    subprocess.run(["ffmpeg", "-y", "-i", m4a_path, "-ar", "16000", temp_wav_path], stderr=subprocess.DEVNULL)

    # Transcribe the temporary WAV file using whisper.cpp. Tip: if on a modern Mac, compile the version that runs on the Apple Neural Engine, it's much faster. If you've done it right the ANE model is used automatically.
    transcription_command = [
        args.whisper_path,
        "--model",
        args.model_file,
        temp_wav_path,
    ]
    if (result := subprocess.run(transcription_command, capture_output=True, text=True)).returncode != 0:
        raise Exception("Transcription error: " + result.stderr)

    # Write to the transcription text file
    with open(transcript_path, 'w') as tf:
        def write(_line):
            """Output to both stdout and the transcription file."""
            print(_line)
            tf.write(_line + '\n')

        # Every time a new day starts, print a new header. I use this when converting to journal entries.
        if prev_end_time is None or prev_end_time.date() != recording_datetime.date():
            write(f"First memo of day at {recording_datetime.strftime('%Y-%m-%d %H:%M:%S')}:")
            prev_end_time = recording_datetime
        else:
            write(f"New memo at {recording_datetime.strftime('%Y-%m-%d %H:%M:%S')}:")

        for line in result.stdout.splitlines():
            if match := pattern.match(line):
                start_time_str, end_time_str, transcript = match.groups()
                start_offset = datetime.strptime(start_time_str, "%H:%M:%S.%f").time()
                end_offset = datetime.strptime(end_time_str, "%H:%M:%S.%f").time()

                start_time = recording_datetime + timedelta(hours=start_offset.hour, minutes=start_offset.minute, seconds=start_offset.second, microseconds=start_offset.microsecond)
                end_time = recording_datetime + timedelta(hours=end_offset.hour, minutes=end_offset.minute, seconds=end_offset.second, microseconds=end_offset.microsecond)

                time_since_prev = start_time - prev_end_time
                if time_since_prev >= timedelta(minutes=1):
                    minutes = time_since_prev.seconds // 60
                    # These "x minutes later" lines are useful when converting to journal entries, giving me a quick gauge for how long I spent doing something between two voice memos. Since I push the text through a generative AI for first pass formatting, this really helps there too (current AI not being great at math, they're helped by having an explicit "x minutes later" line rather than timestamps).
                    write(f"[ {minutes} minutes later... ]")

                adjusted_line = f"> {transcript.strip()}"
                write(adjusted_line)
                prev_end_time = end_time
            else:
                # Ignore blank lines but fail on other unexpected lines
                if line.strip():
                    raise ValueError(f"Unexpected line: {line}")

        write(f"Memo ended at {prev_end_time.strftime('%Y-%m-%d %H:%M:%S')}.")

    os.remove(temp_wav_path)
    return prev_end_time


class M4AEventHandler(FileSystemEventHandler):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def on_modified(self, event):
        if event.src_path.endswith(".m4a"):
            self.fn(event.src_path)

    def on_created(self, event):
        if event.src_path.endswith(".m4a"):
            self.fn(event.src_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--whisper-path', type=str, required=True, help='Path to the whisper.cpp binary')
    parser.add_argument('--model-file', type=str, required=True, help='Path to the whisper model file')
    parser.add_argument('--memos-path', type=str, required=True, help='Path to the directory containing the voice memos')
    parser.add_argument('--watch', action='store_true', help='Keep the script running and watch for new or changed M4A files')
    args = parser.parse_args()

    last_end_time = None


    def transcribe_one(m4a_file):
        global last_end_time
        last_end_time = transcribe_file(args, m4a_file, last_end_time)


    # Get a sorted list of M4A files in the directory
    m4a_files = sorted([f for f in os.listdir(args.memos_path) if f.endswith(".m4a")])
    sys.stderr.write(f"Found {len(m4a_files)} recordings.\n")
    for fname in m4a_files:
        transcribe_one(fname)

    if args.watch:
        # Make sure not to start the watcher until after the initial transcription is done. We need `prev_end_time` to be up to date.
        event_handler = M4AEventHandler(transcribe_one)
        observer = Observer()
        observer.schedule(event_handler, args.memos_path, recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(5)  # keep the script running
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
