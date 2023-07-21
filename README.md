Some of my personal tools and utilities.


# Voice Memo Transcription Script

This script is designed to automate the process of transcribing my voice memos into text files. I've found that voice transcription technology has significantly improved in recent years, to the point where it has become a viable tool for daily journaling. It saves a considerable amount of time compared to traditional written notes, especially for those of us who may be prone to obsessing over the perfection of their written notes.

<i>Example of my continuous journalling transcriptions. Meandering content provided for illustrative purposes only. Do not try to replicate at home.</i>

<img width="871" alt="Screenshot showing terminal output of voice memos being transcribed with time information." src="https://github.com/aljungberg/tools/assets/154423/8994a2ea-eee3-4be4-a7d6-bfd3342fcbb6">

My workflow with this tool is as follows:

1.  The beauty of this process is in the 'record-and-forget' approach. I simply record my progress, thoughts and ideas, then move on with my work. This method bypasses the temptation to stop and perfect each entry as I would with written notes, eliminating a significant distraction from my workflow. I do not have to concern myself with what has been recorded until the next morning.
2. Each voice memo is automatically synced to my computer (via iCloud in my case), where this Python script picks them up. It monitors my voice memo folder using a watchdog and transcribes each new file it detects into a text file.
3. The script also measures the time between each note, which is very helpful when annotating the duration of tasks in my journal entries.
4. The following morning, I review and lightly format the previous day's notes. This review process is streamlined by the high accuracy of the transcription and, as a result, usually requires only minor corrections.
5. Naturally I pipeline the transcriptions through an LLM text model to do the initial formatting and to fix obvious transcription errors. This further minimizes the time I need to spend.

This process has been an excellent substitute for traditional journaling for me. It allows a stream of consciousness
style of recording my thoughts, tasks, and ideas, aiding in focusing my mind without getting caught up in the writing
process itself. I also use journalling for my personal performance metrics which are roughly "how many useful things did
I do today".

This script uses OpenAI's Whisper model via [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for transcription.

(Whisper is a little awkward to use real-time, so while initially I tried to just dictate live into my journal notes,
that wasn't working well for me. The delay made it take longer than just writing, plus seeing the results on screen made
me feel compelled to immediately edit and clean it up. With this script, I can just leave it running the background and
when I compose my notes the next morning I basically just `cat` all the text files of yesterday in chronological order--
which is the same as alphabetical order given my naming scheme. Fire and forget.)

I hope this script can be useful to others. Check the Python script for additional details and feel free to modify it to
suit your specific needs.

## Installation and Usage

Briefly:

```bash
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
bash ./models/download-ggml-model.sh base.en
make -j
cd ..
git clone git@github.com:aljungberg/tools.git atools
cd atools
# use your venv of choice, then
pip install -r requirements.txt
```

Follow the instructions to build [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for more options. If you're on an Apple Silicon
Mac, you might want to use the ANE version since it's much faster. (That said this script is meant to just run in the
background so whether it takes 10 or 30 seconds per memo doesn't really matter that much.)

Now you can run the script:

```bash
python transcribe_voice_memos.py --whisper-path ../whisper.cpp/main --model-file ../whisper.cpp/models/ggml-base.en.bin --memos-path ~/Library/Mobile\ Documents/com~apple~CloudDocs/Voice\
memos --watch
```

The `--watch` flag keeps it running the background so that when you need your transcriptions they're always ready. Transcribing a day's worth of notes isn't instant but if you don't mind the delay you can just run the tool as needed without `--watch`. It's idempotent.

## Memo Recorder

How you do your memos is up to you! Here's my method. 

I use an iPhone Shortcut to record a memo. I wanted a "push to record" experience, and this is close enough. The micro-app is on my home screen and launches basically instantly. I tap to finish the recording. The output files are named with date and time, and at least in my UK locale the lexographic and chronological sort order is the same. 

I've set it to save to an iCloud folder. The memos appear on my Mac moments later for the transcription script to pick up on. This screenshot shows the core of it (there's some extra stuff related to pausing music while I record, omitted for clarity):

<div><img alt="A handy voice memo Apple Shortcut." src="https://github.com/aljungberg/tools/assets/154423/ee819fc9-ebf0-4b90-a5f4-efce6e08f323" width="300"/></div>
