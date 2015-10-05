#https://github.com/ricobl/django-importer

from django_importer.importers.xml_importer import XMLImporter
from .models import Constant,StarSequence,StarDensity


class MyXMLConstantImporter(XMLImporter):
    model=Constant
    item_tag_name='Constant'
    fields=('name','value','desc')
    field_map={'name':'Name',
               'value':'Value',
              'desc':'Desc',
              }
    
    unique_fields=('name',)
    
    def save_item(self, item, data, instance, commit=True):
        if commit:
            instance.save()
        return instance
    
    
class MyXMLStarSequence(XMLImporter):
    model=StarSequence
    item_tag_name='StarSequence'
    fields=('seq','clase','minmass','maxmass','mintemp','maxtemp','minr','maxr','desc','freq')
    field_map={'seq':'Seq',
               'clase':'Class',
               'minmass':'MinMass',
               'maxmass':'MaxMass',
               'mintemp':'MinTemp',
               'maxtemp':'MaxTemp',
               'minr':'MinR',
               'maxr':'MaxR',
               'desc':'Desc',
               'freq':'Freq',
               }
    unique_fields=('clase',)
     
    def save_item(self, item, data, instance, commit=True):
        if commit:
            instance.save()
        return instance
    
class MyXMLStarDensity(XMLImporter):
    model=StarDensity
    item_tag_name='StarDensity'
    fields=('val','factor','ident')
    field_map={'val':'Val',
               'factor':'Factor',
               'ident':'Id',}
    unique_fields=('ident',)
    
    def save_item(self,item, data, instance, commit=True):
        if commit:
            instance.save()
        return instance