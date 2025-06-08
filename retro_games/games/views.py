from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from .models import Game, HighScore, Review
from orders.models import Order, OrderItem
from .serializers import UserSerializer
import json
from django.db.models import Avg, Count, Max
from cart.forms import CartAddGameForm
from django.contrib import messages
from .forms import ReviewForm

def home(request):
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')

    games = Game.objects.all()
    if search_query:
        games = games.filter(name__icontains=search_query)

    if sort_by == 'rating':
        games = games.annotate(avg_rating=Avg('reviews__rating')).order_by(
            '-avg_rating' if order == 'desc' else 'avg_rating'
        )
    elif sort_by == 'reviews':
        games = games.annotate(review_count=Count('reviews')).order_by(
            '-review_count' if order == 'desc' else 'review_count'
        )
    else:
        games = games.order_by('-name' if order == 'desc' else 'name')

    # Получаем список купленных игр для авторизованного пользователя
    purchased_games = []
    if request.user.is_authenticated:
        purchased_games = Game.objects.filter(
            orderitem__order__user=request.user,
            orderitem__order__paid=True
        ).distinct()

    cart_add_form = CartAddGameForm()
    return render(request, 'home.html', {
        'games': games,
        'sort_by': sort_by,
        'order': order,
        'search_query': search_query,
        'cart_add_form': cart_add_form,
        'purchased_games': purchased_games,
    })

def game_detail(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)
    reviews = game.reviews.all()
    purchased = False
    can_review = False
    if request.user.is_authenticated:
        purchased = OrderItem.objects.filter(
            order__user=request.user,
            game=game,
            order__paid=True
        ).exists()
        can_review = purchased and not game.reviews.filter(user=request.user).exists()
    
    # Получение лучших результатов пользователей
    leaderboard = HighScore.objects.filter(game=game).values('user__username').annotate(
        best_score=Max('score')
    ).order_by('-best_score')[:10]  # Ограничим топ-10

    cart_add_form = CartAddGameForm()
    review_form = None
    if can_review and request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.game = game
            try:
                review.save()
                messages.success(request, 'Отзыв успешно отправлен!')
                return redirect('games:game_detail', game_slug=game_slug)
            except IntegrityError:
                messages.error(request, 'Вы уже оставили отзыв для этой игры.')
    elif can_review:
        review_form = ReviewForm()
    
    return render(request, 'game_detail.html', {
        'game': game,
        'reviews': reviews,
        'purchased': purchased,
        'can_review': can_review,
        'cart_add_form': cart_add_form,
        'review_form': review_form,
        'leaderboard': leaderboard,
    })

@login_required
def play_game(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)
    # Проверяем, купил ли пользователь игру
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        game=game,
        order__paid=True  # Учитываем только оплаченные заказы
    ).exists()
    
    if not has_purchased:
        # Если игра не куплена, перенаправляем на страницу корзины
        return redirect('cart:cart_add', game_id=game.id)
    
    return render(request, 'play_game.html', {'game': game})

def leaderboard(request):
    scores = HighScore.objects.select_related('game', 'user')[:10]
    games = Game.objects.all()
    return render(request, 'leaderboard.html', {'scores': scores, 'games': games})

@login_required
def save_score(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = data.get('score')
            game_slug = data.get('game')
            game = get_object_or_404(Game, slug=game_slug)
            
            # Отладочный вывод
            print(f"Saving score: user={request.user.username}, game={game.name}, score={score}")
            
            # Проверяем, купил ли пользователь игру
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                game=game,
                order__paid=True
            ).exists()
            if not has_purchased:
                return JsonResponse({'status': 'error', 'message': 'Игра не куплена'}, status=403)
            
            # Сохраняем результат
            HighScore.objects.create(user=request.user, game=game, score=score)
            messages.success(request, 'Очки успешно сохранены!')
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error saving score: {str(e)}")  # Для отладки
            messages.error(request, 'Ошибка при сохранении очков.')
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'}, status=400)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('games:home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            login(request, user)
            return redirect('games:home')
        return render(request, 'register.html', {'errors': serializer.errors})
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('games:home')

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request):
    data = json.loads(request.body)
    game = get_object_or_404(Game, slug=data['game_slug'])
    rating = int(data['rating'])
    if not 1 <= rating <= 5:
        return JsonResponse({'status': 'error', 'message': 'Rating must be between 1 and 5'}, status=400)
    Review.objects.update_or_create(
        user=request.user,
        game=game,
        defaults={'rating': rating, 'comment': data.get('comment', '')}
    )
    return JsonResponse({'status': 'success'})