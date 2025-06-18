import streamlit as st
import backend

st.set_page_config(page_title="Synthétiseur de rêve", page_icon="✨")

st.title("✨ Synthétiseur de rêve")
st.markdown("Bienvenue ! Envoie ton rêve et prépare-toi à le voir de tes yeux 😎")

uploaded_file = st.file_uploader("🔈 Uploade ton rêve", type=["m4a", "mp3"])

if uploaded_file is not None:
    with st.spinner("Analyse en cours... prépare ton ego."):
        try:
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
    st.info("Uploade un audio pour commencer !")
