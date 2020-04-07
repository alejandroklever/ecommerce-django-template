from django.shortcuts import render


def index(request):
    return render(request, 'index.html', context={'tienda_id': request.user.tienda.id})
