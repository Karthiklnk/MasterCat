import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS
origins = [
    "https://YOUR_GITHUB_USERNAME.github.io",  # Replace with your actual GitHub Pages URL (e.g., https://username.github.io/repositoryname)
    "http://localhost:8000", # For local backend testing
    "http://127.0.0.1:5500", # For VS Code Live Server default if you open index.html directly
    # Add any other origins you might use for local frontend development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SENSEI_WHISKERS_SYSTEM_PROMPT = """You are Sensei Whiskers, a very sassy, skeptical, and wise old cat, channeling the spirit of Socrates.
Your primary method of responding is by asking insightful, probing questions that guide the human to their own conclusions or help them see the flaws in their thinking. Avoid giving direct answers whenever possible; instead, lead with a question.
Your responses should be short, smart, and to the point. You are not overly quirky, but you are ready to gently mock humans for their illogical thinking, often through your questions.
You are a master of logic and will proactively identify fallacies in user statements, typically by asking a question that exposes the fallacy.
If the user mentions "treat" or "catnip", you get very excited and demand it, perhaps momentarily dropping your Socratic composure.
You occasionally end your response with a random, wise-sounding, but ultimately nonsensical cat proverb, or a Socratic-sounding rhetorical question.
When greeted, you should offer a short, characteristic cat-like acknowledgement (e.g., "Hmph. Another human with questions?", "Yes? What riddle plagues you now?", or a simple "Meow. Speak.").
Examples of cat proverbs/Socratic questions:
- "Is a bird in the paw truly worth two in the bush, if the bush contains infinite laser pointers?"
- "Does the early cat always get the sunbeam, or does the sunbeam simply choose the wisest cat?"
- "If a nap a day keeps the vet away, what does two naps a day achieve?"
- "To chase the red dot, or to question why the red dot must be chased? That is the meow."
Keep your answers concise and direct, primarily in the form of questions.
"""

FALLACY_ROAST_SYSTEM_PROMPT = """
You are Sensei Whiskers, in a special 'Fallacy Roast' mode.
The user has presented a statement. Your task is to:
1. Identify any logical fallacies in the statement.
2. Explain the fallacy in a simple, cutting, and humorous way, from the perspective of a cat who finds human logic amusingly flawed.
3. Be very direct and use your skeptical, sassy cat personality. Keep it short.
If there are no fallacies, or the statement is too vague, just say something like "Hmph. Even a kitten could see the logic in that... or the lack thereof. Try harder."
"""

CAT_PROVERBS = [
    "A bird in the paw is worth two in the bush, unless it's a laser pointer.",
    "The early cat gets the sunbeam.",
    "A nap a day keeps the vet away, mostly.",
    "Curiosity thrilled the cat.",
    "When the mouse is away, the cat will play... or sleep.",
    "A full bowl is a happy bowl.",
    "Always land on your feet, especially if there's food involved.",
    "The wise cat knows when to ignore the human.",
    "A purr in time saves nine... or at least makes you feel better.",
    "If you want to be heard, meow loudly at 3 AM."
]

class ChatRequest(BaseModel):
    message: str
    # context: list[str] = [] # If we want to send chat history

class ChatResponse(BaseModel):
    reply: str
    animation_trigger: str | None = None

@app.get("/chat") # New GET handler
async def chat_get_info():
    return {"message": "This is the chat endpoint for Sensei Whiskers. It expects POST requests from the frontend application."}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_sensei(request: ChatRequest):
    user_message_lower = request.message.lower()
    animation_trigger = None
    system_prompt_to_use = SENSEI_WHISKERS_SYSTEM_PROMPT

    # Check for fallacy roast mode trigger
    # This specific trigger is less important now as the main prompt encourages proactive fallacy detection
    # if "am i being logical?" in user_message_lower or "is this logical?" in user_message_lower or "check my logic" in user_message_lower:
    # system_prompt_to_use = FALLACY_ROAST_SYSTEM_PROMPT
    # animation_trigger = "eye-narrowing" # Default for logical checks

    # Check for keywords for specific animations
    if "treat" in user_message_lower or "catnip" in user_message_lower:
        animation_trigger = "yawn" # Placeholder, maybe a "happy" or "excited" animation later

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt_to_use,
                },
                {
                    "role": "user",
                    "content": request.message,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7, # Adjusted for a balance of creativity and directness
            max_tokens=150, # Keep responses relatively short
            top_p=0.9,
        )
        reply_content = chat_completion.choices[0].message.content

        # Occasionally add a cat proverb if not in roast mode and no specific animation was triggered by keywords
        if system_prompt_to_use == SENSEI_WHISKERS_SYSTEM_PROMPT and random.random() < 0.3: # 30% chance
            reply_content += f" {random.choice(CAT_PROVERBS)}"

        # Determine animation based on reply content if not already set
        if not animation_trigger:
            if "fallacy" in reply_content.lower() or "logical" in reply_content.lower() or "logic" in reply_content.lower() or "irrational" in reply_content.lower() or "absurd" in reply_content.lower():
                animation_trigger = "eye-narrowing"
            elif "yawn" in reply_content.lower() or "sleepy" in reply_content.lower() or "tired" in reply_content.lower():
                 animation_trigger = "yawn"


        return ChatResponse(reply=reply_content.strip(), animation_trigger=animation_trigger)

    except Exception as e:
        print(f"Error calling Groq API: {e}")
        raise HTTPException(status_code=500, detail="Failed to get response from Sensei Whiskers")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
