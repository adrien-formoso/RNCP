import streamlit as st
from audio_recorder_streamlit import audio_recorder
import backend
import tempfile

st.set_page_config(page_title="Onyria", page_icon="✨", layout="centered")


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


load_css('style.css')

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(
    '<h1 class="main-title">✨ Onyria</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="intro">Bienvenue ! Vos rêves, révélés</p>',
    unsafe_allow_html=True,
)

recorded_audio = audio_recorder(
    recording_color="#c34fff",
    neutral_color="#764ba2",
    icon_name="microphone-alt",
    icon_size="3x",
    key="dream_recorder",
    text="Raconte ton rêve",
)

audio_file = None
if recorded_audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(recorded_audio)
        audio_file = tmpfile.name

    st.audio(recorded_audio, format="audio/wav")

    with st.spinner("Analyse en cours..."):
        try:
            dream_text = backend.speech_to_Text(audio_file, file_type="path")

            st.success("Transcription :")
            st.markdown(
                f'<div class="results-block">{dream_text}</div>',
                unsafe_allow_html=True,
            )

            emotions = backend.text_analysis(dream_text)

            dominant_emotion, dominant_score = (
                backend.get_dominant_emotion_and_score(emotions)
            )
            st.markdown(
                f'<div class="results-block"><b>Émotion dominante :</b> {dominant_emotion.replace("_", " ")} ({dominant_score:.2f})</div>',
                unsafe_allow_html=True,
            )

            dream_classification = backend.classify_dream_from_emotions(
                emotions
            )
            st.markdown(
                f'<div class="results-block"><b>Type de rêve détecté :</b> {dream_classification}</div>',
                unsafe_allow_html=True,
            )

            interpretations = backend.interpret_dream_with_ai(dream_text)
            st.markdown(
                "<h3 style='text-align:center;'>Interprétation du rêve</h3>",
                unsafe_allow_html=True,
            )
            for approche, interpretation in interpretations.items():
                st.markdown(
                    f'<div class="results-block"><b>{approche}</b> : {interpretation}</div>',
                    unsafe_allow_html=True,
                )

            prompt = backend.text_to_prompt(dream_text)
            image = backend.prompt_to_image(prompt)
            st.image(image)

        except Exception as e:
            st.error(f"Erreur pendant l'analyse : {e}")

else:
    st.info("Commence par enregistrer ton rêve")

st.markdown('</div>', unsafe_allow_html=True)
