/**
 * AI Virtual Pet Studio - Client Interaction Enhancer
 * Implements AJAX updates for seamless feeding, playing, and mood transitions.
 * Gracefully degrades to native HTTP POST when JS is disabled.
 */

document.addEventListener('DOMContentLoaded', () => {
    initActionForms();
    initPetClickAnimation();
});

/**
 * Web Audio API cute sound effects synthesizer (zero external audio files needed!)
 */
const PetAudio = {
    ctx: null,
    init() {
        if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContext();
        }
    },
    playTone(freq, type = 'sine', duration = 0.15) {
        try {
            this.init();
            if (!this.ctx) return;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
            gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start();
            osc.stop(this.ctx.currentTime + duration);
        } catch (e) {
            // Audio policy or unsupported
        }
    },
    feedSound() {
        this.playTone(330, 'triangle', 0.12);
        setTimeout(() => this.playTone(440, 'triangle', 0.15), 100);
    },
    playSound() {
        this.playTone(400, 'sine', 0.1);
        setTimeout(() => this.playTone(600, 'sine', 0.1), 80);
        setTimeout(() => this.playTone(800, 'sine', 0.18), 160);
    },
    restSound() {
        this.playTone(280, 'sine', 0.3);
    }
};

/**
 * AJAX Action Forms Handling (Feed, Play, Rest)
 */
function initActionForms() {
    const actionForms = document.querySelectorAll('.action-form');
    actionForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const actionType = form.dataset.action;
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) submitBtn.disabled = true;

            // Trigger audio
            if (actionType === 'FEED') PetAudio.feedSound();
            else if (actionType === 'PLAY') PetAudio.playSound();
            else if (actionType === 'REST') PetAudio.restSound();

            // Play mascot reaction animation
            bouncePetMascot();

            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.pet) {
                        updateDashboardState(data.pet, data.message, actionType);
                    }
                } else {
                    // Fall back to standard form submission if server returned error
                    form.submit();
                }
            } catch (err) {
                // If fetch fails, do traditional post
                form.submit();
            } finally {
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    });
}

/**
 * Updates UI DOM elements with new state values
 */
function updateDashboardState(petState, messageText, actionType) {
    // 1. Update metric numbers & progress bars
    const hungerVal = document.getElementById('hunger-val');
    const hungerBar = document.getElementById('hunger-bar');
    const hungerSub = document.getElementById('hunger-subtext');
    if (hungerVal) hungerVal.textContent = `${petState.hunger}%`;
    if (hungerBar) hungerBar.style.width = `${petState.hunger}%`;
    if (hungerSub) {
        if (petState.hunger >= 75) hungerSub.textContent = "Critical: Starving! Needs food immediately!";
        else if (petState.hunger >= 50) hungerSub.textContent = "Getting hungry! A treat would be nice.";
        else if (petState.hunger >= 20) hungerSub.textContent = "Comfortably fed.";
        else hungerSub.textContent = "Completely full and satisfied!";
    }

    const happyVal = document.getElementById('happiness-val');
    const happyBar = document.getElementById('happiness-bar');
    const happySub = document.getElementById('happiness-subtext');
    if (happyVal) happyVal.textContent = `${petState.happiness}%`;
    if (happyBar) happyBar.style.width = `${petState.happiness}%`;
    if (happySub) {
        if (petState.happiness >= 80) happySub.textContent = "Overjoyed & deeply bonded with you!";
        else if (petState.happiness >= 50) happySub.textContent = "Happy & content.";
        else if (petState.happiness >= 25) happySub.textContent = "A bit lonely, play with me!";
        else happySub.textContent = "Sad and neglected. Needs affection!";
    }

    const energyVal = document.getElementById('energy-val');
    const energyBar = document.getElementById('energy-bar');
    const energySub = document.getElementById('energy-subtext');
    if (energyVal) energyVal.textContent = `${petState.energy}%`;
    if (energyBar) energyBar.style.width = `${petState.energy}%`;
    if (energySub) {
        if (petState.energy >= 75) energySub.textContent = "Brimming with high energy!";
        else if (petState.energy >= 40) energySub.textContent = "Ready for playtime.";
        else if (petState.energy >= 20) energySub.textContent = "Growing tired...";
        else energySub.textContent = "Exhausted! Needs a nap to recharge!";
    }

    // 2. Update Mood Badge & Text
    const moodBadge = document.getElementById('pet-mood-badge');
    const moodEmoji = document.getElementById('pet-mood-emoji');
    const moodTitle = document.getElementById('pet-mood-title');
    const headerBadge = document.getElementById('header-pet-badge');

    if (moodBadge) {
        // Reset mood classes
        moodBadge.className = `mood-showcase-badge ${petState.mood_badge_class}`;
    }
    if (moodEmoji) moodEmoji.textContent = petState.mood_emoji;
    if (moodTitle) moodTitle.textContent = petState.mood;

    if (headerBadge) {
        const headerPill = headerBadge.querySelector('.mood-pill');
        if (headerPill) {
            headerPill.className = `header-pet-mood mood-pill ${petState.mood_badge_class}`;
            headerPill.textContent = `${petState.mood_emoji} ${petState.mood}`;
        }
    }

    // 3. Update Speech/Thought bubble
    const thoughtText = document.getElementById('pet-thought-text');
    if (thoughtText) {
        thoughtText.textContent = messageText || petState.mood_description;
    }

    // 4. Prepend to timeline list smoothly
    prependTimelineEntry(actionType, messageText);
}

/**
 * Dynamically inserts new interaction into the visible timeline
 */
function prependTimelineEntry(actionType, responseMessage) {
    const list = document.getElementById('timeline-list');
    if (!list) return;

    // Remove empty state if present
    const empty = list.querySelector('.empty-state');
    if (empty) empty.remove();

    const entry = document.createElement('div');
    entry.className = `timeline-entry type-${actionType.toLowerCase()} fade-in`;

    const iconMap = {
        'FEED': '🍲',
        'PLAY': '🎾',
        'REST': '💤',
        'CHAT': '💬'
    };
    const titleMap = {
        'FEED': 'Feeding',
        'PLAY': 'Playing',
        'REST': 'Resting',
        'CHAT': 'Chat'
    };

    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

    entry.innerHTML = `
        <div class="timeline-marker">${iconMap[actionType] || '🐾'}</div>
        <div class="timeline-content">
            <div class="timeline-meta">
                <span class="timeline-type-tag">${titleMap[actionType] || actionType}</span>
                <span class="timeline-time">${timeStr}</span>
                <span class="badge-fallback">🐾 Pet Instinct</span>
            </div>
            <div class="timeline-pet-response">
                ${responseMessage}
            </div>
        </div>
    `;

    list.insertBefore(entry, list.firstChild);
}

/**
 * Pet Mascot interactive click bounce
 */
function initPetClickAnimation() {
    const mascot = document.getElementById('pet-mascot');
    if (mascot) {
        mascot.addEventListener('click', () => {
            PetAudio.playTone(520, 'sine', 0.15);
            bouncePetMascot();
        });
    }
}

function bouncePetMascot() {
    const emoji = document.getElementById('pet-mascot-emoji');
    if (emoji) {
        emoji.style.transform = 'scale(1.22) rotate(-8deg)';
        setTimeout(() => {
            emoji.style.transform = 'scale(0.92) rotate(6deg)';
            setTimeout(() => {
                emoji.style.transform = '';
            }, 150);
        }, 150);
    }
}
