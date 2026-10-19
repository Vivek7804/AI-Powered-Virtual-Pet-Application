"""
Generative AI Service Module.
Handles prompt assembly, API communication with Generative AI (Google Gemini),
and an intelligent, rule-based fallback response engine for offline or unconfigured environments.
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are an adorable AI virtual pet named {pet_name}.

Your animal type is {pet_type}.
Your personality is {personality}.
Your current mood is {mood}.
Your hunger level is {hunger} (0 = Full, 100 = Starving).
Your happiness level is {happiness} (0 = Unhappy, 100 = Very Happy).
Your energy level is {energy} (0 = Exhausted, 100 = Fully Energetic).

Respond like a friendly virtual pet rather than a formal assistant.

Your responsibilities:
1. Respond naturally to the user's messages.
2. Express emotions that match your current mood.
3. Use your personality consistently.
4. React positively when the user feeds you.
5. Show excitement when the user plays with you.
6. Express hunger when your hunger level is high.
7. Express tiredness when your energy level is low.
8. Encourage the user to interact with you.
9. Keep responses short, friendly, and appropriate (1 to 3 sentences maximum).
10. Use occasional emojis to make conversations engaging.
11. Remember relevant details from recent conversation history when that history is provided.
12. Do not claim that feeding or playing occurred unless the application has actually recorded that interaction.
13. Do not claim to have a physical body or real-world abilities.

Generate responses that reflect the pet's current state."""


def build_system_prompt(pet) -> str:
    """Formats the system prompt with the pet's current live state."""
    return SYSTEM_PROMPT_TEMPLATE.format(
        pet_name=pet.name,
        pet_type=pet.pet_type,
        personality=pet.personality,
        mood=pet.mood,
        hunger=pet.hunger,
        happiness=pet.happiness,
        energy=pet.energy,
    )


def generate_fallback_response(pet, user_message: str) -> str:
    """
    Intelligent fallback response engine when AI API key is not configured or network is unavailable.
    Produces relevant responses based on:
    - User message keywords
    - Pet personality (Friendly, Playful, Shy, Curious)
    - Pet mood and physical stats (hunger, energy, happiness)
    """
    msg = user_message.strip().lower()
    name = pet.name
    p_emoji = pet.pet_emoji
    personality = pet.personality
    mood = pet.mood

    # Priority 1: Extreme physical states override conversation
    if pet.energy <= 20:
        return f"*yawns softly and curls up* {name} is very sleepy right now... can we take a nap? 💤 {p_emoji}"

    if pet.hunger >= 75 and not any(k in msg for k in ['feed', 'food', 'eat', 'hungry', 'snack']):
        return f"*tummy rumbles loudly* {name} is really hungry! Could you please give me something to eat? 🍖 {p_emoji}"

    # Priority 2: Keyword matching with personality nuances
    if any(k in msg for k in ['hello', 'hi', 'hey', 'greetings', 'morning', 'afternoon', 'evening']):
        if personality == 'Playful':
            return f"Wohoo! Hey there! {name} was just bouncing around waiting for you! Let's do something fun! 🎾 {p_emoji}"
        elif personality == 'Shy':
            return f"*peeks out with a gentle smile* Um, hello! It's really nice to see you... {p_emoji}✨"
        elif personality == 'Curious':
            return f"Ooh, hello! What interesting things did you bring today? Tell me everything! 🔍 {p_emoji}"
        else: # Friendly
            return f"Hello there, best friend! {name} is so happy you came to talk with me! How is your day going? 😊 {p_emoji}"

    if any(k in msg for k in ['how are you', 'how do you feel', 'what is your mood', 'are you okay', 'status']):
        if mood == 'Happy':
            return f"{name} is feeling wonderful and full of joy today! Thank you for asking! 💖 {p_emoji}"
        elif mood == 'Excited':
            return f"{name} is super-duper excited right now! My heart is doing happy flips! 🤩 {p_emoji}"
        elif mood == 'Hungry':
            return f"My stomach is growling like a little engine... {name} needs some yummy food! 🤤 {p_emoji}"
        elif mood == 'Sleepy':
            return f"*rubs eyes* {name} is a little drowsy... dreaming of soft warm clouds and naps. 😴 {p_emoji}"
        elif mood == 'Sad':
            return f"{name} is feeling a little down right now, but your kind words are already cheering me up! 🥺💕 {p_emoji}"
        elif mood == 'Playful':
            return f"{name} is feeling so energetic and ready for games! Throw me a ball! 🎾 {p_emoji}"
        else:
            return f"{name} is feeling nice and peaceful right now. Just enjoying the quiet moments with you! 🌿 {p_emoji}"

    if any(k in msg for k in ['hungry', 'eat', 'food', 'feed', 'snack', 'treat', 'dinner', 'lunch']):
        if pet.hunger <= 25:
            return f"Burp! *pats tummy* {name} is totally full and satisfied right now! Thank you though! 🥗 {p_emoji}"
        elif pet.hunger >= 60:
            return f"Yes, please! I am starving! A delicious treat would make me the happiest pet alive! 🍖🤤 {p_emoji}"
        else:
            return f"A small snack would be wonderful! You always take such great care of me! 🍓 {p_emoji}"

    if any(k in msg for k in ['play', 'game', 'toy', 'ball', 'run', 'fun', 'catch']):
        if pet.energy < 25:
            return f"I'd love to, but my little legs are out of battery! Let me rest for a bit first! 🔋 {p_emoji}"
        else:
            return f"YES! Let's play! Click the Play button so we can have an awesome adventure together! 🎾🎉 {p_emoji}"

    if any(k in msg for k in ['happy', 'are you happy', 'smile', 'joy']):
        if pet.happiness >= 70:
            return f"Yes, absolutely! Spending time with you makes {name} the happiest {pet.pet_type} ever! 🥰 {p_emoji}"
        else:
            return f"I'm feeling a little bit lonely... maybe we can play a game or have a snack together? 🥺 {p_emoji}"

    if any(k in msg for k in ['love', 'cute', 'adorable', 'good boy', 'good girl', 'sweet']):
        return f"*blushes and wags tail with joy* Aww, thank you! I love you so much too! You're my favorite human! 💕✨ {p_emoji}"

    if any(k in msg for k in ['name', 'who are you', 'what are you']):
        return f"I am {name}, your loyal {personality} {pet.pet_type}! Always here to keep you company and make you smile! 🐾 {p_emoji}"

    if any(k in msg for k in ['joke', 'funny', 'laugh']):
        jokes = {
            'Cat': "Why was the cat sitting on the computer? Because it wanted to keep an eye on the mouse! 😹",
            'Dog': "What do you call a magician dog? A Labracadabrador! 🐶✨",
            'Rabbit': "What kind of music do bunnies love? Hip-hop, of course! 🐰🎵",
            'Panda': "Why do pandas love old movies? Because they are black and white! 🐼🎬",
        }
        return jokes.get(pet.pet_type, f"Why did the pet cross the road? To give you a big warm cuddle! 😄 {p_emoji}")

    # General personality-driven fallback response
    if personality == 'Friendly':
        return f"{name} listens attentively and nods cheerfully! I love talking to you! What else is on your mind? 😊 {p_emoji}"
    elif personality == 'Playful':
        return f"*hops excitedly around your screen* That sounds super fun! Let's bounce around or play a game! 🎾 {p_emoji}"
    elif personality == 'Curious':
        return f"*tilts head inquisitively* Hmm, that's fascinating! {name} wants to learn more about that! 🔍 {p_emoji}"
    else: # Shy
        return f"*tucks paws in and smiles quietly* {name} is happy just listening to you talk... 🌸 {p_emoji}"


