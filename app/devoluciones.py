# -*- coding: utf-8 -*-
import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext, Context
from django.template.loader import get_template

from app.form import InfoCompraProductoForm, DevolucionForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, ok_json
from app.models import CompraProducto, Detallecompra, DetalleDevolucion, DevolucionCompraProducto


@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def view(request):
    global ex
    data = informacionusuario(request)
    persona = request.session['persona']
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'nueva':
            try:
                form = DevolucionForm(request.POST)
                if form.is_valid():
                    datos = json.loads(request.POST['lista_items1'])
                    if not datos:
                        return bad_json(transaction, mensaje=u'Debe especificar valores a devolver')
                    factura = form.cleaned_data['factura']
                    dev = DevolucionCompraProducto(compra=factura,
                                     usuario=request.user,
                                     motivo=form.cleaned_data['motivo'],
                                     fecha=datetime.now().date())
                    dev.save()
                    for dato in datos:
                        detalle = Detallecompra.objects.get(id=int(dato['id']))
                        if detalle.articulo.mi_inventario().cantidad < float(dato['valor']):
                            return bad_json(transaction, mensaje=u'No se puede completar la devolucion porque el inventario de este producto es menor')
                        detdev = DetalleDevolucion(devolucion=dev,
                                                   detalle=detalle,
                                                   cantidad=float(dato['valor']))
                        detdev.save()
                        detalle.cantidad -= float(dato['valor'])
                        detalle.valor = detalle.calcular_valor()
                        detalle.save()
                        p = detalle.articulo
                        inv = p.mi_inventario()
                        inv.cantidad -= float(dato['valor'])
                        inv.valor = inv.costo * inv.cantidad
                        inv.save()
                    factura.actualiza_valor()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'datosprod':
            try:
                c = CompraProducto.objects.get(id=int(request.POST['id']))
                detalles = c.productos.all()
                data['detalles'] = detalles
                template = get_template("devoluciones/segmento.html")
                json_content = template.render(Context(data))
                return ok_json(transaction, {'data': json_content})
            except Exception as ex:
                return bad_json(transaction, error=3)

        if action == 'confirmar':
            try:
                c = DevolucionCompraProducto.objects.get(id=int(request.POST['id']))
                for d in c.detalledevolucion_set.all():
                    det = d.detalle
                    det.cantidad += d.cantidad
                    det.valor = det.calcular_valor()
                    det.save()
                    p = det.articulo
                    inv = p.mi_inventario()
                    inv.cantidad += d.cantidad
                    inv.valor = inv.costo * inv.cantidad
                    inv.save()
                c.compra.actualiza_valor()
                c.delete()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Nueva Devolucion'
                    data['form'] = DevolucionForm()
                    return render_to_response("devoluciones/nueva.html", data)
                except Exception as ex:
                    pass

            if action == 'revertir':
                try:
                    data['title'] = u'Revertir devolucion'
                    data['c'] = c = DevolucionCompraProducto.objects.get(id=int(request.GET['id']))
                    return render_to_response("devoluciones/confirmar.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'detalle':
                try:
                    data['title'] = u'Detalle Devolucion'
                    data['c'] = c = DevolucionCompraProducto.objects.get(id=int(request.GET['id']))
                    data['detalles'] = c.detalledevolucion_set.all()
                    form = InfoCompraProductoForm(initial={'numero': c.compra.numerodocumento})
                    data['form'] = form
                    data['permite_modificar'] = False
                    return render_to_response("devoluciones/detalles.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Devoluciones realizadas'
                search = None
                ids = None
                if 'c' in request.GET:
                    request.session['c'] = c = int(request.GET['c'])
                elif 'c' in request.session:
                    c = int(request.session['c'])
                else:
                    request.session['c'] = c = 10
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    ventas = DevolucionCompraProducto.objects.filter(Q(compra__proveedor__razonsocial__icontains=search) |
                                                    Q(motivo__icontains=search) |
                                                    Q(compra__numero__icontains=search)).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    ventas = DevolucionCompraProducto.objects.filter(id=ids).distinct()
                else:
                    ventas = DevolucionCompraProducto.objects.all()
                paging = MiPaginador(ventas, c)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session and 'paginador_url' in request.session:
                        if request.session['paginador_url'] == 'ventas':
                            paginasesion = int(request.session['paginador'])
                    if 'page' in request.GET:
                        p = int(request.GET['page'])
                    else:
                        p = paginasesion
                    page = paging.page(p)
                except:
                    p = 1
                    page = paging.page(p)
                request.session['paginador'] = p
                request.session['paginador_url'] = 'ventas'
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data['search'] = search if search else ""
                data['ids'] = ids if ids else ""
                data['ventas'] = page.object_list
                data['c'] = c
                data['totales'] = DevolucionCompraProducto.objects.all().count()
                return render_to_response("devoluciones/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')