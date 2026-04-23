import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import os


# 🔥 MUST be defined first
def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)

    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"


st.title("Auto Caption Generator 🎬")

uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_file:

    if st.button("Generate Captions"):

        st.info("Processing... ⚡")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            temp.write(uploaded_file.read())
            input_path = temp.name

        fixed_path = "fixed.mp4"
        os.system(f"ffmpeg -y -i {input_path} -vcodec libx264 -acodec aac {fixed_path}")

        model = WhisperModel("tiny")

        segments, _ = model.transcribe(fixed_path)

        srt_path = "captions.srt"
        with open(srt_path, "w") as f:
            for i, seg in enumerate(segments):
                start = seg.start
                end = seg.end
                text = seg.text.strip()

                f.write(f"{i+1}\n")
                f.write(f"{format_time(start)} --> {format_time(end)}\n")
                f.write(f"{text}\n\n")

        output_path = "output.mp4"
        os.system(f"ffmpeg -y -i {fixed_path} -vf subtitles={srt_path} {output_path}")

        st.success("Done")

        with open(output_path, "rb") as f:
            st.download_button("Download Video", f, file_name="captioned.mp4")
