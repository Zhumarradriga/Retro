from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Game(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    js_file = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='game_covers/', blank=True, null=True)  # Поле для обложки
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def average_rating(self):
        # Вычисляем средний рейтинг на основе отзывов
        avg_rating = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0.0
    def review_count(self):
        return self.reviews.count()

class HighScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='high_scores')
    score = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='high_scores')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"{self.user.username} - {self.score} ({self.game.name})"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Оценка от 1 до 5
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'game']  # Один пользователь — один отзыв на игру

    def __str__(self):
        return f"{self.user.username} - {self.game.name} ({self.rating})"