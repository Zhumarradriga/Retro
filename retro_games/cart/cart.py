from decimal import Decimal
from django.conf import settings
from games.models import Game

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, game, quantity=1, update_quantity=False):
        game_id = str(game.id)
        if game_id not in self.cart:
            self.cart[game_id] = {'quantity': 0, 'price': str(game.price)}
        if update_quantity:
            self.cart[game_id]['quantity'] = quantity
        else:
            self.cart[game_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, game):
        game_id = str(game.id)
        if game_id in self.cart:
            del self.cart[game_id]
            self.save()

    def __iter__(self):
        game_ids = self.cart.keys()
        games = Game.objects.filter(id__in=game_ids)
        for game in games:
            self.cart[str(game.id)]['game'] = game
            yield self.cart[str(game.id)]

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True