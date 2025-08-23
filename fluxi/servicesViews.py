from django.shortcuts import render

def emailMarketing(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"services/emailMarketing.html",data)

def influencerMarketing(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"services/influencerMarketing.html",data)

def service(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"services/service.html",data)

def serviceSingle(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"services/serviceSingle.html",data)

def socialMediaMarketing(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"services/socialMediaMarketing.html",data)
