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

from app.form import InfoCompraProductoForm, DevolucionForm, DevolucionFacturaForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, ok_json
from app.models import CompraProducto, Detallecompra, DetalleDevolucion, DevolucionCompraProducto, DevolucionFactura, \
    Factura, DetalleFactura, DetalleDevolucionFactura, IvaAplicado


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
                form = DevolucionFacturaForm(request.POST)
                if form.is_valid():
                    datos = json.loads(request.POST['lista_items1'])
                    if not datos:
                        return bad_json(transaction, mensaje=u'Debe especificar valores a devolver')
                    factura = form.cleaned_data['factura']
                    dev = DevolucionFactura(factura=factura,
                                     usuario=request.user,
                                     motivo=form.cleaned_data['motivo'],
                                     fecha=datetime.now().date())
                    dev.save()
                    for dato in datos:
                        detalle = DetalleFactura.objects.get(id=int(dato['id']))
                        detdev = DetalleDevolucionFactura(devolucion=dev,
                                                   detalle=detalle,
                                                   cantidad=float(dato['valor']))
                        detdev.save()
                        detalle.cantidad -= float(dato['valor'])
                        i = IvaAplicado.objects.all()[0]
                        p = i.porciento / 100
                        subtotal = detalle.calcular_valor()
                        iva = subtotal * p
                        total = subtotal + iva
                        detalle.subtotal = subtotal
                        detalle.iva = iva
                        detalle.valor = total
                        detalle.save()
                        p = detalle.producto
                        inv = p.mi_inventario()
                        inv.cantidad += float(dato['valor'])
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
                c = Factura.objects.get(id=int(request.POST['id']))
                detalles = c.detalles.all()
                data['detalles'] = detalles
                template = get_template("devolucionesf/segmento.html")
                json_content = template.render(Context(data))
                return ok_json(transaction, {'data': json_content})
            except Exception as ex:
                return bad_json(transaction, error=3)

        if action == 'confirmar':
            try:
                c = DevolucionFactura.objects.get(id=int(request.POST['id']))
                for d in c.detalledevolucionfactura_set.all():
                    det = d.detalle
                    det.cantidad += d.cantidad
                    det.valor = det.calcular_valor()
                    det.save()
                    p = det.producto
                    inv = p.mi_inventario()
                    inv.cantidad -= d.cantidad
                    inv.valor = inv.costo * inv.cantidad
                    inv.save()
                c.factura.actualiza_valor()
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
                    data['form'] = DevolucionFacturaForm()
                    return render_to_response("devolucionesf/nueva.html", data)
                except Exception as ex:
                    pass

            if action == 'revertir':
                try:
                    data['title'] = u'Revertir devolucion'
                    data['c'] = c = DevolucionFactura.objects.get(id=int(request.GET['id']))
                    return render_to_response("devolucionesf/confirmar.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'detalle':
                try:
                    data['title'] = u'Detalle Devolucion'
                    data['c'] = c = DevolucionFactura.objects.get(id=int(request.GET['id']))
                    data['detalles'] = c.detalledevolucionfactura_set.all()
                    form = InfoCompraProductoForm(initial={'numero': c.factura.numero})
                    data['form'] = form
                    data['permite_modificar'] = False
                    return render_to_response("devolucionesf/detalles.html", data, context_instance=RequestContext(request))
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
                    ventas = DevolucionFactura.objects.filter(Q(factura__cliente__apellidos__icontains=search) |
                                                              Q(factura__cliente__nombres__icontains=search) |
                                                    Q(motivo__icontains=search) |
                                                    Q(factura__numero__icontains=search)).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    ventas = DevolucionFactura.objects.filter(id=ids).distinct()
                else:
                    ventas = DevolucionFactura.objects.all()
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
                data['totales'] = DevolucionFactura.objects.all().count()
                return render_to_response("devolucionesf/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')