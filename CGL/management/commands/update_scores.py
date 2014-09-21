from django.core.management.base import BaseCommand, CommandError
from CGL.models import *
from CGL.settings import current_seasons, current_ladder_season

from datetime import date, timedelta

class Command(BaseCommand):
    args = '<Season Name>'
    help = '''Recalculates all player records, match scores, and school records
            for the requested season. Defaults to current season'''

    def update_match_and_schools(self, season):
        # reset all scores for this season; recompute from scratch.
        for membership in Membership.objects.all().filter(season=season):
            membership.num_wins = 0
            membership.num_losses = 0
            membership.num_ties = 0
            membership.num_byes = 0
            membership.num_forfeits = 0
            membership.save()
            
        # compute the result of each match, based on games and forfeits
        # at the same time, tally up each school's wins/losses
        for round in season.round_set.filter(date__lte=date.today()):
            for b in round.bye_set.all():
                mem = b.school.membership_set.get(season=season)
                mem.num_byes += 1
                mem.save()

            for match in round.match_set.all():
                m = match
                
                # Clear previously calculated match record
                m.score1 = 0
                m.score2 = 0

                # Figure out who won the match. Make note of forfeits.
                for game in m.game_set.all():
                    if game.winning_school == 'School1':
                        m.score1 += 1
                    else:
                        m.score2 += 1
                for forfeit in m.forfeit_set.all():
                    if forfeit.school1_noshow and not forfeit.school2_noshow:
                        m.score2 += 1
                    elif forfeit.school2_noshow and not forfeit.school1_noshow:
                        m.score1 += 1
                m.save()


                if m.is_exhibition:
                    # shortcircuit here. don't want to count exhibition matches
                    # towards season results.
                    continue
                # Update the school's scores based on match result
                mem1 = m.school1.membership_set.get(season=season)
                mem2 = m.school2.membership_set.get(season=season)
               
                for forfeit in m.forfeit_set.all():
                    if forfeit.school1_noshow:
                        mem1.num_forfeits += 1
                    if forfeit.school2_noshow:
                        mem2.num_forfeits += 1
                if m.score1 > m.score2:
                    mem1.num_wins += 1
                    mem2.num_losses += 1
                elif m.score1 < m.score2:
                    mem1.num_losses += 1
                    mem2.num_wins += 1
                else:
                    mem1.num_ties += 1
                    mem2.num_ties += 1
                mem1.save()
                mem2.save()
                
    def update_player_record(self, player):        
        player.num_wins = 0
        player.num_losses = 0

        # Assume player is inactive until evidence to contrary is found
        player.isActive = False

        for game in player.game_set():
            if (date.today() - game.match.round.date) < timedelta(days=180):
                player.isActive = True
            if game.winner == player:
                player.num_wins += 1
            else:
                player.num_losses += 1

        for game in player.laddergame_set():
            if game.season.name == current_ladder_season:
                player.isActive = True
            if game.winner == player:
                player.num_wins += 1
            else:
                player.num_losses += 1

        player.save()
    
    def handle(self, *args, **options):
        if not args:
            self.stdout.write('No season names provided. Defaulting to %s\n' % current_seasons)
            seasons = [Season.objects.get(name=s) for s in current_seasons]
        else:
            seasons = [Season.objects.get(name=arg) for arg in args]
        for season in seasons:
            self.stdout.write('Updating %s\n' % (season.name))
            self.update_match_and_schools(season)
            self.stdout.write('%s match records updated\n' % (season.name))
            self.stdout.write('School records updated from match results\n')
        self.stdout.write('Updating player records\n')
        for player in Player.objects.all():
            self.update_player_record(player)
        self.stdout.write('All player records updated\n')
        self.stdout.write('Done!\n')

