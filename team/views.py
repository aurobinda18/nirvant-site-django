# team/views.py
from django.shortcuts import render
from .models import TeamMember

def team_view(request):
    # Get all team members grouped by team
    team_members = TeamMember.objects.all()
    
    # Group by team_name
    teams = {
        'FOUNDERS': [],
        'SUPER_MENTORS': [],
        'MENTORS': [],
    }
    
    for member in team_members:
        teams[member.team_name].append(member)
    
    # Get only mentors for the carousel (MENTORS team)
    mentors = TeamMember.objects.filter(team_name='MENTORS')
    
    context = {
        'teams': teams,
        'mentors': mentors,
        'user': request.user
    }
    
    return render(request, 'team.html', context)