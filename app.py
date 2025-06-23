# Solution native Streamlit - Pas besoin d'installation supplémentaire !

import streamlit as st
import tempfile
import backend

st.set_page_config(page_title="Onyria", page_icon="✨", layout="centered")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('style.css')

# CSS pour personnaliser la barre audio générée par Streamlit
st.markdown(
    '''
    <style>
    /* Container principal centré */
    .main-container {
        text-align: center;
    }
    
    /* Centrer le composant audio_input */
    .stAudioInput {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin: 2rem auto !important;
    }
    
    /* Style pour la barre audio générée automatiquement */
    .stAudio {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
    }
    
    /* Style des résultats */
    .results-block {
        background: rgba(118, 75, 162, 0.1);
        border-left: 4px solid #764ba2;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
    }
    
    /* Style pour le label du composant */
    .stAudioInput label {
        color: #764ba2 !important;
        font-weight: bold !important;
        font-size: 18px !important;
        text-align: center !important;
        margin-bottom: 1rem !important;
    }
    </style>
    ''',
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Logo
with open("./RNCP/logo_base64.txt", "r") as f:
    base64_logo = f.read().strip()

logo_html = f'''
<div class="logo-container">
    <img src="data:image/png;base64,{base64_logo}" alt="Onyria Logo" />
</div>
'''

st.markdown(logo_html, unsafe_allow_html=True)
st.markdown('<p class="intro">Vos rêves, révélés</p>', unsafe_allow_html=True)

# Centrer le composant audio_input
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Utiliser st.audio_input (natif Streamlit)
    audio_bytes = st.audio_input(
        "Enregistrez votre rêve", key="dream_audio_input"
    )

# Traitement de l'audio
if audio_bytes is not None:
    # Sauvegarder l'audio temporairement
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(audio_bytes.getvalue())
        audio_file = tmpfile.name

    # Garder SEULEMENT la barre de lecture générée automatiquement par st.audio_input
    # (pas besoin d'ajouter st.audio() car st.audio_input le fait déjà)

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

        dream_classification = backend.classify_dream_from_emotions(emotions)
        st.markdown(
            f'<div class="results-block"><b>Classification :</b> {dream_classification}</div>',
            unsafe_allow_html=True,
        )
        
        interpretations = backend.interpret_dream_with_ai(dream_text)
        st.markdown(
            "<h3 style='text-align:center; color: #764ba2;'>Interprétation du rêve</h3>",
            unsafe_allow_html=True,
        )
        for approche, interpretation in interpretations.items():
            st.markdown(
                f'<div class="results-block"><b>{approche}</b> : {interpretation}</div>',
                unsafe_allow_html=True,
            )

        prompt = backend.text_to_prompt(dream_text)
        image = backend.prompt_to_image(prompt)
        st.image(image, caption="Visualisation de votre rêve")

    except Exception as e:
        st.error(f"Erreur : {str(e)}")

else:
    st.info("Cliquez sur le microphone pour enregistrer votre rêve")

st.markdown('</div>', unsafe_allow_html=True)