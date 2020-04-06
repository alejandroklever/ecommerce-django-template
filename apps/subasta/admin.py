from django.contrib import admin
from apps.subasta.models import SubastaEnCurso, SubastaFinalizada


# Register your models here.
admin.site.register(SubastaEnCurso)
admin.site.register(SubastaFinalizada)
