from datetime import datetime
from django.db import transaction

from app.funciones import ok_json, bad_json
from app.models import *


@transaction.commit_on_success
def view(request):
    sid = transaction.savepoint()
    if request.method == "POST":
        if 'action' in request.POST:
            action = request.POST['action']

            if action == 'checksession':
                try:
                    nuevasession = False
                    if datetime.now() >= request.session['timeout']:
                        nuevasession = True
                    return ok_json(transaction, data={'nuevasesion': nuevasession})
                except:
                    return ok_json(transaction, data={'nuevasesion': True})

            if action == 'cantones':
                try:
                    provincia = Provincia.objects.get(pk=request.POST['id'])
                    lista = []
                    for canton in provincia.canton_set.all():
                        lista.append([canton.id, canton.nombre])
                    return ok_json(transaction, data={'lista': lista})
                except Exception as ex:
                    return bad_json(transaction, error=3)

            if action == 'destino_traspaso':
                try:
                    origen = Sucursales.objects.get(pk=request.POST['id'])
                    lista = []
                    listap = []
                    for s in Sucursales.objects.all().exclude(id=origen.id):
                        lista.append([s.id, s.nombre])
                    for p in Producto.objects.filter(inventario__cantidad__gt=0, inventario__sucursal=origen).distinct():
                        listap.append([p.id, p.__unicode__()])
                    return ok_json(transaction, data={'lista': lista, 'listap': listap})
                except Exception as ex:
                    return bad_json(transaction, error=3)

            if action == 'parroquias':
                try:
                    canton = Canton.objects.filter(institucion=request.session['persona'].institucion).get(pk=request.POST['id'])
                    lista = []
                    for parroquia in canton.parroquia_set.all():
                        lista.append([parroquia.id, parroquia.nombre])
                    return ok_json(transaction, data={'lista': lista})
                except:
                    return bad_json(transaction, error=3)

            if action == 'data':
                try:
                    m = request.POST['model']
                    sp = m.split(':')
                    model = eval(sp[0])
                    persona = request.session['persona']
                    q = ''
                    if 'q' in request.POST:
                        q = request.POST['q'].upper().strip()
                    funcion = 'model.flexbox_query(q, persona.institucion.id'
                    if len(sp) > 1:
                        if len(sp[1]) > 0:
                            funcion += ', filtro=sp[1]'
                        if len(sp[2]) > 0:
                            funcion += ', exclude=sp[2]'
                        if len(sp[3]) > 0:
                            funcion += ', cantidad=sp[3]'
                    funcion += ')'
                    query = eval(funcion)
                    return ok_json(transaction, {"data": [{"id": x.id, "name": x.flexbox_repr(), 'alias': x.flexbox_alias() if hasattr(x, 'flexbox_alias') else []} for x in query]})
                except Exception as ex:
                    return bad_json(transaction, error=3)

    return bad_json(transaction, error=0)