from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout as auth_logout
from twilio.rest import Client
import random
from .models import *


# Create your views here.
def dashboard(request):
	if request.user.is_authenticated:
		up = UserProfile.objects.get(user_detail=request.user)
		print(up.emp_Id)
		team = Team.objects.all()
		print(team)
		leaderboard = UserProfile.objects.all().order_by('-level_points')[0:5]
		print(leaderboard)
		for a in leaderboard:
			print(a.level_points)
		team_mem = TeamMembers.objects.get(user_profile = up)
		all_mem = TeamMembers.objects.filter(team = team_mem.team)
		for i in all_mem:
			print(i.team.name)	
		return render(request,'index.html',{"up" : up, "team":team, "leaderboard":leaderboard, "all_mem":all_mem})
	else:
		return redirect('/login/')


def profile(request):
	if request.user.is_authenticated:
		up = UserProfile.objects.get(user_detail=request.user)
		print(up.emp_Id)

		level = Level.objects.get(user_profile=up)

		required = creds_level_conversion(up.level+1)

		progress = str(str(up.level_points) + '/' + str(required))
		progp = up.level_points/required*100

		return render(request,'user_profile.html',{"up" : up, "level" : level,
		 "progress" : progress, "progp" : progp })
	else:
		return redirect('/login/')


def login_site(request):
	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(username = email, password = password)
		if user:
			login(request, user)
			return redirect('/')
		else:
			return redirect('/login/')

	else:
		return render(request, 'login.html')

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect('/logout_complete/')
    else:
        return redirect('/login/')


def bet(request):
	if request.user.is_authenticated:
		print(request.user)
		up = UserProfile.objects.get(user_detail=request.user)
		print(up.emp_Id)

		return render(request,'bet.html',{"up" : up})

	else:
		return redirect('/login/')


def logout_complete(request):
	return render(request, 'logout_complete.html')

def create_trade(request):
	if request.method == "POST":
		d=request.POST['duration']
		c=int(d)*100
		print(c)
		trade = Trading.objects.create(issuer_name=request.POST['name'],duration=request.POST['duration'],creds=c,available=True)
		return redirect("/profile/")


