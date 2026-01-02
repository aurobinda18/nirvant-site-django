# team/views.py
from django.shortcuts import render
from .models import TeamMember

def team_view(request):
    teams = {
        'Founders': TeamMember.objects.filter(team_name='FOUNDERS'),
        'Super_Mentors': TeamMember.objects.filter(team_name='SUPER_MENTORS'),
        'Tech_Team': TeamMember.objects.filter(team_name='TECH'),
        'Design_Team': TeamMember.objects.filter(team_name='DESIGN'),
        'Marketing_Team': TeamMember.objects.filter(team_name='MARKETING'),
    }
    return render(request, 'team.html', {'teams': teams})