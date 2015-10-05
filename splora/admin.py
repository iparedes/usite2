from django.contrib import admin

# Register your models here.
from .models import Constant,StarSequence,StarDensity,Position,Sun,Sector

admin.site.register(Constant)
admin.site.register(StarSequence)
admin.site.register(StarDensity)

admin.site.register(Position)
admin.site.register(Sun)
admin.site.register(Sector)
