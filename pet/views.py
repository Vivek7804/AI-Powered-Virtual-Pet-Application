import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from .models import Pet, Interaction
from .forms import PetForm, ChatMessageForm
from .services.mood_service import update_pet_mood
from .services.ai_service import generate_pet_response


def get_current_pet(request):
    """
    Helper function to retrieve the active virtual pet.
    Prioritizes session-stored pet_id, then falls back to the most recent pet.
    """
    pet_id = request.session.get('active_pet_id')
    if pet_id:
        try:
            return Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            pass
    pet = Pet.objects.first()
    if pet:
        request.session['active_pet_id'] = pet.id
    return pet


def home(request):
    """Home / Virtual Pet Dashboard View."""
    pet = get_current_pet(request)
    if not pet:
        return redirect('create_pet')

    # Fetch recent interactions for the dashboard timeline
    recent_interactions = pet.interactions.all()[:8]
    chat_form = ChatMessageForm()

    context = {
        'pet': pet,
        'recent_interactions': recent_interactions,
        'chat_form': chat_form,
    }
    return render(request, 'pet/home.html', context)


def create_pet(request):
    """Pet creation and customization view."""
    if request.method == 'POST':
        form = PetForm(request.POST)
        if form.is_valid():
            pet = form.save()
            request.session['active_pet_id'] = pet.id

            # Initial welcome interaction
            Interaction.objects.create(
                pet=pet,
                interaction_type='CHAT',
                user_message="Hello!",
                pet_response=f"Hi there! I'm {pet.name}, your new {pet.personality.lower()} {pet.pet_type}! I am so happy to meet you! {pet.pet_emoji}✨",
                is_ai_generated=False
            )

            messages.success(request, f"🎉 Hooray! {pet.name} the {pet.pet_type} was successfully adopted!")
            return redirect('home')
    else:
        form = PetForm()

    return render(request, 'pet/create_pet.html', {'form': form})


@require_POST
def feed_pet(request, pet_id):
    """
    Feed interaction:
    - Reduces hunger level by 25.
    - Increases happiness slightly by 10.
    - Updates mood accordingly.
    - Records interaction in SQLite.
    """
    pet = get_object_or_404(Pet, id=pet_id)

    if pet.hunger <= 5:
        response_msg = f"*Burp!* {pet.name} is already completely full and happily rubbing tummy! 🥗 {pet.pet_emoji}"
    else:
        # State transitions
        pet.hunger = max(0, pet.hunger - 25)
        pet.happiness = min(100, pet.happiness + 10)
        pet.save()

        # Update dynamic mood
        update_pet_mood(pet, last_action='FEED')
        response_msg = f"Yummy! Thank you! I feel much better now! 🍖 {pet.pet_emoji}"

    # Log interaction
    interaction = Interaction.objects.create(
        pet=pet,
        interaction_type='FEED',
        user_message="Fed the pet a delicious meal",
        pet_response=response_msg,
        is_ai_generated=False
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'action': 'FEED',
            'message': response_msg,
            'pet': {
                'hunger': pet.hunger,
                'happiness': pet.happiness,
                'energy': pet.energy,
                'mood': pet.mood,
                'mood_emoji': pet.mood_emoji,
                'mood_badge_class': pet.mood_badge_class,
                'mood_description': pet.mood_description,
            }
        })

    messages.info(request, response_msg)
    return redirect('home')


@require_POST
def play_pet(request, pet_id):
    """
    Play interaction:
    - Increases happiness by 20.
    - Reduces energy by 15.
    - Slightly increases hunger by 10.
    - Updates mood dynamically.
    - Records interaction in SQLite.
    """
    pet = get_object_or_404(Pet, id=pet_id)

    if pet.energy <= 15:
        response_msg = f"*yawns heavily* {pet.name} is too exhausted to play right now! Let me take a nap first... 💤 {pet.pet_emoji}"
    else:
        pet.happiness = min(100, pet.happiness + 20)
        pet.energy = max(0, pet.energy - 15)
        pet.hunger = min(100, pet.hunger + 10)
        pet.save()

        update_pet_mood(pet, last_action='PLAY')
        response_msg = f"Yay! That was so much fun! Let's play again! 🎾 {pet.pet_emoji}"

    interaction = Interaction.objects.create(
        pet=pet,
        interaction_type='PLAY',
        user_message="Played fun games together",
        pet_response=response_msg,
        is_ai_generated=False
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'action': 'PLAY',
            'message': response_msg,
            'pet': {
                'hunger': pet.hunger,
                'happiness': pet.happiness,
                'energy': pet.energy,
                'mood': pet.mood,
                'mood_emoji': pet.mood_emoji,
                'mood_badge_class': pet.mood_badge_class,
                'mood_description': pet.mood_description,
            }
        })

    messages.info(request, response_msg)
    return redirect('home')


