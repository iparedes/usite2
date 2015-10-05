from django.forms import ModelForm
from models import Sector

class NewSectorForm(ModelForm):
    class Meta:
        model=Sector
        fields=['name','density']
    