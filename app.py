import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import os
import subprocess
import uuid

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

        # ---------------- UNIQUE SESSION ID (IMPORTANT FIX) ----------------
        session_id = str(uuid.uuid4())

        fixed_path = f"/tmp/fixed_{session_id}.mp4"
        output_path = f"/tmp/output_{session_id}.mp4"
        srt_path = f"/tmp/captions_{session_id}.srt"

        # ---------------- SAVE INPUT ----------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            temp.write(uploaded_file.read())
            input_path = temp.name

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

        # ---------------- TRANSCRIBE ----------------
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

        # ---------------- SAFE DOWNLOAD (IMPORTANT FIX) ----------------
        with open(output_path, "rb") as f:
            video_bytes = f.read()

        st.download_button(
            "⬇ Download Captioned Video",
            data=video_bytes,
            file_name="captioned.mp4",
            mime="video/mp4"
        )
