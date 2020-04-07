from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render


def index(request):
    if not isinstance(request.user, AnonymousUser):
        return render(request, 'index.html', context={'tienda_id': request.user.tienda.id})
    return render(request, 'index.html')
