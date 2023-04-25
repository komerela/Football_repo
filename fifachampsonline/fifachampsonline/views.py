
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from fixtures.models import Fixture, Booking, Player, Item, HeadToHead, Matches, Result, Purchase, Cart
from fixtures.forms import HeadToHeadForm, PurchaseForm, HeadToHeadRequestForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from fixtures.serializers import ItemSerializer
from accounts.models import User, UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

# Chatbot imports
from django.http import JsonResponse
from chatbot.models import ChatbotResponse
from chatbot.openai_chatbot import OpenAIChatbot
from dotenv import load_dotenv

load_dotenv()

import os
import sys


import logging

logger = logging.getLogger(__name__)

# Add the directory containing the module to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create your views here.

# Define a function to check if a user is a staff member or not
def is_staff(user):
    return user.is_staff


class RestrictedView(TemplateView):
    template_name = 'restricted.html'

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    

def home(request):
    try:
        upcoming_fixtures = Fixture.objects.filter(is_completed=False).order_by('date')[:5]
        point_table = UserProfile.objects.all().order_by('-total_points')
        shop_items = Item.objects.all()
        return render(request, 'home.html', {'upcoming_fixtures': upcoming_fixtures,
                                             'point_table': point_table,
                                             'shop_items': shop_items})
    except Exception as e:
        # Handle the exception here, for example by logging it or displaying an error page.
        logger.exception(e)
        # Render the error page with a custom error message
        return render(request, 'error.html', {'error_message': 'An error occurred. Please try again later.'})
    
class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'profile.html'

    def get_object(self, queryset=None):
        return self.request.user


class FixtureListView(ListView):
    model = Fixture
    template_name = 'fixture_list.html'
    context_object_name = 'fixtures'


class FixtureCreateView(CreateView):
    model = Fixture
    template_name = 'fixture_form.html'
    fields = ['home_team', 'away_team', 'date', 'time', 'venue', 'price']

    def form_valid(self, form):
        return super().form_valid(form)

@method_decorator(user_passes_test(is_staff), name='dispatch')
class FixtureUpdateView(UpdateView):
    model = Fixture
    template_name = 'fixture_form.html'
    fields = ['home_team', 'away_team', 'date', 'time', 'venue', 'price']

    def form_valid(self, form):
        return super().form_valid(form)

@method_decorator(user_passes_test(is_staff), name='dispatch')
class FixtureDeleteView(DeleteView):
    model = Fixture
    template_name = 'fixture_confirm_delete.html'
    success_url = reverse_lazy('fixture-list')


class FixtureDetailView(View):
    def get(self, request, fixture_id):
        fixture = get_object_or_404(Fixture, pk=fixture_id)
        form = HeadToHeadForm(current_user=request.user)
        return render(request, 'fixture_detail.html', {'fixture': fixture, 'form': form})

    def post(self, request, fixture_id):
        fixture = get_object_or_404(Fixture, pk=fixture_id)
        form = HeadToHeadForm(request.POST, current_user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.fixture = fixture
            booking.user = request.user
            booking.save()
            messages.success(request, 'Head-to-head booking successfully made.')
            return redirect('fixture_detail', fixture_id=fixture_id)
        return render(request, 'fixture_detail.html', {'fixture': fixture, 'form': form})

fixture_detail = FixtureDetailView.as_view()


# display past fixtures and results
# In the updated get_context_data method, we first call the parent's get_context_data method to get the default context. We then filter the results to only include those that belong to the fixtures in the current view. Finally, we add the filtered results to the context.

# With this modification, the results variable will be available in the template
class PastFixtureListView(ListView):
    model = Fixture
    template_name = 'fixtures/past_fixtures.html'

    def get_queryset(self):
        return Fixture.objects.filter(date__lt=timezone.now()).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fixtures = context['object_list']
        results = Result.objects.filter(fixture__in=fixtures)
        context['results'] = results
        return context


def error_view(request):
    return render(request, 'error.html')


class HeadToHeadView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, id):
        fixture = get_object_or_404(Fixture, id=id)
        form = HeadToHeadForm(current_user=request.user)
        return render(request, 'fixtures/head_to_head.html', {'form': form, 'fixture': fixture})

    def post(self, request, id):
        fixture = get_object_or_404(Fixture, id=id)
        form = HeadToHeadForm(request.POST, current_user=request.user)

        if form.is_valid():
            player1 = request.user
            player2 = form.cleaned_data['player2']
            amount = fixture.price_per_player * 2
            paid = False

            # Create the HeadToHead object
            head_to_head = HeadToHead.objects.create(
                fixture=fixture,
                player1=player1,
                player2=player2,
                amount=amount,
                paid=paid
            )

            # Redirect the user to the payment page
            return redirect(reverse('payment:process_payment', args=[fixture.id, head_to_head.id]))

        return render(request, 'fixtures/head_to_head.html', {'form': form, 'fixture': fixture})