@require_POST
def rest_pet(request, pet_id):
    """
    Rest / Sleep interaction:
    - Restores energy by +35.
    - Slightly increases hunger by +5.
    - Updates mood dynamically.
    """
    pet = get_object_or_404(Pet, id=pet_id)

    pet.energy = min(100, pet.energy + 35)
    pet.hunger = min(100, pet.hunger + 5)
    pet.save()

    update_pet_mood(pet, last_action='REST')
    response_msg = f"Ahhh... that was a wonderful cozy nap! {pet.name} is refreshed and full of energy again! ⚡ {pet.pet_emoji}"

    Interaction.objects.create(
        pet=pet,
        interaction_type='REST',
        user_message="Put the pet to sleep for a quick nap",
        pet_response=response_msg,
        is_ai_generated=False
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'action': 'REST',
            'message': response_msg,
            'pet': {
                'hunger': pet.hunger,
                'happiness': pet.happiness,
                'energy': pet.energy,
                'mood': pet.mood,
                'mood_emoji': pet.mood_emoji,
                'mood_badge_class': pet.mood_badge_class,
                'mood_description': pet.mood_description,
            }
        })

    messages.info(request, response_msg)
    return redirect('home')


def chat_view(request):
    """
    Dedicated Chat Interface View:
    - Displays full conversation history.
    - Processes user messages with AI service or intelligent fallback.
    - Updates pet happiness slightly (+5).
    - Persists interaction in SQLite.
    """
    pet = get_current_pet(request)
    if not pet:
        return redirect('create_pet')

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if not user_message:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Message cannot be empty.'}, status=400)
            messages.error(request, "Message cannot be empty.")
            return redirect('chat')

        # Retrieve recent conversation turns for context
        recent_history = list(pet.interactions.filter(interaction_type='CHAT').order_by('-created_at')[:5])
        recent_history.reverse()

        # Generate response using AI Service or Fallback Engine
        pet_response_text, is_ai = generate_pet_response(pet, user_message, recent_history)

        # Chat interaction brings a small boost in happiness (+5)
        pet.happiness = min(100, pet.happiness + 5)
        pet.save()
        update_pet_mood(pet)

        # Save to database
        interaction = Interaction.objects.create(
            pet=pet,
            interaction_type='CHAT',
            user_message=user_message,
            pet_response=pet_response_text,
            is_ai_generated=is_ai
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'user_message': user_message,
                'pet_response': pet_response_text,
                'is_ai_generated': is_ai,
                'created_at': interaction.created_at.strftime('%H:%M'),
                'pet': {
                    'mood': pet.mood,
                    'mood_emoji': pet.mood_emoji,
                    'happiness': pet.happiness,
                }
            })

        return redirect('chat')

    # GET request
    chat_messages = pet.interactions.filter(interaction_type='CHAT').order_by('created_at')
    chat_form = ChatMessageForm()

    context = {
        'pet': pet,
        'chat_messages': chat_messages,
        'chat_form': chat_form,
    }
    return render(request, 'pet/chat.html', context)


def switch_pet(request, pet_id):
    """Allows selecting between pets if multiple pets are created."""
    pet = get_object_or_404(Pet, id=pet_id)
    request.session['active_pet_id'] = pet.id
    messages.info(request, f"Switched active pet to {pet.name}!")
    return redirect('home')


def list_pets(request):
    """List all created pets to allow easy switching during demonstration."""
    pets = Pet.objects.all()
    active_pet = get_current_pet(request)
    return render(request, 'pet/list_pets.html', {
        'pets': pets,
        'active_pet': active_pet,
    })
