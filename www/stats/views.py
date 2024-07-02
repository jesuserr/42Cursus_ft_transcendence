from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *
from game3.models import stats as stats_pvc         # pvc -> player vs cpu
from game2.models import stats as stats_pvp         # pvp -> player vs player
from game5.models import stats as stats_pvp_tour    # pvp -> player vs player (tournament)
from main.models import User
import json
from itertools import chain
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@token_required
def friendstat(request):
    token = request.COOKIES.get('tokenid')
    tmp = get_user_from_token(token)
    response = render(request, "main_stats_friends.html", {'email': request.POST.get('email'), 'User': tmp})
    return response

@token_required
def friend(request):
    return index(request, request.GET.get('email'))

@token_required
def index(request, useremail = None):
    try:
        tmp_user = User.objects.get(email=useremail)
    except:
        token = request.COOKIES.get('tokenid')
        tmp_user = get_user_from_token(token)
    player_vs_cpu = stats_pvc.objects.filter(left_player = tmp_user)
    player_vs_player = stats_pvp.objects.filter(player_one = tmp_user)
    player_vs_player_tour = stats_pvp_tour.objects.filter(player_one = tmp_user)

    user_stats = {}
    # Avatar and displayname
    user_stats['avatar'] = str(tmp_user.avatar)
    user_stats['display_name'] = tmp_user.displayname
    # Games played, won and lost
    user_stats = calculate_games_stats(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats)
    # Points per game
    user_stats = calculate_points_per_game(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats)
    # Directs points per game
    user_stats = calculate_aces_per_game(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats)
    # Games duration
    user_stats = calculate_match_duration(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats)
    # Generates player gaming history
    player_game_history = generate_game_history(player_vs_cpu, player_vs_player, player_vs_player_tour)
    player_game_history = sorted(player_game_history, key=lambda x: x['date'], reverse=True)
    # Generates server gaming history and removes duplicates
    all_game_history = generate_game_history(stats_pvc.objects.all(), stats_pvp.objects.all(), stats_pvp_tour.objects.all())
    all_game_history = sorted(all_game_history, key=lambda x: x['date'])
    unique_game_history = {}
    for game in reversed(all_game_history):
        unique_game_history[game['date']] = game
    all_game_history = list(unique_game_history.values())

    #user_stats_json = json.dumps(user_stats)
    #player_game_history_json = json.dumps(player_game_history)
    #all_game_history_json = json.dumps(all_game_history)
    return HttpResponse(render(request, "stats_2.html", {'user_stats': user_stats, 'player_game_history': player_game_history, 'all_game_history': all_game_history}))    

def calculate_games_stats(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats):
    user_stats['matches_played_pvc'] = player_vs_cpu.count()
    user_stats['matches_played_pvp'] = player_vs_player.count() + player_vs_player_tour.count()
    user_stats['matches_played'] = user_stats['matches_played_pvc'] + user_stats['matches_played_pvp']
    user_stats['matches_won_pvc'] = player_vs_cpu.filter(left_player_win = True).count()
    user_stats['matches_won_pvp'] = player_vs_player.filter(player_one_win = True).count() + player_vs_player_tour.filter(player_one_win = True).count()
    user_stats['matches_won'] = user_stats['matches_won_pvc'] + user_stats['matches_won_pvp']
    user_stats['matches_lost_pvc'] = player_vs_cpu.filter(left_player_win = False).count()
    user_stats['matches_lost_pvp'] = player_vs_player.filter(player_one_win = False).count() + player_vs_player_tour.filter(player_one_win = False).count()
    user_stats['matches_lost'] = user_stats['matches_lost_pvc'] + user_stats['matches_lost_pvp']
    user_stats['matches_won_ratio'] = round(user_stats['matches_won'] / user_stats['matches_played'] * 100, 1) if user_stats['matches_played'] else 0
    user_stats['matches_lost_ratio'] = round(user_stats['matches_lost'] / user_stats['matches_played'] * 100, 1) if user_stats['matches_played'] else 0
    user_stats['matches_won_pvc_ratio'] = round(user_stats['matches_won_pvc'] / user_stats['matches_played_pvc'] * 100, 1) if user_stats['matches_played_pvc'] else 0
    user_stats['matches_lost_pvc_ratio'] = round(user_stats['matches_lost_pvc'] / user_stats['matches_played_pvc'] * 100, 1) if user_stats['matches_played_pvc'] else 0
    user_stats['matches_won_pvp_ratio'] = round(user_stats['matches_won_pvp'] / user_stats['matches_played_pvp'] * 100, 1) if user_stats['matches_played_pvp'] else 0
    user_stats['matches_lost_pvp_ratio'] = round(user_stats['matches_lost_pvp'] / user_stats['matches_played_pvp'] * 100, 1) if user_stats['matches_played_pvp'] else 0
    user_stats['tournaments_won'] = player_vs_player_tour.filter(player_one_tournament_win = True).count()
    user_stats['tournaments_played'] = countPlayedTournaments(stats_pvp_tour.objects.all())
    user_stats['tournaments_lost'] = user_stats['tournaments_played'] - user_stats['tournaments_won']
    return user_stats

def countPlayedTournaments(object_pvp_tour):
    played_tournaments = 0
    for match in object_pvp_tour:
        if (match.player_one_tournament_win):
            played_tournaments += 1
    return played_tournaments

