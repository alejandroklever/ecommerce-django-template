import datetime
import threading
from time import sleep

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from apps.tienda.models import Producto
from .models import SubastaFinalizada, SubastaEnCurso

mutex = threading.Lock()


def subasta_init(request):
    template = loader.get_template("init.html")
    return HttpResponse(template.render({'user_name': request.user.username}))


def listar_subastas(request):
    user = request.user
    subastas_en_curso = SubastaEnCurso.objects.filter(tienda__usuario_id=user.id)
    template = loader.get_template("listar_subastas.html")
    context = {'subastas_en_curso': subastas_en_curso, 'user': user.username}
    return HttpResponse(template.render(context, request))


def listar_subastas_usuario(request):
    user = request.user
    subastas_usuario = SubastaEnCurso.objects.filter(pujante_id=user.id)
    template = loader.get_template("listar_subastas_usuario.html")
    context = {'subastas_usuario': subastas_usuario, 'user': user.username}
    return HttpResponse(template.render(context, request))


def listar_subasta_terminadas(request):
    user = request.user
    subastas_terminada = SubastaFinalizada.objects.filter(tienda__usuario_id=user.id)
    template = loader.get_template("listar_subastas_finalizadas.html")
    context = {'subastas_finalizadas': subastas_terminada, 'user': user.username}
    return HttpResponse(template.render(context, request))


def agregar_subasta(request):
    template = loader.get_template('agregar_subasta.html')
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            _precio = request.POST['precio']
            descripcion = request.POST['descripcion']
            imagen = request.POST['img']
            _prod = Producto(nombre=nombre, precio=_precio, descripcion=descripcion, imagen=imagen)
            _prod.save()
            hora = request.POST['hora_fecha'].split('-')
            hora_t = request.POST['hora_reloj'].split(':')
            _final = datetime.datetime(year=int(hora[0]), month=int(hora[1]), day=int(hora[2]), hour=int(hora_t[0]),
                                       minute=int(hora_t[1]))
            _start = datetime.datetime.now()
            _tienda = request.user.tienda
            new_sub = SubastaEnCurso(pujante=None, tienda=_tienda, producto=_prod, precio_inicial=_precio,
                                     precio_actual=_precio, hora_inicio=_start, hora_final=_final)
            new_sub.save()
            return HttpResponseRedirect('/subasta')
        except Exception as exc:
            if exc.args[0] == 'User has no tienda.':
                return HttpResponse(template.render({'message': "Necesitas una tienda para poder subastar productos"}))
            return HttpResponse(template.render({'message': "Conjunto de datos Invalido"}, request))
    else:
        return HttpResponse(template.render({}, request))


def busqueda_mostrar_subastas(request):
    try:
        _name = request.GET['prod_name']
    except:
        _name = ''
    subastas_usuario = SubastaEnCurso.objects.filter(pujante_id=request.user.id)
    subastas_tienda = SubastaEnCurso.objects.filter(tienda__usuario_id=request.user.id)
    template = loader.get_template('buscar_subastas.html')
    results = [elem for elem in SubastaEnCurso.objects.filter(producto__nombre__contains=_name) if
               elem not in subastas_usuario and elem not in subastas_tienda]
    return HttpResponse(template.render({'elems': results}, request))


def pujar(request, name, precio):
    _precio = float(precio)
    _precio_nuevo = float(request.POST['new_price'])
    if _precio_nuevo <= _precio:
        return HttpResponseRedirect('/subasta/buscar')
    subastas = SubastaEnCurso.objects.filter(precio_actual=precio, producto__nombre=name)
    _subasta = subastas[0]
    _subasta.pujante = request.user
    _subasta.precio_actual = _precio_nuevo
    _prod = _subasta.producto
    _prod.precio = _precio_nuevo
    _prod.save()
    _subasta.save()
    return HttpResponseRedirect('/subasta')


class DestroyerThread(threading.Thread):

    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        while True:
            mutex.acquire()
            now = datetime.datetime.now()
            subastas = SubastaEnCurso.objects.filter(hora_final__lte=now)
            for subasta in subastas:
                if subasta.pujante is not None:
                    SubastaFinalizada(producto=subasta.producto.nombre, tienda=subasta.tienda,
                                      comprador=subasta.pujante,
                                      hora_final=subasta.hora_final, precio_final=subasta.precio_actual).save()
                subasta.delete()
            mutex.release()
            sleep(60)


# a = DestroyerThread(1, "Thread-1", 1)
# a.start()
