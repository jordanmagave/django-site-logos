from django.shortcuts import render

def about(request):
    data = {
        'footer':'true',
    }
    return render(request,"pages/about.html",data)

def bookDemo(request):
    data = {
        'header':'true',
    }
    return render(request,"pages/bookDemo.html",data)

def faq(request):
    data = {
        'header':'true',
    }
    return render(request,"pages/faq.html",data)

def free(request):
    data = {
        'header':'true',
    }
    return render(request,"pages/free.html",data)

def pageError(request):
    data = {}
    return render(request,"pages/pageError.html",data)

def pricing(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"pages/pricing.html",data)

def team(request):
    data = {
        'footer':'true',
    }
    return render(request,"pages/team.html",data)
