import sys
import logging

from django.db import models
from __builtin__ import True
#from django.template.defaultfilters import default

from numpy import random
import numpy

logger=logging.getLogger(__name__)


# Create your models here.

class Constant(models.Model):
    name=models.CharField(max_length=32)
    value=models.FloatField(default=0)
    desc=models.CharField(max_length=1024,default='')

    def __unicode__(self):
        return self.name
    
class StarSequence(models.Model):
    MAINSEQUENCE='MS'
    NONMAINSEQUENCE='NMS'
    SEQTYPES=((MAINSEQUENCE,'Main Sequence'),(NONMAINSEQUENCE,'Non Main Sequence'))
    
    seq=models.CharField(max_length=3,choices=SEQTYPES)
    #seq=models.CharField(max_length=20)
    clase=models.CharField(max_length=4,default='')
    minmass=models.FloatField(default=0)
    maxmass=models.FloatField(default=0)
    mintemp=models.FloatField(default=0)
    maxtemp=models.FloatField(default=0)
    minr=models.FloatField(blank=True,default=0)
    maxr=models.FloatField(blank=True,default=0)
    desc=models.CharField(max_length=128,default='')
    freq=models.FloatField(default=0)
    
    def __unicode__(self):
        return self.clase    
    
class StarDensity(models.Model):
    val=models.FloatField(default=0)
    factor=models.FloatField(default=0)
    ident=models.CharField(max_length=24,default='')
    
    def  __unicode__(self):
        return self.ident
    
    
class Position(models.Model):
    x=models.IntegerField(default=0)
    y=models.IntegerField(default=0)
    z=models.IntegerField(default=0)
       
    def randomPos(self,mini,maxi):
        self.x=random.randint(mini,maxi)
        self.y=random.randint(mini,maxi)
        self.z=random.randint(mini,maxi)
           
    def fromTupla(self,t):
        self.x=t[0]
        self.y=t[1]
        self.z=t[2]
        return self
    
    def __add__(self,other):
        A=Position(self.x+other.x,self.y+other.y,self.z+other.z)
        return A
    
    def inbound(self,limit):
        """Tests if the position coordinates are in [-limit,limit]
        """
        return abs(self.x)<=limit and \
               abs(self.y)<=limit and \
               abs(self.z)<=limit
    
    def __unicode__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+")"
    

class Sector(models.Model):
    name=models.CharField(max_length=32)
    numstars=models.IntegerField(default=0)
    """ We try to keep a constant amount of stars inside the sector,
    so we introduce a correction factor to reduce the real size of the sector in bigger densities
    and increase its size in lower densities
    """
    density=models.ForeignKey(StarDensity)
    
    # Sector has cubic shape. Side is the side of the cube
    side=1000
    #number of stars while populating
    #it is used to avoid multiple queries during position generation
    starsnow=0
    _positions=[]
    _mindelta=0
    _maxdelta=0
    
    def populate(self):
        try:
            # mean and standard deviation
            density=self.density.val
            factor=self.density.factor
            mu=density*(self.side*factor)**3
            sigma=mu/5
            # Watch here!!!!!
            self.numstars=int(random.normal(mu,sigma,1)[0])
            self.numstars=10
            
            self._mindelta=Constant.objects.filter(name="MinDelta")[0].value
            self._maxdelta=Constant.objects.filter(name="MaxDelta")[0].value
            self._starindependece=Constant.objects.filter(name='StarIndependence')[0].value
    
            
            # Save after setting the number of stars
            self.save()
            logger.debug("Populating "+str(self.numstars)+" suns")
            self.starsnow=0
            while self.starsnow<self.numstars:
                S=Sun() 
                S.rand(self)
                logger.debug("Created sun "+S.name)
                p=self.newpos()
                S.pos=p
                S.save()
                self.starsnow=self.starsnow+1              
            return self.numstars
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        
    def newpos(self):
        """Returns a new Position for a solar system
            The position can be independent or belonging to a cluster
        """        
        n=random.random()
        p=Position()
        if (n<self._starindependece) or self.starsnow==0:
            maxi=int(self.side/2)
            mini=-maxi
            p=Position()
            p.randomPos(mini, maxi)
            tupla=(p.x,p.y,p.z)
            while tupla in self._positions:
                p.randomPos(mini, maxi)
                tupla=(p.x,p.y,p.z)
            self._positions.append(tupla)
        else:
            # Star belongs to a cluster
            valido=False
            while not valido:
                # We're gonna select a random star, calculate a new position near it
                # and test if there is empty space
                # We calculate the new position adding deltas to each coordinate
                # This means that the new position could end out of bounds
                # This loop forces the position to be inside the sector bounds
                bounded=False
                while not bounded:
                    i=random.choice(len(self._positions),1)[0]
                    b=self._positions[i]
                    q=Position()
                    q.fromTupla(b)
                    d=Position()
                    d.fromTupla((self.delta(),self.delta(),self.delta()))
                    p=q+d
                    if p.inbound(self.side):
                        bounded=True
                if not (p.x,p.y,p.z) in self._positions:
                    valido=True
        
        self._positions.append((p.x,p.y,p.z))
        p.save()
        return p  
                
    def delta(self):
        delta=random.randint(self._mindelta,self._maxdelta)
        if random.random()<0.5:
            delta=-delta
        return delta


    def addsun(self):      
        return 1
    
    def __unicode__(self):
        return self.name
    
