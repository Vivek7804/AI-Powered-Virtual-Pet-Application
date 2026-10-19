"""
Mood Service Module.
Handles dynamic mood calculation based on physical stats (hunger, happiness, energy)
and recent interactions, according to deterministic examination rules.
"""

def calculate_mood(hunger: int, happiness: int, energy: int, last_action: str = None) -> str:
    """
    Calculates the pet's mood based on current state values and optional last action.

    Priority Order:
    1. Very Low Energy (<= 20) -> Sleepy (Needs rest regardless of other stats)
    2. Very High Hunger (>= 75) -> Hungry (Tummy rumbling takes precedence)
    3. Very Low Happiness (<= 25) -> Sad (Feeling neglected or lonely)
    4. Action Context:
       - If last action was 'PLAY' or personality is energetic and happiness is high (>= 70) and energy >= 30:
         mood becomes 'Playful' or 'Excited'
    5. Well-fed (hunger <= 40) and high happiness (happiness >= 60) -> Happy
    6. High energy (>= 80) and happiness (>= 80) -> Excited
    7. Otherwise -> Neutral

    Returns:
        str: One of ['Happy', 'Excited', 'Hungry', 'Sleepy', 'Sad', 'Playful', 'Neutral']
    """
    # Rule 1: Low energy dominates
    if energy <= 20:
        return 'Sleepy'

    # Rule 2: High hunger dominates
    if hunger >= 75:
        return 'Hungry'

    # Rule 3: Low happiness dominates
    if happiness <= 25:
        return 'Sad'

    # Rule 4: Action-based mood transitions
    if last_action == 'PLAY':
        if happiness >= 80 and energy >= 40:
            return 'Excited'
        return 'Playful'

    if last_action == 'FEED':
        if hunger <= 30 and happiness >= 60:
            return 'Happy'

    # Rule 5: Peak happiness and energy
    if happiness >= 85 and energy >= 70:
        return 'Excited'

    # Rule 6: Well-fed & happy
    if hunger <= 40 and happiness >= 60:
        return 'Happy'

    # Rule 7: Default fallback state
    return 'Neutral'


def update_pet_mood(pet, last_action: str = None) -> str:
    """
    Evaluates and updates the pet's mood in the database if it changed.
    Returns the updated mood string.
    """
    new_mood = calculate_mood(
        hunger=pet.hunger,
        happiness=pet.happiness,
        energy=pet.energy,
        last_action=last_action
    )
    if pet.mood != new_mood:
        pet.mood = new_mood
        pet.save()
    return new_mood
