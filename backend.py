import os
import json
from dotenv import load_dotenv
from groq import Groq
from mistralai import Mistral
from datetime import datetime
import math 

load_dotenv()

groq_client = Groq() 
mistral_client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()

def softmax(predictions):
    exp_values = {k: math.exp(v) for k, v in predictions.items()}
    total = sum(exp_values.values())
    return {k: v / total for k, v in exp_values.items()}



def create_transcription(file, language="fr"):
    transcription = groq_client.audio.transcriptions.create(
        file=file,
        model="whisper-large-v3-turbo",
        prompt="Specify context or spelling",
        response_format="verbose_json",
        timestamp_granularities=["word", "segment"],
        language=language,
        temperature=0.0,
    )
    return transcription


def speech_to_Text(file, file_type="file", language="fr", path=None):
    if file_type == "file":
        transcription = create_transcription(file)
    else:
        with open(file, "rb") as file:
            transcription = create_transcription(file)
    
    return transcription.text


def text_analysis(text):
    chat_response = mistral_client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "system",
                "content": read_file("context_emotion.txt"),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        response_format={"type": "json_object"},
    )

    emotions = json.loads(chat_response.choices[0].message.content)
    return softmax(emotions)

    
def get_dominant_emotion_and_score(emotions):
    dominant_emotion = max(emotions, key=emotions.get)
    return dominant_emotion, emotions[dominant_emotion]

def classify_dream_from_emotions(emotions):
    with open('reference_emotions.json') as file:
        reference_emotions_dict = json.load(file)

    positif = reference_emotions_dict["positif"]
    negatif = reference_emotions_dict["negatif"]

    # filtrer les émotions effectivement présentes
    pos_vals = [emotions[e] for e in positif if e in emotions]
    neg_vals = [emotions[e] for e in negatif if e in emotions]

    # moyenne sur le nombre réel
    score_positif = sum(pos_vals) / len(pos_vals) if pos_vals else 0
    score_negatif = sum(neg_vals) / len(neg_vals) if neg_vals else 0

    if score_negatif > score_positif:
        return "cauchemar"
    else:
        return "rêve"



def text_to_prompt(dream_text):
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Tu est un de pormpt ingenieur. Genere moi un prompt pour generer une image de ce rêve. Je ne veux pas de conseil, juste le prompt. Je veux le rêve en 6 sentences maximum. Je veux tous les détails",
            },
            {
                "role": "user",
                "content": dream_text,
            },
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content


def prompt_to_image(prompt):
    mistral_image_agent = mistral_client.beta.agents.create(
        model="mistral-medium-2505",
        name="Image Generation Agent",
        description="Agent used to generate images.",
        instructions="Use the image generation tool when you have to create images.",
        tools=[{"type": "image_generation"}],
        completion_args={
            "temperature": 0.3,
            "top_p": 0.95,
        },
    )

    response = mistral_client.beta.conversations.start(
        agent_id=mistral_image_agent.id, inputs=prompt
    )

    file_id = response.outputs[1].content[1].file_id
    file_bytes = mistral_client.files.download(file_id=file_id).read()

    output_dir = "./generated_images"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dream_image_{timestamp}.png"
    file_path = os.path.join(output_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    print(f"Image saved at: {file_path}")
    return file_bytes


if __name__ == "__main__":
    test_data = r"./RNCP/test_data/crabe.m4a"
    dream_text = speech_to_Text(test_data, file_type="path")
    print(f" speech_to_Text : {dream_text}\n\n\n")
    emotions = text_analysis(dream_text)
    print(f" emotions : {emotions}\n\n")
    prompt = text_to_prompt(dream_text)
    print(f" text_to_prompt : {prompt}\n\n")
    image = prompt_to_image(prompt)