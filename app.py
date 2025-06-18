import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import tempfile
import os

import backend

st.set_page_config(page_title="Synthétiseur de rêve", page_icon="✨")
st.title("✨ Synthétiseur de rêve")
st.markdown(
    "Bienvenue ! Envoie ou enregistre ton rêve et prépare-toi à le voir de tes yeux 😎"
)

# -- Section 1 : Upload de fichier
uploaded_file = st.file_uploader(
    "🔈 Ou upload un fichier audio (m4a, mp4)", type=["m4a", "mp4"]
)

# -- Section 2 : Enregistrement micro
st.markdown("---")
st.subheader("🎤 Enregistre ton rêve directement ici :")


class AudioRecorder(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.frames.append(frame)
        return frame


ctx = webrtc_streamer(
    key="recorder",
    audio_processor_factory=AudioRecorder,
    media_stream_constraints={"video": False, "audio": True},
    async_processing=True,
)

recorded_audio_path = None

if (
    ctx.audio_processor
    and not ctx.state.playing
    and ctx.audio_processor.frames
):
    st.success("✅ Enregistrement terminé !")

    # Enregistrer temporairement l'audio en .wav
    recorded_audio_path = tempfile.mktemp(suffix=".wav")
    container = av.open(recorded_audio_path, mode='w', format='wav')
    stream = container.add_stream("pcm_s16le")

    for frame in ctx.audio_processor.frames:
        for packet in stream.encode(frame):
            container.mux(packet)

    container.close()
    st.audio(recorded_audio_path, format="audio/wav")

# -- Traitement commun
if uploaded_file or recorded_audio_path:
    st.markdown("---")
    st.subheader("🧠 Analyse en cours...")

    with st.spinner("Transcription du rêve..."):
        try:
            if uploaded_file:
                dream_text = backend.speech_to_Text(uploaded_file)
            else:
                with open(recorded_audio_path, "rb") as f:
                    dream_text = backend.speech_to_Text(f)

            st.markdown("### ✍️ Texte extrait")
            st.write(dream_text)

            prompt = backend.text_to_prompt(dream_text)
            st.markdown("### 🪄 Prompt généré")
            st.code(prompt)

            image_path = backend.prompt_to_image(prompt)
            st.markdown("### 🖼️ Image de ton rêve")
            st.image(image_path)

        except Exception as e:
            st.error(f"Erreur pendant l’analyse : {e}")
else:
    st.info(
        "Tu peux uploader un fichier **ou enregistrer directement ton rêve vocalement** 🎤."
    )
