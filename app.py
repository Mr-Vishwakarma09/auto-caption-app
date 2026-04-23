import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from faster_whisper import WhisperModel
import tempfile
import os

st.title("Auto Caption Generator 🎬")

uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

if uploaded_file:

    if st.button("Generate Captions"):

        st.info("Processing... ⚡ Please wait")

        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
            temp_input.write(uploaded_file.read())
            input_path = temp_input.name

        # 🔥 Step 1: Normalize video using FFmpeg (CRITICAL FIX)
        fixed_path = "fixed.mp4"
        os.system(f"ffmpeg -y -i {input_path} -vcodec libx264 -acodec aac {fixed_path}")

        # 🔥 Step 2: Load video safely
        try:
            video = VideoFileClip(fixed_path)
        except Exception as e:
            st.error("❌ Error loading video. Try another file.")
            st.stop()

        # Limit duration (MVP safety)
        if video.duration > 30:
            st.error("❌ Video too long! Keep it under 30 seconds.")
            st.stop()

        # 🔥 Step 3: Load Whisper model (lightweight)
        model = WhisperModel("tiny")

        # Transcribe audio
        segments, _ = model.transcribe(fixed_path)

        clips = [video]

        # Caption position (bottom-safe zone)
        y_pos = video.h * 0.88

        # 🔥 Step 4: Add captions
        for segment in segments:
            txt = segment.text.strip()

            if txt:
                text_clip = (
                    TextClip(
                        txt,
                        fontsize=45,
                        color="white",
                        stroke_color="black",
                        stroke_width=2,
                        method="caption",
                        size=(video.w * 0.8, None)
                    )
                    .set_position(("center", y_pos))
                    .set_start(segment.start)
                    .set_end(segment.end)
                )

                clips.append(text_clip)

        # 🔥 Step 5: Combine video + captions
        final = CompositeVideoClip(clips)

        # Export
        output_path = "output.mp4"
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24
        )

        st.success("✅ Done!")

        # Download button
        with open(output_path, "rb") as f:
            st.download_button(
                "Download Captioned Video",
                f,
                file_name="captioned_video.mp4"
            )
