import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import os
import subprocess

# ---------------- TIME FORMAT ----------------
def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

# ---------------- UI ----------------
st.title("🎬 Auto Caption Generator (Pro Mode)")

uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_file:

    if st.button("Generate Captions ⚡"):

        st.info("Processing video... Please wait ⏳")

        # ---------------- SAVE INPUT ----------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            temp.write(uploaded_file.read())
            input_path = temp.name

        fixed_path = "fixed.mp4"
        output_path = "output.mp4"
        srt_path = "captions.srt"

        # ---------------- SAFE FFMPEG CONVERT ----------------
        subprocess.run([
            "ffmpeg", "-y",
            "-i", input_path,
            "-vcodec", "libx264",
            "-acodec", "aac",
            fixed_path
        ])

        # ---------------- LOAD MODEL (SMALL) ----------------
        model = WhisperModel("small", compute_type="int8")

        # ---------------- TRANSCRIBE (IMPROVED ACCURACY) ----------------
        segments, _ = model.transcribe(
            fixed_path,
            beam_size=5,
            vad_filter=True,
            temperature=0.0
        )

        # ---------------- CREATE SRT ----------------
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments):

                start = seg.start
                end = seg.end
                text = seg.text.strip()

                f.write(f"{i+1}\n")
                f.write(f"{format_time(start)} --> {format_time(end)}\n")
                f.write(f"{text}\n\n")

        # ---------------- BURN SUBTITLES ----------------
        subprocess.run([
            "ffmpeg", "-y",
            "-i", fixed_path,
            "-vf", f"subtitles={srt_path}",
            output_path
        ])

        st.success("Done Captions Generated")

        # ---------------- DOWNLOAD ----------------
        with open(output_path, "rb") as f:
            st.download_button(
                "⬇ Download Captioned Video",
                f,
                file_name="captioned.mp4"
            )
