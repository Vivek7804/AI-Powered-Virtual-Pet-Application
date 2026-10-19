from django.contrib import admin
from .models import Pet, Interaction


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_type', 'personality', 'mood', 'hunger', 'happiness', 'energy', 'updated_at')
    list_filter = ('pet_type', 'personality', 'mood')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('pet', 'interaction_type', 'user_message', 'is_ai_generated', 'created_at')
    list_filter = ('interaction_type', 'is_ai_generated', 'created_at')
    search_fields = ('user_message', 'pet_response', 'pet__name')
    readonly_fields = ('created_at',)
