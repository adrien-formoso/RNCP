import wave
import tempfile
import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import os
import numpy as np
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

    def recv_queued(self, frames):
        self.frames.extend(frames)
        return frames[
            -1
        ]  # retourne le dernier pour la sortie audio (sinon silence)


ctx = webrtc_streamer(
    key="recorder",
    audio_processor_factory=AudioRecorder,
    media_stream_constraints={"video": False, "audio": True},
    async_processing=True,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },  # (optionnel mais plus stable)
)


recorded_audio_path = None

# Bloc : Enregistrement terminé
if (
    ctx.audio_processor
    and not ctx.state.playing
    and ctx.audio_processor.frames
    and recorded_audio_path
    is None  # Important : pour éviter de re-traiter à chaque rerun
):
    st.success("✅ Enregistrement terminé !")

    audio_frames = ctx.audio_processor.frames
    samples = []

    for frame in audio_frames:
        array = frame.to_ndarray().flatten()
        samples.append(array)

    audio_data = np.concatenate(samples).astype(np.int16)

    recorded_audio_path = tempfile.mktemp(suffix=".wav")
    with wave.open(recorded_audio_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(audio_data.tobytes())

    st.audio(recorded_audio_path, format="audio/wav")

    uploaded_file = None  # Force à utiliser uniquement le vocal

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
