from django.contrib.postgres.fields import ArrayField
from django.db import models
from pongapi.models import User
from django.utils import timezone

class stats(models.Model):
	left_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game3_stats')
	left_player_score = models.IntegerField()
	left_player_hits = models.IntegerField()
	left_player_aces = models.IntegerField()	
	left_player_win = models.BooleanField(default=False)
	right_player = models.EmailField()
	right_player_score = models.IntegerField()
	right_player_hits = models.IntegerField()
	right_player_aces = models.IntegerField()	
	right_player_win = models.BooleanField(default=False)
	match_length = models.DecimalField(max_digits = 5, decimal_places = 2)
	point_length = ArrayField(models.DecimalField(max_digits = 5, decimal_places = 2), default=list)
	created_at = models.DateTimeField(default=timezone.now)
	tournament = models.BooleanField(default=False)