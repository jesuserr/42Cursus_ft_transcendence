from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from main.token import *
from game3.models import stats as stats_pvc         # pvc -> player vs cpu
from game2.models import stats as stats_pvp         # pvp -> player vs player

@token_required
def index(request):
    token = request.COOKIES.get('tokenid')
    tmp_user = get_user_from_token(token)
    player_vs_cpu = stats_pvc.objects.filter(left_player = tmp_user)
    player_vs_player = stats_pvp.objects.filter(player_one = tmp_user)
    if not player_vs_cpu or not player_vs_player:                               # revise div by 0
        return HttpResponse(render(request, "stats.html", {'variable': 0}))     # improve later

    user_stats = {}
    # Avatar and displayname
    user_stats['avatar'] = tmp_user.avatar
    user_stats['displayname'] = tmp_user.displayname
    # Games played, won and lost
    user_stats = calculate_games_stats(player_vs_cpu, player_vs_player, user_stats)   
    # Points per game
    user_stats = calculate_points_per_game(player_vs_cpu, player_vs_player, user_stats)
    # Directs points per game
    user_stats = calculate_aces_per_game(player_vs_cpu, player_vs_player, user_stats)
    # Games duration
    user_stats = calculate_match_duration(player_vs_cpu, player_vs_player, user_stats)
       
    #average_length = total_length / len(player_vs_cpu) if player_vs_cpu else 0    
    print(user_stats)
    return HttpResponse(render(request, "stats.html", {'user_stats': user_stats}))

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
    user_stats['matches_won_ratio'] = round(user_stats['matches_won'] / user_stats['matches_played'] * 100, 1)
    user_stats['matches_lost_ratio'] = round(user_stats['matches_lost'] / user_stats['matches_played'] * 100, 1)
    user_stats['matches_won_pvc_ratio'] = round(user_stats['matches_won_pvc'] / user_stats['matches_played_pvc'] * 100, 1)
    user_stats['matches_lost_pvc_ratio'] = round(user_stats['matches_lost_pvc'] / user_stats['matches_played_pvc'] * 100, 1)
    user_stats['matches_won_pvp_ratio'] = round(user_stats['matches_won_pvp'] / user_stats['matches_played_pvp'] * 100, 1)
    user_stats['matches_lost_pvp_ratio'] = round(user_stats['matches_lost_pvp'] / user_stats['matches_played_pvp'] * 100, 1)
    return user_stats

def calculate_points_per_game(player_vs_cpu, player_vs_player, user_stats):
    total_points_pvc_scored = sum([data.left_player_score for data in player_vs_cpu])
    user_stats['scored_goals_per_match_pvc'] = round(total_points_pvc_scored / user_stats['matches_played_pvc'], 1)
    total_points_pvc_received = sum([data.right_player_score for data in player_vs_cpu])
    user_stats['received_goals_per_match_pvc'] = round(total_points_pvc_received / user_stats['matches_played_pvc'], 1)
    total_points_pvp_scored = sum([data.player_one_score for data in player_vs_player])
    user_stats['scored_goals_per_match_pvp'] = round(total_points_pvp_scored / user_stats['matches_played_pvp'], 1)
    total_points_pvp_received = sum([data.player_two_score for data in player_vs_player])
    user_stats['received_goals_per_match_pvp'] = round(total_points_pvp_received / user_stats['matches_played_pvp'], 1)
    total_points_scored = total_points_pvc_scored + total_points_pvp_scored
    user_stats['scored_goals_per_match'] = round(total_points_scored / user_stats['matches_played'], 1)
    total_points_received = total_points_pvc_received + total_points_pvp_received
    user_stats['received_goals_per_match'] = round(total_points_received / user_stats['matches_played'], 1)
    return user_stats

def calculate_aces_per_game(player_vs_cpu, player_vs_player, user_stats):
    total_aces_pvc_scored = sum([data.left_player_aces for data in player_vs_cpu])
    user_stats['scored_aces_per_match_pvc'] = round(total_aces_pvc_scored / user_stats['matches_played_pvc'], 1)
    total_aces_pvc_received = sum([data.right_player_aces for data in player_vs_cpu])
    user_stats['received_aces_per_match_pvc'] = round(total_aces_pvc_received / user_stats['matches_played_pvc'], 1)
    total_aces_pvp_scored = sum([data.player_one_aces for data in player_vs_player])
    user_stats['scored_aces_per_match_pvp'] = round(total_aces_pvp_scored / user_stats['matches_played_pvp'], 1)
    total_aces_pvp_received = sum([data.player_two_aces for data in player_vs_player])
    user_stats['received_aces_per_match_pvp'] = round(total_aces_pvp_received / user_stats['matches_played_pvp'], 1)
    total_aces_scored = total_aces_pvc_scored + total_aces_pvp_scored
    user_stats['scored_aces_per_match'] = round(total_aces_scored / user_stats['matches_played'], 1)
    total_aces_received = total_aces_pvc_received + total_aces_pvp_received
    user_stats['received_aces_per_match'] = round(total_aces_received / user_stats['matches_played'], 1)
    return user_stats

def calculate_match_duration(player_vs_cpu, player_vs_player, user_stats):
    user_stats['shortest_match_pvc'] = min([data.match_length for data in player_vs_cpu])
    user_stats['longest_match_pvc'] = max([data.match_length for data in player_vs_cpu])
    user_stats['shortest_match_pvp'] = min([data.match_length for data in player_vs_player])
    user_stats['longest_match_pvp'] = max([data.match_length for data in player_vs_player])    
    user_stats['shortest_match'] = min(user_stats['shortest_match_pvc'], user_stats['shortest_match_pvp'])
    user_stats['longest_match'] = max(user_stats['longest_match_pvc'], user_stats['longest_match_pvp'])
    return user_stats