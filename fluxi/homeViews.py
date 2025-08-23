from django.shortcuts import render


def index(request):
    data = {
        'header':'true',
    }
    return render(request,"home/index.html",data)

def indexEight(request):
    data = {}
    return render(request,"home/indexEight.html",data)

def indexFive(request):
    data = {}
    return render(request,"home/indexFive.html",data)

def indexFour(request):
    data = {}
    return render(request,"home/indexFour.html",data)

def indexSeven(request):
    data = {}
    return render(request,"home/indexSeven.html",data)

def indexSix(request):
    data = {}
    return render(request,"home/indexSix.html",data)

def indexThree(request):
    data = {}
    return render(request,"home/indexThree.html",data)

def indexTwo(request):
    data = {}
    return render(request,"home/indexTwo.html",data)

def contact(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"contact.html",data)

def privacyPolicy(request):
    data = {
        'header':'true',
    }
    return render(request,"privacyPolicy.html",data)

def serviceSingle2(request):
    data = {
    }
    return render(request,"serviceSingle2.html",data)

def serviceSingle3(request):
    data = {}
    return render(request,"serviceSingle3.html",data)

def serviceSingle4(request):
    data = {}
    return render(request,"serviceSingle4.html",data)

def terms(request):
    data = {
        'header':'true',
    }
    return render(request,"terms.html",data)
