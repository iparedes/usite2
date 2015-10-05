import sys
from numpy import random


from django.http import HttpResponse

from .models import Constant, StarSequence, StarDensity, Sector, Sun, Position
from .importer import MyXMLConstantImporter,MyXMLStarSequence, MyXMLStarDensity
from .forms import NewSectorForm

from django.template.context_processors import request
from django.shortcuts import render
from django.http import HttpResponseRedirect

#from __main__ import name

def index(request):
    a=''
    l=Constant.objects.all()
    for s in l:
        a=a+s.name+'<br>'
    return HttpResponse(a)
    
    
def loadxml(request):
    try:
        for e in Constant.objects.all():
            e.delete()
        ConstantXML=MyXMLConstantImporter("usite2/conf/constants.xml")        
        a=ConstantXML.parse()
        
        for e in StarSequence.objects.all():
            e.delete()
        SequenceXML=MyXMLStarSequence("usite2/conf/constants.xml")
        a=SequenceXML.parse()
        
        for e in StarDensity.objects.all():
            e.delete()
        SequenceXML=MyXMLStarDensity("usite2/conf/constants.xml")
        a=SequenceXML.parse()
        
    except:
        a=sys.exc_info()[0]
        print "Unexpected error:", sys.exc_info()[0]
        raise

    return HttpResponse(a)

def newsun(request):
    p=Position()
    p.randomPos(0, 1000)
    
    s=Sun(name='Sol',radius=1,mass=1,clase='G',luminosity=1,temperature=5000)
    s.save()
    
    p.sun=s
    p.save()
    
    return HttpResponse

def newsector(request):
    if request.method=='POST':
        form=NewSectorForm(request.POST)
        if form.is_valid():
            n=form.cleaned_data['name']
            d=form.cleaned_data['density']
                        
            S=Sector(name=n,density=d)
            
            density=S.density.val
            factor=S.density.factor
            mu=density*(S.side*factor)**3
            sigma=mu/5
            S.numstars=int(random.normal(mu,sigma,1)[0])
            S.save()
            
            S.populate()
            return HttpResponseRedirect('/admin/splora/sector')
    else:
        form=NewSectorForm()
    
    return render(request,'splora/newsector.html',{'form':form})




