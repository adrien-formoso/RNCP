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
            print(f" speech_to_Text : {dream_text}\n\n\n")
            emotions = backend.text_analysis(dream_text)
            print(f" emotions : {emotions}\n\n")
            
            # Trouver l'émotion dominante
            dominant_emotion = max(emotions, key=emotions.get)
            dominant_score = emotions[dominant_emotion]
            
            st.write(f"**Émotion dominante :** {dominant_emotion.replace('_', ' ')} ({dominant_score:.2f})")
            
            prompt =  backend.text_to_prompt(dream_text)
            print(f" text_to_prompt : {prompt}\n\n")
            image =  backend.prompt_to_image(prompt)
            st.image(image)

        except Exception as e:
            st.error(f"Erreur pendant l'analyse : {e}")
else:
    st.info("Uploade un audio pour commencer !")