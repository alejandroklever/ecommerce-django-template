from django.shortcuts import render


# Create your views here.

def index(request, pk):
    return render(request, 'compra_index.html')