def calculate_points_per_game(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats):
    total_points_pvc_scored = sum([data.left_player_score for data in player_vs_cpu])
    user_stats['scored_goals_per_match_pvc'] = round(total_points_pvc_scored / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_points_pvc_received = sum([data.right_player_score for data in player_vs_cpu])
    user_stats['received_goals_per_match_pvc'] = round(total_points_pvc_received / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_points_pvp_scored = sum([data.player_one_score for data in player_vs_player]) + sum([data.player_one_score for data in player_vs_player_tour])
    user_stats['scored_goals_per_match_pvp'] = round(total_points_pvp_scored / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_points_pvp_received = sum([data.player_two_score for data in player_vs_player]) + sum([data.player_two_score for data in player_vs_player_tour])
    user_stats['received_goals_per_match_pvp'] = round(total_points_pvp_received / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_points_scored = total_points_pvc_scored + total_points_pvp_scored
    user_stats['scored_goals_per_match'] = round(total_points_scored / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    total_points_received = total_points_pvc_received + total_points_pvp_received
    user_stats['received_goals_per_match'] = round(total_points_received / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    return user_stats

def calculate_aces_per_game(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats):
    total_aces_pvc_scored = sum([data.left_player_aces for data in player_vs_cpu])
    user_stats['scored_aces_per_match_pvc'] = round(total_aces_pvc_scored / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_aces_pvc_received = sum([data.right_player_aces for data in player_vs_cpu])
    user_stats['received_aces_per_match_pvc'] = round(total_aces_pvc_received / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_aces_pvp_scored = sum([data.player_one_aces for data in player_vs_player]) + sum([data.player_one_aces for data in player_vs_player_tour])
    user_stats['scored_aces_per_match_pvp'] = round(total_aces_pvp_scored / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_aces_pvp_received = sum([data.player_two_aces for data in player_vs_player]) + sum([data.player_two_aces for data in player_vs_player_tour])
    user_stats['received_aces_per_match_pvp'] = round(total_aces_pvp_received / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_aces_scored = total_aces_pvc_scored + total_aces_pvp_scored
    user_stats['scored_aces_per_match'] = round(total_aces_scored / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    total_aces_received = total_aces_pvc_received + total_aces_pvp_received
    user_stats['received_aces_per_match'] = round(total_aces_received / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    return user_stats

def calculate_match_duration(player_vs_cpu, player_vs_player, player_vs_player_tour, user_stats):
    user_stats['shortest_match_pvc'] = float(min([data.match_length for data in player_vs_cpu])) if user_stats['matches_played_pvc'] else 0
    user_stats['longest_match_pvc'] = float(max([data.match_length for data in player_vs_cpu])) if user_stats['matches_played_pvc'] else 0
    user_stats['shortest_match_pvp'] = float(min([data.match_length for data in chain(player_vs_player, player_vs_player_tour)])) if user_stats['matches_played_pvp'] else 0
    user_stats['longest_match_pvp'] = float(max([data.match_length for data in chain(player_vs_player, player_vs_player_tour)])) if user_stats['matches_played_pvp'] else 0
    if user_stats['shortest_match_pvc'] != 0 and user_stats['shortest_match_pvp'] != 0:
        user_stats['shortest_match'] = min(user_stats['shortest_match_pvc'], user_stats['shortest_match_pvp'])
    elif user_stats['shortest_match_pvc'] != 0:
        user_stats['shortest_match'] = user_stats['shortest_match_pvc']
    elif user_stats['shortest_match_pvp'] != 0:
        user_stats['shortest_match'] = user_stats['shortest_match_pvp']
    else:
        user_stats['shortest_match'] = 0
    user_stats['longest_match'] = max(user_stats['longest_match_pvc'], user_stats['longest_match_pvp'])
    return user_stats

def generate_game_history(object_pvc, object_pvp, object_pvp_tour):
    game_sessions = []
    for match in object_pvc:
        player_info = get_user_info(match.left_player)
        match_entry = {
            'date': (match.created_at + timedelta(hours = 2)).strftime('%B %d, %Y - %H:%M:%S'),
            'player': player_info.displayname,
            'player_avatar': str(player_info.avatar),
            'opponent': 'CPU',
            'opponent_avatar': '/static/avatars/CPU.jpg',
            'player_score': match.left_player_score,
            'opponent_score': match.right_player_score,
            'match_length': float(match.match_length),
            'tournament': match.tournament
        }
        game_sessions.append(match_entry)
    for match in chain(object_pvp, object_pvp_tour):
        player_one_info = get_user_info(match.player_one)
        player_two_info = get_user_info(match.player_two)
        match_entry = {
            'date': (match.created_at + timedelta(hours = 2)).strftime('%B %d, %Y - %H:%M:%S'),
            'player': player_one_info.displayname,
            'player_avatar': str(player_one_info.avatar),
            'opponent': player_two_info.displayname,
            'opponent_avatar': str(player_two_info.avatar),
            'player_score': match.player_one_score,
            'opponent_score': match.player_two_score,
            'match_length': float(match.match_length),
            'tournament': match.tournament,
            'tournament_name': match.tournament_name
        }        
        game_sessions.append(match_entry)
    return game_sessions

def get_user_info(email):
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None