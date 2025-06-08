from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from games.models import Game
from django.contrib.auth.decorators import login_required

@login_required
def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('home')
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.paid = True  # Отмечаем заказ как оплаченный
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    game=item['game'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            return render(request, 'orders/order/created.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})

def add_to_cart(request):
    if request.method == 'POST':
        game_id = request.POST.get('game_id')
        game = get_object_or_404(Game, id=game_id)
        cart = Cart(request)
        cart.add(game=game, quantity=1)
    return redirect('home')