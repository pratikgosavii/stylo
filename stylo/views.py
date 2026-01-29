
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from django.db.models import Count
# from petprofile.models import *



@login_required(login_url='login_admin')
def dashboard(request):


    operators_count = 0
    investors_count = 0
    total_money = 0


    # operators_count = operator.objects.all().count()
    # investors_count = investor.objects.all().count()

    total_money = 0
    # total_money = transactions.objects.aggregate(Sum('amount'))['amount__sum']  or 0
    



    context = {
        'operators_count' : operators_count,
        'investors_count' : investors_count,
        'total_money' : total_money
    }
    
    return render(request, 'adminDashboard.html', context)
