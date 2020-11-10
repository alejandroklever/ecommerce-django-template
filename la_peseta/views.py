from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect


def index(request):
    if not isinstance(request.user, AnonymousUser):
        if not hasattr(request.user, 'tienda'):
            return redirect('tienda:mostrar-tienda')
        return render(request, 'index.html', context={'tienda_id': request.user.tienda.id})
    return render(request, 'index.html')
