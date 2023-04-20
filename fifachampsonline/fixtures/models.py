from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from accounts.models import User
from datetime import date
# Create your models here.

class Fixture(models.Model):
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_completed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.date} {self.time}"


class Player(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ps_username = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    team_name = models.CharField(max_length=100)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='shop')

    def __str__(self):
        return self.name


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    buyer = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.item.name} - {self.buyer}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item)

class Matches(models.Model):
    name = models.CharField(max_length=100)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_drawn = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    
class HeadToHead(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
    date = models.DateField(default=date(2023, 4, 17))
    time = models.TimeField()
    immediate_game = models.BooleanField(default=False)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=2.00)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player1} vs {self.player2} - {self.fixture}"

    def clean(self):
        
         # Ensure that the opponent is not the current user
        if self.player1 == self.player2:
            raise ValidationError('Opponent cannot be the same as the current user')
        
        # Check if opponent has already been requested for a game at this date and time
        conflicting_games = HeadToHead.objects.filter(
            player2=self.player2,
            date=self.date,
            time=self.time,
        ).exclude(pk=self.pk)
        if conflicting_games.exists():
            raise ValidationError("The opponent has already been requested for a game at this date and time.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Result(models.Model):
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    home_team_score = models.PositiveIntegerField()
    away_team_score = models.PositiveIntegerField()
    winner = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='wins')
    loser = models.ForeignKey(Matches, on_delete=models.CASCADE, related_name='losses')
    draw = models.BooleanField(default=False)


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE)
    head_to_head = models.ForeignKey(HeadToHead, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        paid_status = "Paid" if self.paid else "Unpaid"
        return f"{self.user.username}'s {paid_status} booking for {self.fixture}"

