from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Pet(models.Model):
    """
    Virtual Pet Model.
    Stores pet attributes, customization, physical stats, and dynamic mood.
    All numeric attributes (hunger, happiness, energy) are constrained between 0 and 100.
    """

    PET_TYPE_CHOICES = [
        ('Cat', 'Cat 🐱'),
        ('Dog', 'Dog 🐶'),
        ('Rabbit', 'Rabbit 🐰'),
        ('Panda', 'Panda 🐼'),
    ]

    PERSONALITY_CHOICES = [
        ('Friendly', 'Friendly 😊'),
        ('Playful', 'Playful 🎾'),
        ('Shy', 'Shy 🙈'),
        ('Curious', 'Curious 🔍'),
    ]

    MOOD_CHOICES = [
        ('Happy', 'Happy 😊'),
        ('Excited', 'Excited 🤩'),
        ('Hungry', 'Hungry 🍖'),
        ('Sleepy', 'Sleepy 😴'),
        ('Sad', 'Sad 🥺'),
        ('Playful', 'Playful 🎾'),
        ('Neutral', 'Neutral 😐'),
    ]

    name = models.CharField(max_length=60, help_text="The pet's customizable name")
    pet_type = models.CharField(max_length=20, choices=PET_TYPE_CHOICES, default='Cat')
    personality = models.CharField(max_length=20, choices=PERSONALITY_CHOICES, default='Friendly')

    # Physical and Emotional Attributes (0 to 100)
    # Hunger: 0 = completely full, 100 = extremely hungry / starving
    hunger = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 (Full) to 100 (Starving)"
    )

    # Happiness: 0 = very unhappy / depressed, 100 = overjoyed
    happiness = models.IntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 (Very Unhappy) to 100 (Very Happy)"
    )

    # Energy: 0 = exhausted, 100 = fully energetic
    energy = models.IntegerField(
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 (Exhausted) to 100 (Fully Energetic)"
    )

    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='Happy')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Virtual Pet'
        verbose_name_plural = 'Virtual Pets'

    def __str__(self):
        return f"{self.name} ({self.pet_type} - {self.mood})"

    def clean(self):
        """Server-side model validation for bounds checking."""
        for field_name in ['hunger', 'happiness', 'energy']:
            val = getattr(self, field_name)
            if val is not None and (val < 0 or val > 100):
                raise ValidationError({field_name: f"{field_name.capitalize()} must be between 0 and 100."})

    def save(self, *args, **kwargs):
        """Clamp stats between 0 and 100 automatically before saving to prevent DB corruption."""
        self.hunger = max(0, min(100, int(self.hunger)))
        self.happiness = max(0, min(100, int(self.happiness)))
        self.energy = max(0, min(100, int(self.energy)))
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def pet_emoji(self):
        """Returns the primary emoji corresponding to the pet animal type."""
        emoji_map = {
            'Cat': '🐱',
            'Dog': '🐶',
            'Rabbit': '🐰',
            'Panda': '🐼',
        }
        return emoji_map.get(self.pet_type, '🐾')

    @property
    def mood_emoji(self):
        """Returns an expressive emoji reflecting the pet's current mood."""
        mood_map = {
            'Happy': '😊',
            'Excited': '🤩',
            'Hungry': '🤤',
            'Sleepy': '😴',
            'Sad': '🥺',
            'Playful': '🎾',
            'Neutral': '😐',
        }
        return mood_map.get(self.mood, '😊')

    @property
    def mood_badge_class(self):
        """CSS class name helper for visual mood indicator badges."""
        return f"badge-mood-{self.mood.lower()}"

    @property
    def mood_description(self):
        """Short emotional message reflecting current mood."""
        descriptions = {
            'Happy': "Feeling wonderful, cheerful, and full of joy!",
            'Excited': "Super energetic and thrilled to spend time with you!",
            'Hungry': "Tummy is rumbling! Could really use a delicious snack!",
            'Sleepy': "Yawning and rubbing eyes... Ready for a cozy nap.",
            'Sad': "Feeling lonely and a bit blue. Needs some love and care.",
            'Playful': "Bouncing with excitement! Ready for games and fun!",
            'Neutral': "Calm, peaceful, and watching the world go by.",
        }
        return descriptions.get(self.mood, "Content and relaxed.")


class Interaction(models.Model):
    """
    Interaction and Chat History Model.
    Tracks all feeding, playing, and chatting activities with the pet.
    """

    INTERACTION_TYPES = [
        ('FEED', 'Feeding 🍖'),
        ('PLAY', 'Playing 🎾'),
        ('CHAT', 'Chat 💬'),
        ('REST', 'Resting 💤'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    user_message = models.TextField(blank=True, default='', help_text="User's input message or prompt")
    pet_response = models.TextField(help_text="Pet's response message")
    is_ai_generated = models.BooleanField(
        default=False,
        help_text="True if generated by an actual Generative AI API, False if generated by fallback rule system"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pet Interaction'
        verbose_name_plural = 'Pet Interactions'

    def __str__(self):
        return f"[{self.interaction_type}] {self.pet.name} at {self.created_at.strftime('%H:%M:%S')}"
