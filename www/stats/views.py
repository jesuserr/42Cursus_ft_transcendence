from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *
from game3.models import stats as stats_pvc         # pvc -> player vs cpu
from game2.models import stats as stats_pvp         # pvp -> player vs player
from main.models import User
import json

@token_required
def index(request):
    token = request.COOKIES.get('tokenid')
    tmp_user = get_user_from_token(token)
    player_vs_cpu = stats_pvc.objects.filter(left_player = tmp_user)
    player_vs_player = stats_pvp.objects.filter(player_one = tmp_user)

    user_stats = {}
    # Avatar and displayname
    user_stats['avatar'] = str(tmp_user.avatar)
    user_stats['display_name'] = tmp_user.displayname
    # Games played, won and lost
    user_stats = calculate_games_stats(player_vs_cpu, player_vs_player, user_stats)
    # Points per game
    user_stats = calculate_points_per_game(player_vs_cpu, player_vs_player, user_stats)
    # Directs points per game
    user_stats = calculate_aces_per_game(player_vs_cpu, player_vs_player, user_stats)
    # Games duration
    user_stats = calculate_match_duration(player_vs_cpu, player_vs_player, user_stats)
    # Game sessions (Match history)
    game_sessions = generate_game_sessions(player_vs_cpu, player_vs_player, user_stats)

    #user_stats_json = json.dumps(user_stats)
    #game_sessions_json = json.dumps(game_sessions)
    #return HttpResponse(render(request, "stats.html", {'user_stats': user_stats_json, 'game_sessions': game_sessions_json}))
    return HttpResponse(render(request, "stats.html", {'user_stats': user_stats, 'game_sessions': game_sessions}))

def calculate_games_stats(player_vs_cpu, player_vs_player, user_stats):
    user_stats['matches_played_pvc'] = player_vs_cpu.count()
    user_stats['matches_played_pvp'] = player_vs_player.count()
    user_stats['matches_played'] = user_stats['matches_played_pvc'] + user_stats['matches_played_pvp']
    user_stats['matches_won_pvc'] = player_vs_cpu.filter(left_player_win = True).count()
    user_stats['matches_won_pvp'] = player_vs_player.filter(player_one_win = True).count()
    user_stats['matches_won'] = user_stats['matches_won_pvc'] + user_stats['matches_won_pvp']
    user_stats['matches_lost_pvc'] = player_vs_cpu.filter(left_player_win = False).count()
    user_stats['matches_lost_pvp'] = player_vs_player.filter(player_one_win = False).count()
    user_stats['matches_lost'] = user_stats['matches_lost_pvc'] + user_stats['matches_lost_pvp']
    user_stats['matches_won_ratio'] = round(user_stats['matches_won'] / user_stats['matches_played'] * 100, 1) if user_stats['matches_played'] else 0
    user_stats['matches_lost_ratio'] = round(user_stats['matches_lost'] / user_stats['matches_played'] * 100, 1) if user_stats['matches_played'] else 0
    user_stats['matches_won_pvc_ratio'] = round(user_stats['matches_won_pvc'] / user_stats['matches_played_pvc'] * 100, 1) if user_stats['matches_played_pvc'] else 0
    user_stats['matches_lost_pvc_ratio'] = round(user_stats['matches_lost_pvc'] / user_stats['matches_played_pvc'] * 100, 1) if user_stats['matches_played_pvc'] else 0
    user_stats['matches_won_pvp_ratio'] = round(user_stats['matches_won_pvp'] / user_stats['matches_played_pvp'] * 100, 1) if user_stats['matches_played_pvp'] else 0
    user_stats['matches_lost_pvp_ratio'] = round(user_stats['matches_lost_pvp'] / user_stats['matches_played_pvp'] * 100, 1) if user_stats['matches_played_pvp'] else 0
    return user_stats

