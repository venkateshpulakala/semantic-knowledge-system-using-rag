import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(question, retrieved_docs):

    # Check whether relevant documents exist
    if not retrieved_docs:
        return "I couldn't find relevant information in your documents."


    # Prepare context from retrieved documents
    context = ""

    for doc in retrieved_docs:

        context += f"""
        Source: {doc['metadata']['source']}
        Page: {doc['metadata']['page']}

        Content:
        {doc['text']}

        -------------------------
        """


    # Create prompt
    prompt = f"""
    You are an intelligent document assistant.

    Answer the user's question using ONLY the
    information provided in the context.

    Instructions:
    1. Do not use external knowledge.
    2. Do not make up information.
    3. If the answer is not available in the
       context, clearly say so.
    4. Give clear and simple answers.
    5. Mention relevant sources whenever possible.

    Context:
    {context}

    User Question:
    {question}

    Answer:
    """


    # Send request to Groq
    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
    )


    # Extract generated answer
    answer = response.choices[0].message.content

    return answer.strip()