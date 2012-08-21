from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.views.generic.simple import direct_to_template

from models import School, Season, Round, Membership, Game, Player
from settings import current_season_name

def display_school(request):
    all_schools = School.objects.all()
    recent_schools = School.objects.order_by("-id")[:5]

    return direct_to_template(request, 'schools.html', locals())

def display_roster(request, school_name):
    school_name = school_name.strip().replace('_', ' ').replace('-', ' ')
    school = get_object_or_404(School, name=school_name)
    roster = school.player_set.filter(isActive=1).order_by('rank')
    retired = school.player_set.filter(isActive=0)
    
    return direct_to_template(request, 'schools-detailed.html', locals())

def display_results(request):
    current_season = Season.objects.get(name=current_season_name)
    all_seasons = Season.objects.all()
    all_memberships = Membership.objects.filter(season=current_season).order_by('-num_wins', 'num_losses', '-num_ties')

    return direct_to_template(request, 'results.html', locals())
    
def display_season(request, season_name):
    season_name = season_name.strip()
    season = get_object_or_404(Season, slug_name=season_name)
    all_memberships = Membership.objects.filter(season=season).order_by('-num_wins', 'num_losses', '-num_ties')
    
    return direct_to_template(request, 'results-detailed.html', locals())

def display_player_search(request):
    # To implement: player searching
    return direct_to_template(request, 'players.html', locals())

def display_player(request, player_name):
    player_name = player_name.strip().replace('_', ' ').replace('-', ' ')
    player = get_object_or_404(Player, name=player_name)

    return direct_to_template(request, 'players-detailed.html', locals())

def display_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    return direct_to_template(request, 'game-detailed.html', locals())