def calculate_points_per_game(player_vs_cpu, player_vs_player, user_stats):
    total_points_pvc_scored = sum([data.left_player_score for data in player_vs_cpu])
    user_stats['scored_goals_per_match_pvc'] = round(total_points_pvc_scored / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_points_pvc_received = sum([data.right_player_score for data in player_vs_cpu])
    user_stats['received_goals_per_match_pvc'] = round(total_points_pvc_received / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_points_pvp_scored = sum([data.player_one_score for data in player_vs_player])
    user_stats['scored_goals_per_match_pvp'] = round(total_points_pvp_scored / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_points_pvp_received = sum([data.player_two_score for data in player_vs_player])
    user_stats['received_goals_per_match_pvp'] = round(total_points_pvp_received / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_points_scored = total_points_pvc_scored + total_points_pvp_scored
    user_stats['scored_goals_per_match'] = round(total_points_scored / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    total_points_received = total_points_pvc_received + total_points_pvp_received
    user_stats['received_goals_per_match'] = round(total_points_received / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    return user_stats

def calculate_aces_per_game(player_vs_cpu, player_vs_player, user_stats):
    total_aces_pvc_scored = sum([data.left_player_aces for data in player_vs_cpu])
    user_stats['scored_aces_per_match_pvc'] = round(total_aces_pvc_scored / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_aces_pvc_received = sum([data.right_player_aces for data in player_vs_cpu])
    user_stats['received_aces_per_match_pvc'] = round(total_aces_pvc_received / user_stats['matches_played_pvc'], 1) if user_stats['matches_played_pvc'] else 0
    total_aces_pvp_scored = sum([data.player_one_aces for data in player_vs_player])
    user_stats['scored_aces_per_match_pvp'] = round(total_aces_pvp_scored / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_aces_pvp_received = sum([data.player_two_aces for data in player_vs_player])
    user_stats['received_aces_per_match_pvp'] = round(total_aces_pvp_received / user_stats['matches_played_pvp'], 1) if user_stats['matches_played_pvp'] else 0
    total_aces_scored = total_aces_pvc_scored + total_aces_pvp_scored
    user_stats['scored_aces_per_match'] = round(total_aces_scored / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    total_aces_received = total_aces_pvc_received + total_aces_pvp_received
    user_stats['received_aces_per_match'] = round(total_aces_received / user_stats['matches_played'], 1) if user_stats['matches_played'] else 0
    return user_stats

def calculate_match_duration(player_vs_cpu, player_vs_player, user_stats):
    user_stats['shortest_match_pvc'] = float(min([data.match_length for data in player_vs_cpu])) if user_stats['matches_played_pvc'] else 0
    user_stats['longest_match_pvc'] = float(max([data.match_length for data in player_vs_cpu])) if user_stats['matches_played_pvc'] else 0
    user_stats['shortest_match_pvp'] = float(min([data.match_length for data in player_vs_player])) if user_stats['matches_played_pvp'] else 0
    user_stats['longest_match_pvp'] = float(max([data.match_length for data in player_vs_player])) if user_stats['matches_played_pvp'] else 0
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

def generate_game_sessions(player_vs_cpu, player_vs_player, user_stats):
    game_sessions = []
    for match in player_vs_cpu:
        match_entry = {
            'date': (match.created_at + timedelta(hours = 2)).strftime('%B %d, %Y - %H:%M:%S'),
            'player': user_stats['display_name'],
            'opponent_avatar': '/static/avatars/CPU.jpg',
            'opponent': 'CPU',
            'player_score': match.left_player_score,
            'opponent_score': match.right_player_score,
            'match_length': float(match.match_length)
        }
        game_sessions.append(match_entry)
    for match in player_vs_player:
        opponent_info = get_user_info(match.player_two)
        match_entry = {
            'date': (match.created_at + timedelta(hours = 2)).strftime('%B %d, %Y - %H:%M:%S'),
            'player': user_stats['display_name'],
            'opponent_avatar': str(opponent_info.avatar),
            'opponent': opponent_info.displayname,
            'player_score': match.player_one_score,
            'opponent_score': match.player_two_score,
            'match_length': float(match.match_length)
        }
        game_sessions.append(match_entry)
    game_sessions = sorted(game_sessions, key=lambda x: x['date'], reverse=True)
    return game_sessions

def get_user_info(email):
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None