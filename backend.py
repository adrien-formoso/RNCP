# backend.py

import os
from dotenv import load_dotenv
from groq import Groq
from mistralai import Mistral

load_dotenv()

groq_clinet = Groq()
mistral_client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def create_transcription(file,language="fr"):

    transcription = groq_clinet.audio.transcriptions.create(
        file=file, # Required audio file
        model="whisper-large-v3-turbo", # Required model to use for transcription
        prompt="Specify context or spelling",  # Optional
        response_format="verbose_json",  # Optional
        timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
        language=language,  # Optional
        temperature=0.0  # Optional
        )
    return transcription


def speech_to_Text(file ,file_type = "file",language="fr",path=None):

    # Open the audio file
    if file_type=="file":
        transcription = create_transcription(file)

    else:
        with open(file, "rb") as file:
            transcription = create_transcription(file)

    return transcription.text
    
def text_to_prompt(dream_text):
    
    chat_completion = groq_clinet.chat.completions.create(
        messages=[
            # Set an optional system message. This sets the behavior of the
            # assistant and can be used to provide specific instructions for
            # how it should behave throughout the conversation.
            {
                "role": "system",
                "content": "Tu est un de pormpt ingenieur. Genere moi un prompt pour generer une image de ce rêve. Je ne veux pas de conseil, juste le prompt. Je veux le rêve en 6 phrases maximum. Je veux tous les détails"
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": dream_text,
            }
        ],

        # The language model which will generate the completion.
        model="llama-3.3-70b-versatile"
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
        }
    )

    response = mistral_client.beta.conversations.start(
        agent_id=mistral_image_agent.id,
        inputs=prompt
    )


    file_id = response.outputs[1].content[1].file_id


    # Download using the ToolFileChunk ID
    file_bytes = mistral_client.files.download(file_id=file_id).read()

    # Save the file locally
    with open(r"/Users/ad/Documents/RNCP/test_data/final_image.png", "wb") as file:
        file.write(file_bytes)

    return file_bytes



if __name__ == "__main__":
    test_data = r"/Users/ad/Documents/RNCP/test_data/crabe.m4a"
    dream_text = speech_to_Text(test_data,file_type="path")
    print(f" speech_to_Text : {dream_text}\n\n\n")
    prompt = text_to_prompt(dream_text)
    print(f" text_to_prompt : {prompt}\n\n")
    image = prompt_to_image(prompt)


