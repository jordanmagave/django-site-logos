from django.shortcuts import render

def caseStudies(request):
    data = {
    'footer': 'true',
    }
    return render(request,"work/caseStudies.html",data)

def singleCaseStudies(request):
    data = {
    'header': 'true',
    'footer': 'false',
    }
    return render(request,"work/singleCaseStudies.html",data)