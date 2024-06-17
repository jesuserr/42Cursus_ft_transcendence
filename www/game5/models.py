from django.contrib.postgres.fields import ArrayField
from django.db import models
from main.models import User
from django.utils import timezone

class stats(models.Model):
	player_one = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game5_stats')
	player_one_score = models.IntegerField()
	player_one_hits = models.IntegerField()
	player_one_aces = models.IntegerField()
	player_one_win = models.BooleanField(default=False)
	player_two = models.EmailField()	
	player_two_score = models.IntegerField()
	player_two_hits = models.IntegerField()
	player_two_aces = models.IntegerField()
	player_two_win = models.BooleanField(default=False)
	match_length = models.DecimalField(max_digits = 5, decimal_places = 2)
	point_length = ArrayField(models.DecimalField(max_digits = 5, decimal_places = 2), default=list)
	created_at = models.DateTimeField(default=timezone.now)