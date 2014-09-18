import itertools
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from CGL.settings import current_seasons
from CGL.models import Season, Round, Match, Membership, Bye
from CGL.matchmaking import best_matchup

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--season', dest='season', default=None, help="Season name. Leave blank to default to current season."),
        make_option('--round', dest='round', default=0, help="Round number. Leave blank to default to next round")
    )
    args = '<season name>'
    help = '''Creates completely random match pairings for the first round
            that has not happened yet, as judged by today's date'''

    def handle(self, *args, **options):
        if options['season']:
            season = Season.objects.get(name=options['season'])
        else:
            season = Season.objects.get(name=current_seasons[0])
        if options['round']:
            round = Round.objects.get(season=season, round_number=int(options['round']))
        else:
            round = Round.objects.get_next_round()

        all_teams = set(Membership.objects.filter(season=season, still_participating=True))
        already_matched = set(itertools.chain((match.team1, match.team2) for match in round.match_set.all()))
        team_pool = all_teams - already_matched

        if len(team_pool) < 2:
            raise CommandError("Not enough schools to do a pairing for round %s" % round.round_number)

        existing_matchups = Match.objects.filter(round__season=season)

        team_pairings, team_bye = best_matchup(team_pool, existing_matchups)
        for pairing in team_pairings:
            self.stdout.write('%s vs. %s\n' % pairing)
        if team_bye:
            self.stdout.write('%s has a bye this round\n' % team_bye)
        self.stdout.write('Registering matchups!\n')
        for pairing in team_pairings:
            Match.objects.create(round=round, team1=pairing[0], team2=pairing[1], school1=pairing[0].school, school2=pairing[1].school)
        if team_bye:
            Bye.objects.create(round=round, team=team_bye, school=team_bye.school)


