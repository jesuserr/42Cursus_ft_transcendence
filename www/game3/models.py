from django.contrib.postgres.fields import ArrayField
from django.db import models
from main.models import User

class stats(models.Model):
	left_player = models.ForeignKey(User, on_delete=models.CASCADE)
	left_player_score = models.IntegerField()
	left_player_hits = models.IntegerField()
	left_player_aces = models.IntegerField()
	right_player = models.EmailField()
	right_player_score = models.IntegerField()
	right_player_hits = models.IntegerField()
	right_player_aces = models.IntegerField()	
	match_length = models.DecimalField(max_digits = 5, decimal_places = 2)
	point_length = ArrayField(models.DecimalField(max_digits = 5, decimal_places = 2), default=list)