class Sun(models.Model):
    name=models.CharField(max_length=32)
    # in Sun Masses
    mass=models.FloatField()
    # Main Sequence: OBAFGKM
    clase=models.CharField(max_length=4)
    # in Sun Radius
    radius=models.FloatField()
    luminosity=models.FloatField()
    temperature=models.FloatField()
    sector=models.ForeignKey(Sector)
    pos=models.OneToOneField(Position)
    

    def rand(self,sector):
        try:
            ismain=Constant.objects.filter(name="IsMainSequence")[0].value
            ratioradius=Constant.objects.filter(name="RatioRadiusMS")[0].value
            ratioradiuspms=Constant.objects.filter(name="RatioRadiusPMS")[0].value
            sunR=Constant.objects.filter(name="SunRadius")[0].value
            sunL=Constant.objects.filter(name="SunLuminosity")[0].value
            StefanBoltzmann=Constant.objects.filter(name="Stefan-Boltzmann")[0].value
            
            MS=StarSequence.objects.filter(seq="MS")
            NMS=StarSequence.objects.filter(seq="NMS")
            
            self.sector=sector
    
            n=random.random()
            if (n<ismain):
                # Main Sequence
                C=random.choice(MS)
                self.clase=C.clase
                mini=C.minmass
                maxi=C.maxmass
                self.mass=mini+random.random()*maxi
                # MS stars have a relationship Radius=Mass^0.8
                self.radius=self.mass**ratioradius
                mini=C.mintemp
                maxi=C.maxtemp
                self.temperature=mini+random.random()*maxi
                     
                # Calculates with Mass-luminosity relation for MS stars
                if self.mass<0.43:
                    self.luminosity=0.23*(self.mass**2.3)
                elif self.mass<2:
                    self.luminosity=(self.mass**4)
                elif self.mass<20:
                    self.luminosity=1.5*(self.mass**3.5)
                else: # s.mass>20
                    self.luminosity=3200*self.mass
    
            else:
                # Non Main Sequence
                C=random.choice(NMS)
                self.clase=C.clase
                mini=C.minmass
                maxi=C.maxmass
                self.mass=mini+random.random()*maxi
                
                if self.clase!="P":
                    # Not Protostar
                    minr=C.minr
                    maxr=C.maxr
                    self.radius=minr+random.random()*maxr
                else:
                    # Protostar
                    self.radius=self.mass**ratioradiuspms
                
                mini=C.mintemp
                maxi=C.maxtemp
                self.temperature=mini+random.random()*maxi
                
                if self.clase=="WD":
                    # White Dwarf
                    # There are way many cool white dwarfs than hot
                    # We use a gamma distribution (k=2, theta=2)
                    self.temperature=mini+random.gamma(2,2)*maxi
                else:
                    self.temperature=mini+random.random()*maxi
                    # Luminosity equation
                l=4*numpy.pi*((self.radius*sunR*1000)**2)*StefanBoltzmann*(self.temperature)**4
                self.luminosity=l/sunL
            self.newname()
            return self.name
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise 

    
    def newname(self):
        """Returns a name that has not been previously used
        The name starts by the class identifier, and is followed by a random hex number
        """
        valido=False
        maxind=Constant.objects.filter(name='NameMaxIndex')[0].value
        while not valido:
            a=random.randint(maxind)
            b=hex(a).split('x')[1].upper()
            nombre=self.clase+'-'+b
            q=Sun.objects.filter(name=b)
            if not q:
                self.name=nombre
                valido=True
        return nombre
        

    
    def __unicode__(self):
        return self.name
    
    
