from django.template.loader import get_template
from django.shortcuts import get_object_or_404, get_list_or_404, redirect
from django.template.defaultfilters import slugify
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from CGL.forms import CreateGameCommentForm
from CGL.models import School, Season, Round, Membership, Game, Player, GameComment
from settings import current_seasons

def display_school(request):
    all_schools = School.objects.filter(inCGL=True)
    recent_schools = all_schools.order_by("-id")[:3]

    return direct_to_template(request, 'schools.html', locals())

def display_roster(request, school_name):
    school_name = school_name.strip().replace('_', ' ').replace('-', ' ')
    school = get_object_or_404(School, name=school_name)
    roster = school.player_set.filter(isActive=1).order_by('rank')
    inactives = school.player_set.filter(isActive=0).order_by('rank')
    participating_seasons = Membership.objects.filter(school__name=school_name)

    return direct_to_template(request, 'schools-detailed.html', locals())

def display_current_seasons(request):
    return display_seasons(request, current_seasons)
    
def display_seasons(request, season_name):
    if isinstance(season_name, basestring):
        season_name = season_name.strip()
        requested_seasons = [get_object_or_404(Season, slug_name=season_name)]
    elif hasattr(season_name, '__iter__'):
        requested_seasons = [get_object_or_404(Season, name=s) for s in season_name]

    all_seasons = Season.objects.all() 

    return direct_to_template(request, 'results.html', locals())

def display_player_search(request):
    query = request.GET.get('query', '')
    errors = []

    if query:
        results = Player.objects.filter(name__icontains=query) | Player.objects.filter(KGS_username__icontains=query)
        
        # If only one player found, automatically redirect to that player's page
        if len(results) == 1:
            return HttpResponseRedirect(results[0].get_absolute_url())

        if not results:
            errors.append('No results')

    return direct_to_template(request, 'players.html', locals())

def display_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    return direct_to_template(request, 'players-detailed.html', locals())

def display_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    form = CreateGameCommentForm()
    return direct_to_template(request, 'game-detailed.html', locals())

def submit_comment(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.method == 'POST':
        form = CreateGameCommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            user = request.user
            new_comment = GameComment(game=game, comment=comment, user=user)
            new_comment.save()
    
    return HttpResponseRedirect(game.get_absolute_url())