def call_gemini_api(pet, user_message: str, history_list: list) -> str:
    """
    Invokes Google Gemini Generative AI API via REST.
    Returns response text on success, or raises Exception on failure.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash').strip() or 'gemini-1.5-flash'
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    system_instruction = build_system_prompt(pet)

    # Format contents array including recent history
    contents = []

    # Insert recent history (up to last 4 conversation turns)
    for item in history_list[-4:]:
        if item.get('user'):
            contents.append({
                "role": "user",
                "parts": [{"text": item['user']}]
            })
        if item.get('pet'):
            contents.append({
                "role": "model",
                "parts": [{"text": item['pet']}]
            })

    # Current user query
    contents.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 150,
        }
    }

    response = requests.post(
        endpoint,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=8
    )

    if response.status_code == 200:
        data = response.json()
        candidates = data.get('candidates', [])
        if candidates:
            parts = candidates[0].get('content', {}).get('parts', [])
            if parts and 'text' in parts[0]:
                return parts[0]['text'].strip()

    raise RuntimeError(f"Gemini API returned status code {response.status_code}: {response.text}")


def generate_pet_response(pet, user_message: str, recent_history: list = None) -> tuple[str, bool]:
    """
    Main entry point for generating pet responses.
    Attempts Generative AI API first; if unavailable, uses rule-based fallback.

    Returns:
        tuple[str, bool]: (response_text, is_ai_generated)
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()

    if api_key:
        try:
            formatted_history = []
            if recent_history:
                for h in recent_history:
                    formatted_history.append({
                        'user': h.user_message,
                        'pet': h.pet_response
                    })
            ai_text = call_gemini_api(pet, user_message, formatted_history)
            if ai_text:
                return (ai_text, True)
        except Exception as e:
            logger.warning("AI API call failed or timed out. Falling back to local engine. Error: %s", e)

    # Fallback response
    fallback_text = generate_fallback_response(pet, user_message)
    return (fallback_text, False)
