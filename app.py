import streamlit as st
from audio_recorder_streamlit import audio_recorder
import backend
import tempfile

st.set_page_config(page_title="Synthétiseur de rêve", page_icon="✨")

# Chargement du fichier CSS externe
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Chargement des styles
load_css('style.css')

st.markdown('<h1 class="main-title">✨ Synthétiseur de rêve</h1>', unsafe_allow_html=True)
st.markdown('<p class="intro">Bienvenue ! Enregistre ton rêve et prépare-toi à le voir de tes yeux 😎</p>', unsafe_allow_html=True)

recorded_audio = audio_recorder(
    recording_color="#ff4757",
    neutral_color="#667eea",
    icon_name="microphone-alt",
    icon_size="3x",
    key="dream_recorder",
    text="Raconte ton rêve"
)

audio_file = None
if recorded_audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(recorded_audio)
        audio_file = tmpfile.name

    st.audio(recorded_audio, format="audio/wav")

    # Si un fichier audio est disponible, on lance l'analyse
    with st.spinner("Analyse en cours..."):
        try:
            dream_text = backend.speech_to_Text(audio_file, file_type="path")

            st.success("Transcription :")
            st.write(dream_text)

            emotions = backend.text_analysis(dream_text)

            # Détermination de l'émotion dominante
            dominant_emotion, dominant_score = backend.get_dominant_emotion_and_score(emotions)
            st.write(
                f"**Émotion dominante :** {dominant_emotion.replace('_', ' ')} ({dominant_score:.2f})"
            )

            # Détermination du type de rêve
            dream_classification = backend.classify_dream_from_emotions(emotions)
            st.write(f"**Type de rêve détecté :** {dream_classification}")

            # Interprétation multi-courants via IA
            interpretations = backend.interpret_dream_with_ai(dream_text)
            st.markdown("### 🧠 Interprétation du rêve")
            for approche, interpretation in interpretations.items():
                st.markdown(f"**{approche}** : {interpretation}")

            # Génération de l'image du rêve 
            prompt = backend.text_to_prompt(dream_text)
            image = backend.prompt_to_image(prompt)
            st.image(image)



        except Exception as e:
            st.error(f"Erreur pendant l'analyse : {e}")