class HeadToHeadRequestView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        form = HeadToHeadRequestForm()
        return render(request, 'head_to_head_request.html', {'form': form})

    def post(self, request):
        form = HeadToHeadRequestForm(request.POST)

        if form.is_valid():
            player1 = request.user
            player2 = form.cleaned_data['player2']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            immediate_game = form.cleaned_data['immediate_game']
            amount = fixture.price_per_player * 2
            paid = False

            # Create the HeadToHead object
            head_to_head = HeadToHead.objects.create(
                player1=player1,
                player2=player2,
                date=date,
                time=time,
                immediate_game=immediate_game,
                amount=amount,
                paid=paid
            )

            # Create the Booking object
            booking = Booking.objects.create(
                user=request.user,
                head_to_head=head_to_head,
                paid=False,
                booking_date=datetime.datetime.now()
            )

            # Redirect the user to the payment page
            return redirect(reverse('payment:process_payment', args=[booking.id]))

        return render(request, 'head_to_head_request.html', {'form': form})

# creates a Booking object and a Payment object and redirects the user to the payment page.

@login_required
def process_payment(request):
    cart = Cart.objects.filter(user=request.user).first()
    total_amount = sum(item.price for item in cart.items.all())

    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.user = request.user
            purchase.buyer = request.user.player.team_name
            purchase.price = total_amount
            purchase.save()

            # Loop over cart items and create Booking and Payment objects
            items = cart.items.all()
            for item in items:
                booking = Booking.objects.create(
                    user=request.user,
                    fixture=item.fixture,
                    head_to_head=item.head_to_head,
                    buyer=request.user.player.team_name,
                    price=item.price,
                    email=request.user.email,
                    phone_number=request.user.player.phone_number
                )

                payment = Payment.objects.create(
                    booking=booking,
                    amount=item.price,
                    paid=False
                )

            # Remove items from the cart
            cart.items.clear()

            return render(request, 'purchase_confirmation.html', {'purchase': purchase})
    else:
        form = PurchaseForm()

    return render(request, 'purchase_form.html', {'form': form, 'total_amount': total_amount})

# A view to display payment error

def payment_error(request):
    return render(request, 'payment_error.html')

class ShopView(ListView):
    model = Item
    template_name = 'shop.html'
    context_object_name = 'items'
    

@login_required
def purchase_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.item = item
            purchase.user = request.user
            purchase.price = item.price
            purchase.save()
            return render(request, 'purchase_confirmation.html', {'purchase': purchase})
    else:
        form = PurchaseForm()

    return render(request, 'purchase_form.html', {'form': form, 'item': item})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    context = {
        'item': item,
    }
    return render(request, 'item.html', context)

@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'cart.html', {'cart': cart})

@login_required
@require_POST
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.add(item)
    cart.save()
    return redirect('shop')

# Player model views

@method_decorator(login_required, name='dispatch')
class PlayerListView(ListView):
    model = Player
    template_name = 'player_list.html'
    context_object_name = 'players'

@method_decorator(user_passes_test(is_staff), name='dispatch')
class PlayerDetailView(DetailView):
    model = Player
    template_name = 'player_detail.html'
    context_object_name = 'player'

@method_decorator(login_required, name='dispatch')
class PlayerCreateView(CreateView):
    model = Player
    template_name = 'player_form.html'
    fields = ['name', 'user', 'ps_username', 'email', 'phone_number', 'team_name', 'fixture']

    def form_valid(self, form):
        return super().form_valid(form)

@method_decorator(user_passes_test(is_staff), name='dispatch')
class PlayerUpdateView(UpdateView):
    model = Player
    template_name = 'player_form.html'
    fields = ['name', 'ps_username', 'email', 'phone_number', 'team_name', 'fixture']

    def form_valid(self, form):
        return super().form_valid(form)

@method_decorator(user_passes_test(is_staff), name='dispatch')
class PlayerDeleteView(DeleteView):
    model = Player
    template_name = 'player_confirm_delete.html'
    success_url = reverse_lazy('player-list')


