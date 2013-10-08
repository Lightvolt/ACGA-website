from django.conf.urls.defaults import *
from django.views import static
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import login, logout
from django.conf import settings

urlpatterns = patterns('accounts.views',
    # User homepage / select a player to link to
    (r'^username_reminder/$', 'send_username_reminder'),
    (r'^username_reminder/done/$', direct_to_template, {'template': 'username_reminder_done.html'}),
    (r'^profile/$', 'display_user_info'),
    (r'^edit/profile/$', 'edit_profile_info'),
    (r'^edit/player_link/$', 'link_to_player'),
    (r'^edit/player_link/done$', direct_to_template, {'template': 'player_link_done.html'}),
    (r'^edit/school/([A-Za-z_-]{1,50})/$', 'edit_school_info'),
    (r'^edit/school/([A-Za-z_-]{1,50})/create/player/$', 'create_player'),
    (r'^edit/player/([0-9]{1,4})/$', 'edit_player_info'),
    (r'^edit/match/([0-9]{1,4})/create/game/$', 'create_game'),
    (r'^edit/match/([0-9]{1,4})/create/forfeit/$', 'create_forfeit'),
    (r'^edit/game/([0-9]{1,4})/$', 'edit_game_info'),
    (r'^edit/forfeit/([0-9]{1,4})/$', 'edit_forfeit_info'),
    (r'^link_requests/$', 'display_all_link_requests'),
    (r'^link_requests/([0-9]{1,4})/$', 'edit_link_request'),
)

urlpatterns += patterns('',
    # Account registration/login
    (r'', include('registration.backends.default.urls')),
)