def trading(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			iname = request.POST['iname']
			duration = request.POST['duration']
			creds = request.POST['creds']
			up = UserProfile.objects.get(user_detail=request.user)
			cname=up.name
			trade = Trading.objects.filter(issuer_name=iname,duration=duration,creds=creds).update(claimer_name=cname,available=False)


			return redirect("/trading/")
		else:
			up = UserProfile.objects.get(user_detail=request.user)
			t = Trading.objects.filter(available=True)
			ct = Trading.objects.filter(available=False)
			# print(ct)
			return render(request,'trading.html', {'t' : t, 'ct' : ct, "up" : up})

	else:
		return redirect('/login/')


def bettingstatus(request):
	up = UserProfile.objects.get(user_detail = request.user)	
	if request.method  == "POST":
		if request.user.is_authenticated:
			qsbet = request.POST['qsbet']
			qscred = request.POST['qscred']
			oscred = request.POST['oscred']
			osbet = request.POST['osbet']
			cqsbet = request.POST['cqsbet']
			cqscred = request.POST['cqscred']
			fcrbet = request.POST['fcrbet']
			fcrcred = request.POST['fcrcred']
			cctbet = request.POST['cctbet']
			cctcred = request.POST['cctcred']
			bb = BettingBets.objects.create(user_profile = up, cct = cctcred, cct_bet = cctbet, 
				qual_score = cqscred, qual_score_bet = cqsbet, os = oscred, os_bet = osbet,
				 fcr = fcrcred, fcr_bet = fcrbet, no_of_queries_solved = qscred, 
				 no_of_queries_solved_bet = qsbet, 
				 total_bet = int(qscred) + int(oscred) + int(cqscred)+ int(fcrcred) + int(cctcred))
			bb.save()
			up.betting_points-=int(qscred) + int(oscred) + int(cqscred)+ int(fcrcred) + int(cctcred)
			up.save()
			bx = BetBoxes.objects.create(user_profile = up, os = 0, fcr = 0, noqs = 0)
			bx.save()
			return redirect('/betting_status/')

	else:
		bx = BetBoxes.objects.get(user_profile = up)
		return render(request, 'bettingstatus.html', {"up" : up, "bx" : bx})


def trade_creds(request):
	if request.user.is_authenticated:
		
		up = UserProfile.objects.get(user_detail=request.user)

		if request.method == 'POST':
			cctbet = request.POST['cctbet']
			print(cctbet)

			val = up.betting_points - int(cctbet)
			up.betting_points = val

			total_conversion = ((15 / 100) * int(cctbet))

			up.level_points = up.level_points + total_conversion

			tip = creds_level_conversion(up.level+1)

			if up.level_points > tip:
				up.level = up.level + 1

			up.save()

			return redirect('/trade_creds/')

		else:

			return render(request, 'trade_creds.html', { 'up' : up })

	else:
		return redirect('/login/')


def creds_level_conversion(level): 
    switcher = {
        1: 1000,
        2: 1500, 
        3: 2000,
        4: 3000, 
        5: 5000,
    } 

    return switcher.get(level, 99999)


def team_view(request):
	if request.user.is_authenticated:
		up = UserProfile.objects.get(user_detail=request.user)

		if up.is_manager:

			team = Team.objects.get(team_leader=up)
			# print(team)

			listing = TeamMembers.objects.filter(team=team)
			print(listing)

			details = []
			for i in listing:
				ups = UserProfile.objects.get(emp_Id=int(str(i)))
				details.append(Level.objects.get(user_profile=ups))
				print(details)

			link = {}
			link = dict(zip(listing, details))
			print(link)

			return render(request, 'team_view.html', { 'up' : up, 'listing' : listing,
			 'link' : link })

		else:
			return HttpResponse('You Should Not Be Here!')

	else:
		return redirect('/login/')

def complete_call(request):
	if request.user.is_authenticated:
		up = UserProfile.objects.get(user_detail=request.user)
		return render(request,'call.html',{"up" : up})		



def call(request):



# Your Account Sid and Auth Token from twilio.com/console

	account_sid = 'ACc74819c84a2b3b685476b29d1affba76'
	auth_token = 'f209d606239c309c0e31c2009dcfbe81'
	client = Client(account_sid, auth_token)
	call = client.calls.create(
	                        url='http://demo.twilio.com/docs/voice.xml',
	                        to='+917303153300',
	                        from_='+17342924458'
	                    )

	
	while(client.calls(call.sid).fetch().status!="completed"):
		pass
	print(client.calls(call.sid).fetch().duration)
	duration = client.calls(call.sid).fetch().duration
	up = UserProfile.objects.get(user_detail=request.user)
	request.session['duration'] = duration
	return redirect('/callfinal/')

def callfinal(request):
	if request.method == "POST":
		duration = request.POST['duration']
		up = UserProfile.objects.get(user_detail = request.user)
		bb = BettingBets.objects.get(user_profile = up)
		print(duration)
		print(bb.cct)
		if(int(duration) <= int(bb.cct)):
			print("hi")
			if int(bb.cct) >= 50 and int(bb.cct) <= 100:
				points = int(bb.cct_bet)*1.1
			elif int(bb.cct) >100 and int(bb.cct) <= 150:
				points = int(bb.cct_bet) * 1.15
			else:
				points = int(bb.cct_bet) * 1.2
			up.betting_points += points
			print(up.betting_points)

			#level points calculations
			#cct
			#qual_score
			#os
			#fcr
			#noofqueries
		usr = UserJson.objects.get(user_detail = request.user)
		incr = usr.currentCCT*0.25+usr.qcal_Score*0.15+usr.fcr_Rate*0.15+usr.totalVOCScore*0.30+usr.sales_Coverted*0.05
		up.level_points+=incr
		if up.level_points > 50:
			up.level=1
		if up.level_points > 200:
			up.level=2
		if up.level_points > 215:
			up.level=3	
		up.save()

		bx = BetBoxes.objects.get(user_profile = up)
		bx.fcr += random.randint(1,10)
		bx.os += random.randint(1,10) 
		bx.noqs += random.randint(1,10)
		bx.save()  
		print(up.level_points)
				
		return redirect('/')	
	else:
		up = UserProfile.objects.get(user_detail=request.user)
		return render(request,'callcomp.html',{"up" : up, "duration":request.session['duration']})
