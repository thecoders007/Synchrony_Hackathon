from django.contrib import admin
from .models import UserJson, UserProfile, Level, BettingBets, Team, TeamMembers 
# Register your models here.


admin.site.register(UserJson)
admin.site.register(UserProfile)
admin.site.register(Level)
admin.site.register(BettingBets)
admin.site.register(Team)
admin.site.register(TeamMembers)
