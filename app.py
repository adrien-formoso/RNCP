# app.py

import streamlit as st
from backend import describe_image

st.set_page_config(page_title="Conseiller de Coupe Taquin", page_icon="💇‍♂️")

st.title("💇‍♂️ Assistant Coiffure Taquin")
st.markdown("Bienvenue ! Envoie une photo et prépare-toi à te faire gentiment vanner tout en recevant des conseils de coupe de cheveux. 😎")

uploaded_file = st.file_uploader("📸 Uploade une photo de ton visage (format JPEG ou PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Voici ta magnifique tronche.", use_container_width=True)

    if st.button("💬 Obtenir une recommandation (et quelques vannes)"):
        with st.spinner("Analyse en cours... prépare ton ego."):
            try:
                response = describe_image(uploaded_file)
                st.markdown("### 💇‍♂️ Recommandation & Roast :")
                st.write(response)
            except Exception as e:
                st.error(f"Erreur pendant l'analyse : {e}")
else:
    st.info("Uploade une photo pour commencer !")
