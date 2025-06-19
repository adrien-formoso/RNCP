import streamlit as st
from audio_recorder_streamlit import audio_recorder
import backend
import tempfile

st.set_page_config(page_title="Synthétiseur de rêve", page_icon="✨")
st.title("✨ Synthétiseur de rêve")
st.markdown(
    "Bienvenue ! Envoie ton rêve et prépare-toi à le voir de tes yeux 😎"
)

# Choix entre upload ou micro
input_method = st.radio(
    "Méthode d'entrée :",
    ["Uploader un fichier", "Enregistrer avec le micro 🎙️"],
)

audio_file = None

if input_method == "Uploader un fichier":
    uploaded_file = st.file_uploader(
        "🔈 Uploade ton rêve", type=["m4a", "mp3", "wav"]
    )
    if uploaded_file:
        audio_file = uploaded_file

elif input_method == "Enregistrer avec le micro 🎙️":
    st.markdown(
        "Clique sur le bouton ci-dessous pour démarrer l'enregistrement puis reclique pour l'arrêter."
    )
    recorded_audio = audio_recorder()

    if recorded_audio:
        # Crée un fichier temporaire avec le contenu audio enregistré
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".wav"
        ) as tmpfile:
            tmpfile.write(recorded_audio)
            audio_file = tmpfile.name
        st.audio(recorded_audio, format="audio/wav")

# Si un fichier audio est disponible (upload ou micro), on lance l'analyse
if audio_file is not None:
    with st.spinner("Analyse en cours..."):
        try:
            if isinstance(audio_file, str):  # Si c’est un chemin (micro)
                dream_text = backend.speech_to_Text(
                    audio_file, file_type="path"
                )
            else:  # Si c’est un fichier uploadé
                dream_text = backend.speech_to_Text(audio_file)

            st.success("Transcription :")
            st.write(dream_text)

            prompt = backend.text_to_prompt(dream_text)
            st.markdown("**Prompt généré :**")
            st.code(prompt)

            image = backend.prompt_to_image(prompt)
            st.image(image)
            dream_text = backend.speech_to_Text(uploaded_file)
            emotions = backend.text_analysis(dream_text)
            
            # Détermination de l'émotion dominante
            dominant_emotion = max(emotions, key=emotions.get)
            dominant_score = emotions[dominant_emotion]
            st.write(f"**Émotion dominante :** {dominant_emotion.replace('_', ' ')} ({dominant_score:.2f})")
            
            # Détermination du type de rêve
            label = backend.classify_dream_from_emotions(emotions)
            st.write(f"**Type de rêve détecté :** {label}")

            # Génération d'image
            prompt = backend.text_to_prompt(dream_text)
            image = backend.prompt_to_image(prompt)
            st.image(image)

        except Exception as e:
            st.error(f"Erreur pendant l'analyse : {e}")
else:
    st.info("Commence par uploader ou enregistrer un audio.")
