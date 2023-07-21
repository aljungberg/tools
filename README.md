Some of my personal tools and utilities.


# Voice Memo Transcription Script

This script is designed to automate the process of transcribing voice memos into text files. I've found that voice transcription technology has significantly improved in recent years, to the point where it has become a viable tool for daily journaling. With its efficiency and accuracy, it saves a considerable amount of time compared to traditional written notes, especially for those who may be prone to obsessing over the perfection of their written notes.

My workflow with this tool is as follows:

1.  The beauty of this process is in the 'record-and-forget' approach. I simply record my progress, thoughts and ideas, then move on with my work. This method bypasses the temptation to stop and perfect each entry as I would with written notes, eliminating a significant distraction from my workflow. I do not have to concern myself with what has been recorded until the next morning.
2. Each voice memo is automatically synced to my computer (via iCloud in my case), where this Python script picks them up. It monitors my voice memo folder using a watchdog and transcribes each new file it detects into a text file.
3. The script also measures the time between each note, which is very helpful when annotating the duration of tasks in my journal entries.
4. The following morning, I review and lightly format the previous day's notes. This review process is streamlined by the high accuracy of the transcription and, as a result, usually requires only minor corrections.
5. Naturally I pipeline the transcriptions through an LLM text model to do the initial formatting and to fix obvious transcription errors. This further minimizes the time I need to spend.

This process has been an excellent substitute for traditional journaling for me. It allows a stream of consciousness style of recording my thoughts, tasks, and ideas, aiding in focusing my mind without getting caught up in the writing process itself. I also use journalling for my personal performance metrics which are roughly "how many useful things did I do today".

This script uses OpenAI's Whisper model via [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for transcription. 

(Whisper is a little awkward to use real-time, so while initially I tried to just dictate live into my journal notes, that wasn't working well for me. The delay made it take longer than just writing, plus seeing the results on screen made me feel compelled to immediately edit and clean it up. With this script, I can just leave it running the background and when I compose my notes the next morning I basically just `cat` all the text files of yesterday in chronological order-- which is the same as alphabetical order given my naming scheme. Fire and forget.)

I hope this script can be useful to others. Check the Python script for additional details and feel free to modify it to suit your specific needs.

## Usage

Follow the instructions to build [whisper.cpp](https://github.com/ggerganov/whisper.cpp). If you're on an Apple Silicon Mac, you might want to use the ANE version since it's much faster. (That said this script is meant to just run in the background so whether it takes 10 or 30 seconds per memo doesn't really matter that much.)

```
transcribe_voice_memos.py --whisper-path /my/path/whisper.cpp/main --model-file /my/path//whisper.cpp/models/ggml-medium.en.bin --memos-path ~/Library/Mobile\ Documents/com~apple~CloudDocs/Voice\ memos --watch
```

The `--watch` flag keeps it running the background so that when you need your transcriptions they're always ready. Transcribing a day's worth of notes isn't instant but if you don't mind the delay you can just run the tool as needed without `--watch`. It's idempotent.
