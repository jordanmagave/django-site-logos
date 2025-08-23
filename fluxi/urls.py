"""
URL configuration for fluxi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from fluxi import homeViews
from fluxi import blogViews
from fluxi import pagesViews
from fluxi import servicesViews
from fluxi import workViews

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', homeViews.index, name ='index'),
    path('index', homeViews.index, name ='index'),
    path('index-eight', homeViews.indexEight, name ='indexEight'),
    path('index-five', homeViews.indexFive, name ='indexFive'),
    path('index-four', homeViews.indexFour, name ='indexFour'),
    path('index-seven', homeViews.indexSeven, name ='indexSeven'),
    path('index-six', homeViews.indexSix, name ='indexSix'),
    path('index-three', homeViews.indexThree, name ='indexThree'),
    path('index-two', homeViews.indexTwo, name ='indexTwo'),
    path('contact', homeViews.contact, name ='contact'),
    path('privacy-policy',homeViews.privacyPolicy, name ='privacyPolicy'),
    path('service-single2',homeViews.serviceSingle2, name ='serviceSingle2'),
    path('service-single3',homeViews.serviceSingle3, name ='serviceSingle3'),
    path('service-single4',homeViews.serviceSingle4, name ='serviceSingle4'),
    path('terms',homeViews.terms, name ='terms'),

    # blog
    path('blog',blogViews.blog, name ='blog'),
    path('blog-details',blogViews.blogDetails, name ='blogDetails'),
    path('blog-grid',blogViews.blogGrid, name ='blogGrid'),
    path('blog-grid2',blogViews.blogGrid2, name ='blogGrid2'),
    path('blog-grid3',blogViews.blogGrid3, name ='blogGrid3'),
    path('blog-left-sidebar',blogViews.blogLeftSidebar, name ='blogLeftSidebar'),

    # pages
    path('about',pagesViews.about, name ='about'),
    path('book-demo',pagesViews.bookDemo, name ='bookDemo'),
    path('faq',pagesViews.faq, name ='faq'),
    path('free',pagesViews.free, name ='free'),
    path('page-error',pagesViews.pageError, name ='pageError'),
    path('pricing',pagesViews.pricing, name ='pricing'),
    path('team',pagesViews.team, name ='team'),

    # services
    path('email-marketing',servicesViews.emailMarketing, name ='emailMarketing'),
    path('influencer-marketing',servicesViews.influencerMarketing, name ='influencerMarketing'),
    path('service',servicesViews.service, name ='service'),
    path('service-single',servicesViews.serviceSingle, name ='serviceSingle'),
    path('social-media-marketing',servicesViews.socialMediaMarketing, name ='socialMediaMarketing'),

    # work
    path('case-studies',workViews.caseStudies, name ='caseStudies'),
    path('single-case-studies',workViews.singleCaseStudies, name ='singleCaseStudies'),

]
