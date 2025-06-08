from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.decorators import login_required
from .models import Game, HighScore, Review
from orders.models import Order, OrderItem
from .serializers import UserSerializer
import json
from django.db.models import Avg, Count
from cart.forms import CartAddGameForm

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

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_score(request):
    data = json.loads(request.body)
    game = get_object_or_404(Game, slug=data['game'])
    HighScore.objects.create(
        user=request.user,
        score=data['score'],
        game=game
    )
    return JsonResponse({'status': 'success'})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
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
            return redirect('home')
        return render(request, 'register.html', {'errors': serializer.errors})
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('home')

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