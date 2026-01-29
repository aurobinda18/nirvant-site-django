# team/views.py
from django.shortcuts import render
from .models import TeamMember
from Home.models import SuperMentor

def team_view(request):
    # Get mentors and super mentors from Home.SuperMentor
    super_mentors = SuperMentor.objects.filter(designation='super_mentor')
    mentors = SuperMentor.objects.filter(designation='mentor')
    
    # Get team members grouped by team (for FOUNDERS, TECH_TEAM, etc.)
    team_members = TeamMember.objects.all()
    
    # Group by team_name
    teams = {
        'FOUNDERS': [],
        'SUPER_MENTORS': list(super_mentors),  # From Home app
        'MENTORS': list(mentors),  # From Home app
        'TECH_TEAM': [],
    }
    
    for member in team_members:
        if member.team_name in teams:
            teams[member.team_name].append(member)
    
    context = {
        'teams': teams,
        'user': request.user
    }
    
    return render(request, 'team.html', context)