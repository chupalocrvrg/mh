# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import Template
from django.template.context import RequestContext, Context
import os
from io import BytesIO
from xhtml2pdf import pisa
from settings import MEDIA_ROOT, MEDIA_URL
from django.template.loader import get_template


from app.form import CompraProductoForm, ProductoForm, InfoCompraProductoForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, ok_json, convertir_fecha, log, \
    proximafecha
from app.models import CompraProducto, IvaAplicado, Proveedor, Detallecompra, KardexInventario, Institucion, \
    null_to_numeric, CuotasCompras, PresupuestoCompra


@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def view(request):
    global ex
    data = informacionusuario(request)
    persona = request.session['persona']
    sucursal = request.session['sucursal']
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'addprod':
            try:
                form = CompraProductoForm(request.POST)
                c = CompraProducto.objects.get(id=int(request.POST['id']))
                if form.is_valid():
                    cantidad = form.cleaned_data['cantidad']
                    costo = form.cleaned_data['costo']
                    porcentaje = 0.12
                    subtotal = cantidad * costo
                    iva = subtotal * porcentaje
                    total = subtotal + iva
                    detalle = Detallecompra(articulo=form.cleaned_data['articulo'],
                                            cantidad=cantidad,
                                            subtotal=subtotal,
                                            costo=costo,
                                            iva=iva,
                                            valor=total)
                    detalle.save()
                    c.productos.add(detalle)
                    c.actualiza_valor()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'updateprov':
            try:
                c = CompraProducto.objects.get(id=int(request.POST['id']))
                prov = Proveedor.objects.get(id=int(request.POST['prov']))
                c.proveedor = prov
                c.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'updatefact':
            try:
                c = CompraProducto.objects.get(id=int(request.POST['id']))
                numero = request.POST['numero']
                c.numerodocumento = numero
                c.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'act_credito':
            try:
                c = CompraProducto.objects.get(id=int(request.POST['id']))
                valor = request.POST['valor'] == 'true'
                c.credito = valor
                c.save()
                if not c.credito:
                    c.meses = 0
                    c.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'act_meses':
            try:
                c = CompraProducto.objects.get(id=int(request.POST['id']))
                valor = int(request.POST['valor'])
                c.meses = valor
                c.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'confirmar':
            try:
                c = CompraProducto.objects.get(id=int(request.POST['id']))
                if not PresupuestoCompra.objects.filter(anio=datetime.now().date().year, activo=True).exists():
                    return bad_json(transaction, mensaje=u'No existe un presupuesto de compra definido')
                p = PresupuestoCompra.objects.filter(anio=datetime.now().date().year, activo=True)[0]
                if not c.proveedor:
                    return bad_json(transaction, mensaje=u'No ha seleccionado un proveedor')
                if not c.numerodocumento:
                    return bad_json(transaction, mensaje=u'No ha especificado el número de documento')
                c.finalizada = True
                c.fecha = datetime.now().date()
                c.presupuesto = p
                c.save()
                empresa = Institucion.objects.all()[0]
                utilidad = empresa.dato_institucion().margenutilidad / 100.0
                for d in c.productos.all():
                    p = d.articulo
                    inv = p.mi_inventario_sucursal(sucursal)
                    inv.cantidad += d.cantidad
                    inv.valor += d.valor
                    inv.costo = d.valor / d.cantidad
                    inv.precioventa = d.costo + (d.costo * 0.30)
                    inv.save()
                    venta = (d.costo * utilidad) + d.costo
                    movimiento = KardexInventario(inventario=inv,
                                                  fechaingreso=datetime.now(),
                                                  cantidad=d.cantidad,
                                                  costo=d.costo,
                                                  valor=d.valor,
                                                  precioventa=venta,
                                                  disponible=d.cantidad)
                    movimiento.save()
                if c.credito:
                    valor = c.valor
                    vc = null_to_numeric(valor / c.meses, 2)
                    fecha = datetime.now().date()
                    fechavence = fecha + timedelta(days=1)
                    for i in range(1, int(c.meses) + 1):
                        cuota  = CuotasCompras(compra=c,
                                               cuota=i,
                                               valor=vc,
                                               fechalimite=fechavence)
                        cuota.save()
                        fechavence = proximafecha(fechavence, 3).date()
                    valorc = null_to_numeric(c.cuotascompras_set.aggregate(valor=Sum('valor'))['valor'], 2)
                    ultima = c.cuotascompras_set.all().order_by('-cuota')[0]
                    faltante = 0
                    excddente = 0
                    if valor > valorc:
                        faltante = valor - valorc
                        ultima.valor += faltante
                        ultima.save()
                    elif valorc > valor:
                        excedente = valorc - valor
                        ultima.valor -= excedente
                        ultima.save()
                log(u'Confirmo compra: %s' % c, request, "edit")
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Nueva Compra'
                    i = IvaAplicado.objects.all()[0]
                    data['iva'] = i.nombre
                    porcentaje = i.porciento
                    if i.porciento > 1:
                        porcentaje = null_to_numeric(i.porciento / 100.0, 2)
                    data['p'] = porcentaje
                    if 'id' in request.GET:
                        c = CompraProducto.objects.get(id=int(request.GET['id']))
                    else:
                        c = CompraProducto(fecha=datetime.now().date(), sucursal=sucursal)
                        c.save()
                    data['c'] = c
                    data['det'] = c.productos.all()
                    data['proveedores'] = Proveedor.objects.all()
                    return render_to_response("compras/nueva.html", data)
                except Exception as ex:
                    pass

            if action == 'addprod':
                try:
                    data['title'] = u'Adicionar Producto'
                    data['iva'] = 12
                    data['compra'] = c = CompraProducto.objects.get(id=int(request.GET['id']))
                    porcentaje = 0.12
                    data['p'] = porcentaje
                    form = CompraProductoForm(initial={'porcentaje': 12})
                    data['form'] = form
                    return render_to_response("compras/addproducto.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'detalle':
                try:
                    data['title'] = u'Productos comprados'
                    data['c'] = c = CompraProducto.objects.get(id=int(request.GET['id']))
                    form = InfoCompraProductoForm(initial={'numero': c.numerodocumento})
                    data['form'] = form
                    data['permite_modificar'] = False
                    return render_to_response("compras/detalles.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'pdf':
                id = request.GET['id']
                compra = CompraProducto.objects.get(id=id)
                i = IvaAplicado.objects.all()[0]
                if CompraProducto.objects.filter(id=id):
                    # template = get_template('compras/report.html')
                    tpl = Template("{% include 'compras/report.html' %}")
                    data = {'e': Institucion.objects.all()[0], 'c': compra, 'details': compra.productos.all(), 'ivanombre': i.nombre}
                    html = tpl.render(Context(data))
                    # html = template.render(d)
                    result = BytesIO()
                    links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                    return HttpResponse(result.getvalue(), content_type='application/pdf')

            if action == 'confirmar':
                try:
                    data['title'] = u'Confirmar compra'
                    data['c'] = c = CompraProducto.objects.get(id=int(request.GET['id']))
                    return render_to_response("compras/confirmar.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Listado de compras realizadas'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    compras = CompraProducto.objects.filter(Q(proveedor__razonsocial__icontains=search) |
                                                            Q(numerodocumento__icontains=search), sucursal=sucursal).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    compras = CompraProducto.objects.filter(id=ids, sucursal=sucursal).distinct()
                else:
                    compras = CompraProducto.objects.filter(sucursal=sucursal)
                paging = MiPaginador(compras, 25)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session and 'paginador_url' in request.session:
                        if request.session['paginador_url'] == 'compras':
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
                request.session['paginador_url'] = 'compras'
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data['search'] = search if search else ""
                data['ids'] = ids if ids else ""
                data['compras'] = page.object_list
                CompraProducto.objects.filter(finalizada=False).delete()
                return render_to_response("compras/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')