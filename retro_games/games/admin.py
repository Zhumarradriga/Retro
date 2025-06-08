from django.contrib import admin
from .models import Game, Review, HighScore

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'created_at']
    list_editable = ['price']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'rating', 'created_at']

@admin.register(HighScore)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'score', 'created_at']