def player_info(request, player_id):
    player = Player.objects.get(pk=player_id)
    context = {
        'player_name': player.name,
        'team_name': player.team_name,
    }
    return render(request, 'player_info.html', context)

# view where a logged-in player can request a head-to-head match with another 
# player and specify the date and time they want to play the game. 

@login_required
def request_head_to_head(request):
    if request.method == 'POST':
        form = HeadToHeadRequestForm(request.POST)
        if form.is_valid():
            player1 = request.user
            player2 = form.cleaned_data['player2']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            immediate_game = form.cleaned_data['immediate_game']
            amount = fixture.price_per_player * 2
            paid = False

            # Create the HeadToHead object
            head_to_head = HeadToHead.objects.create(
                player1=player1,
                player2=player2,
                date=date,
                time=time,
                immediate_game=immediate_game,
                amount=amount,
                paid=paid
            )

            # Create the Booking object
            booking = Booking.objects.create(
                user=request.user,
                head_to_head=head_to_head,
                paid=False,
                booking_date=datetime.datetime.now()
            )

            # Redirect the user to the payment page
            return redirect(reverse('payment:process_payment', args=[booking.id]))

    else:
        form = HeadToHeadRequestForm()

    return render(request, 'head_to_head_request.html', {'form': form})


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    # Allow only authenticated users to access this view
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class PointsTable(ListView):
    model = Matches
    template_name = 'points_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fixtures = Fixture.objects.all()

        # Calculate points and goals for each team
        team_stats = {}
        for fixture in fixtures:
            if fixture.home_score > fixture.away_score:
                winner = fixture.home_team
                loser = fixture.away_team
                result = 'W'
            elif fixture.home_score < fixture.away_score:
                winner = fixture.away_team
                loser = fixture.home_team
                result = 'L'
            else:
                winner = None
                loser = None
                result = 'D'

            # Update winner's stats
            if winner in team_stats:
                team_stats[winner]['points'] += 3
                team_stats[winner]['wins'] += 1
            else:
                team_stats[winner] = {'points': 3, 'wins': 1, 'draws': 0, 'losses': 0, 'goals_for': 0, 'goals_against': 0}

            # Update loser's stats
            if loser in team_stats:
                team_stats[loser]['losses'] += 1
            else:
                team_stats[loser] = {'points': 0, 'wins': 0, 'draws': 0, 'losses': 1, 'goals_for': 0, 'goals_against': 0}

            # Update draws
            if result == 'D':
                if fixture.home_team in team_stats:
                    team_stats[fixture.home_team]['points'] += 1
                    team_stats[fixture.home_team]['draws'] += 1
                else:
                    team_stats[fixture.home_team] = {'points': 1, 'wins': 0, 'draws': 1, 'losses': 0, 'goals_for': 0, 'goals_against': 0}

                if fixture.away_team in team_stats:
                    team_stats[fixture.away_team]['points'] += 1
                    team_stats[fixture.away_team]['draws'] += 1
                else:
                    team_stats[fixture.away_team] = {'points': 1, 'wins': 0, 'draws': 1, 'losses': 0, 'goals_for': 0, 'goals_against': 0}

            # Update goals for and against
            if winner:
                if winner == fixture.home_team:
                    team_stats[winner]['goals_for'] += fixture.home_score
                    team_stats[winner]['goals_against'] += fixture.away_score
                else:
                    team_stats[winner]['goals_for'] += fixture.away_score
                    team_stats[winner]['goals_against'] += fixture.home_score

        # Calculate goal difference and add team stats to context
        for team in team_stats:
            team_stats[team]['goal_difference'] = team_stats[team]['goals_for'] - team_stats[team]['goals_against']
        context['teams'] = team_stats

        return context
    

class ChatbotView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = os.getenv("OPENAI_API_KEY") 
        self.chatbot = OpenAIChatbot(api_key=self.api_key)

    def get(self, request):
        responses = ChatbotResponse.objects.all().order_by('-created_at')[:10]
        return render(request, 'chatbot.html', {'responses': responses})
    
    def post(self, request):
        message = request.POST['message']
        response = self.chatbot.generate_response(message=message)
        if "I'm sorry, I don't understand the question." in response:
            return JsonResponse({'message': response, 'suggested_responses': ['Can you please rephrase your question?', 'Can you provide more information?', 'Would you like to speak to a human representative?']})
        else:
            return JsonResponse({'message': response})
        
