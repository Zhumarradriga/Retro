from django.contrib import admin
from .models import Game, HighScore, Review

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'average_rating')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(HighScore)
class HighScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'game', 'created_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'rating', 'created_at')