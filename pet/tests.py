from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Pet, Interaction
from .services.mood_service import calculate_mood, update_pet_mood
from .services.ai_service import generate_pet_response, generate_fallback_response


class VirtualPetApplicationTests(TestCase):
    """
    Comprehensive Test Suite for MCA Semester III GenAI Lab Practical.
    Covers all 9 mandated test cases from Section 12 of the requirements.
    """

    def setUp(self):
        self.client = Client()
        # Default test pet: Coco
        self.pet = Pet.objects.create(
            name="Coco",
            pet_type="Dog",
            personality="Friendly",
            hunger=50,
            happiness=70,
            energy=60,
            mood="Neutral"
        )

    # -------------------------------------------------------------
    # Test 1: Create a pet named Coco
    # Expected result: Pet details are saved and displayed
    # -------------------------------------------------------------
    def test_01_create_pet(self):
        response = self.client.post(reverse('create_pet'), {
            'name': 'Bella',
            'pet_type': 'Cat',
            'personality': 'Playful'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        bella = Pet.objects.get(name='Bella')
        self.assertEqual(bella.pet_type, 'Cat')
        self.assertEqual(bella.personality, 'Playful')
        # Check starting values
        self.assertEqual(bella.hunger, 30)
        self.assertEqual(bella.happiness, 80)
        self.assertEqual(bella.energy, 80)
        # Check welcome interaction was created
        self.assertTrue(bella.interactions.exists())

    # -------------------------------------------------------------
    # Test 2: Feed Coco
    # Expected result: Hunger decreases, happiness may increase, state saved
    # -------------------------------------------------------------
    def test_02_feed_pet(self):
        initial_hunger = self.pet.hunger
        initial_happiness = self.pet.happiness

        response = self.client.post(reverse('feed_pet', args=[self.pet.id]), follow=True)
        self.assertEqual(response.status_code, 200)

        self.pet.refresh_from_db()
        self.assertLess(self.pet.hunger, initial_hunger)
        self.assertGreaterEqual(self.pet.happiness, initial_happiness)

        # Verify interaction recorded
        latest_interaction = self.pet.interactions.first()
        self.assertEqual(latest_interaction.interaction_type, 'FEED')
        self.assertIn("Yummy!", latest_interaction.pet_response)

    # -------------------------------------------------------------
    # Test 3: Play with Coco
    # Expected result: Happiness increases, energy decreases, mood updated
    # -------------------------------------------------------------
    def test_03_play_pet(self):
        initial_energy = self.pet.energy
        initial_happiness = self.pet.happiness

        response = self.client.post(reverse('play_pet', args=[self.pet.id]), follow=True)
        self.assertEqual(response.status_code, 200)

        self.pet.refresh_from_db()
        self.assertGreater(self.pet.happiness, initial_happiness)
        self.assertLess(self.pet.energy, initial_energy)

        # Verify interaction recorded
        latest_interaction = self.pet.interactions.first()
        self.assertEqual(latest_interaction.interaction_type, 'PLAY')
        self.assertIn("fun", latest_interaction.pet_response.lower())

    # -------------------------------------------------------------
    # Test 4: Send "Hello!" in chat
    # Expected result: The pet generates a contextually appropriate response
    # -------------------------------------------------------------
    def test_04_chat_hello(self):
        response = self.client.post(reverse('chat'), {
            'message': 'Hello!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        interaction = self.pet.interactions.filter(interaction_type='CHAT').first()
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.user_message, 'Hello!')
        self.assertTrue(len(interaction.pet_response) > 5)

    # -------------------------------------------------------------
    # Test 5: Send "Are you hungry?"
    # Expected result: The response reflects the pet's current hunger level
    # -------------------------------------------------------------
    def test_05_chat_hunger_reflection(self):
        # Case A: Not hungry (hunger = 10)
        self.pet.hunger = 10
        self.pet.save()
        resp_full = generate_fallback_response(self.pet, "Are you hungry?")
        self.assertIn("full", resp_full.lower())

        # Case B: Very hungry (hunger = 90)
        self.pet.hunger = 90
        self.pet.save()
        resp_starving = generate_fallback_response(self.pet, "Are you hungry?")
        self.assertTrue("hungry" in resp_starving.lower() or "starving" in resp_starving.lower() or "food" in resp_starving.lower() or "treat" in resp_starving.lower())

    # -------------------------------------------------------------
    # Test 6: Database Persistence across requests
    # Expected result: State and interaction history persist in SQLite
    # -------------------------------------------------------------
    def test_06_database_persistence(self):
        # Modify and save
        self.pet.hunger = 42
        self.pet.happiness = 88
        self.pet.energy = 55
        self.pet.mood = 'Excited'
        self.pet.save()

        Interaction.objects.create(
            pet=self.pet,
            interaction_type='FEED',
            user_message='Test meal',
            pet_response='Delicious meal test!',
            is_ai_generated=False
        )

        # Fetch in a fresh DB query
        fetched_pet = Pet.objects.get(id=self.pet.id)
        self.assertEqual(fetched_pet.hunger, 42)
        self.assertEqual(fetched_pet.happiness, 88)
        self.assertEqual(fetched_pet.energy, 55)
        self.assertEqual(fetched_pet.mood, 'Excited')
        self.assertEqual(fetched_pet.interactions.count(), 1)

    # -------------------------------------------------------------
    # Test 7: Low energy mood rule -> Sleepy
    # Expected result: When energy <= 20, mood becomes Sleepy
    # -------------------------------------------------------------
    def test_07_low_energy_mood_sleepy(self):
        self.pet.energy = 10
        self.pet.hunger = 20
        self.pet.happiness = 80
        self.pet.save()

        new_mood = update_pet_mood(self.pet)
        self.assertEqual(new_mood, 'Sleepy')
        self.assertEqual(self.pet.mood, 'Sleepy')

    # -------------------------------------------------------------
    # Test 8: Run application without an AI API key
    # Expected result: Fallback response system works seamlessly
    # -------------------------------------------------------------
    def test_08_fallback_without_api_key(self):
        with self.settings(GEMINI_API_KEY=''):
            reply, is_ai = generate_pet_response(self.pet, "How are you?")
            self.assertFalse(is_ai)
            self.assertTrue(len(reply) > 0)
            self.assertIn("Coco", reply)

    # -------------------------------------------------------------
    # Test 9: Submit invalid state values
    # Expected result: Validation clamps values between 0 and 100
    # -------------------------------------------------------------
    def test_09_state_bounds_clamping(self):
        # Clamping logic on save
        self.pet.hunger = 150
        self.pet.happiness = -50
        self.pet.energy = 200
        self.pet.save()

        self.pet.refresh_from_db()
        self.assertEqual(self.pet.hunger, 100)
        self.assertEqual(self.pet.happiness, 0)
        self.assertEqual(self.pet.energy, 100)
