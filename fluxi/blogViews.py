from django.shortcuts import render

def blog(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"blog/blog.html",data)

def blogDetails(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"blog/blogDetails.html",data)

def blogGrid(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"blog/blogGrid.html",data)

def blogGrid2(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"blog/blogGrid2.html",data)

def blogGrid3(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"blog/blogGrid3.html",data)

def blogLeftSidebar(request):
    data = {
        'header':'true',
        'footer':'true',
    }
    return render(request,"blog/blogLeftSidebar.html",data)