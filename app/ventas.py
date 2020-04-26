# -*- coding: utf-8 -*-
from datetime import datetime

import os
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Max, Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import Template
from django.template.context import RequestContext, Context
from django.template.loader import get_template
from io import BytesIO

from xhtml2pdf import pisa

from settings import MEDIA_ROOT, MEDIA_URL
from app.form import CompraProductoForm, ProductoForm, InfoCompraProductoForm, SalidaProductoForm, ClienteForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, ok_json, convertir_fecha, proximafecha, \
    log
from app.models import CompraProducto, IvaAplicado, Proveedor, Detallecompra, KardexInventario, Institucion, Factura, \
    Cliente, Producto, DetalleFactura, null_to_numeric, CuotasFacturas, TipoIdentificacion
from datetime import *

@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def view(request):
    global ex
    data = informacionusuario(request)
    persona = request.session['persona']
    sucursal = request.session['sucursal']

    if request.method == 'POST':
        action = request.POST['action']

        if action == 'deldetalle':
            try:
                c = DetalleFactura.objects.get(id=int(request.POST['valor']))
                compra = c.factura_set.all()[0]
                c.delete()
                compra.actualiza_valor()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'addprod':
            try:
                form = SalidaProductoForm(request.POST)
                c = Factura.objects.get(id=int(request.POST['id']))
                if form.is_valid():
                    cantidad = form.cleaned_data['cantidad']
                    costo = float(request.POST['micosto'])
                    articulo = form.cleaned_data['articulo']
                    if cantidad > articulo.mi_inventario_sucursal(sucursal).cantidad:
                        return bad_json(transaction, mensaje=u'No existe esa cantidad disponible para ese artículo')
                    desc = form.cleaned_data['descuento']
                    p = 0.12
                    subtotal = cantidad * costo
                    iva = subtotal * p
                    total = subtotal + iva - desc
                    detalle = DetalleFactura(producto=articulo,
                                            cantidad=cantidad,
                                            subtotal=subtotal,
                                             descuento=desc,
                                            precio=costo,
                                            iva=iva,
                                            valor=total)
                    detalle.save()
                    c.detalles.add(detalle)
                    c.actualiza_valor()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'updatecli':
            try:
                c = Factura.objects.get(id=int(request.POST['id']))
                cliente = Cliente.objects.get(id=int(request.POST['cli']))
                c.cliente = cliente
                c.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'datosprod':
            try:
                c = Producto.objects.get(id=int(request.POST['id']))
                disponible = '0'
                costo = '0'
                i = c.mi_inventario_sucursal(sucursal)
                total = c.stock_total()
                disponible = i.cantidad
                costo = i.precioventa
                otros = total - disponible
                return ok_json(transaction, data={'disponible': disponible, 'costo': costo, 'otros': otros})
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'confirmar':
            try:
                c = Factura.objects.get(id=int(request.POST['id']))
                if not c.cliente:
                    return bad_json(transaction, mensaje=u'No ha seleccionado un cliente')
                c.finalizada = True
                c.fecha = datetime.now().date()
                c.sucursal = sucursal
                c.save()
                for d in c.detalles.all():
                    p = d.producto
                    inv = p.mi_inventario_sucursal(sucursal)
                    movimiento = KardexInventario(ingreso=False,
                                                  fechaingreso=datetime.now(),
                                                  inventario=inv,
                                                  precioventa=d.precio,
                                                  cantidad=d.cantidad,
                                                  valor=d.valor)
                    movimiento.save()
                    inv.cantidad -= d.cantidad
                    inv.valor = inv.cantidad * inv.costo
                    inv.save()
                if c.credito:
                    valor = c.total
                    vc = null_to_numeric(valor / c.meses, 2)
                    fecha = datetime.now().date()
                    fechavence = fecha + timedelta(days=1)
                    for i in range(1, int(c.meses) + 1):
                        cuota = CuotasFacturas(factura=c,
                                              cuota=i,
                                              valor=vc,
                                              fechalimite=fechavence)
                        cuota.save()
                        fechavence = proximafecha(fechavence, 3).date()
                    valorc = null_to_numeric(c.cuotasfacturas_set.aggregate(valor=Sum('valor'))['valor'], 2)
                    ultima = c.cuotasfacturas_set.all().order_by('-cuota')[0]
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
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'act_credito':
            try:
                c = Factura.objects.get(id=int(request.POST['id']))
                valor = request.POST['valor'] == 'true'
                c.credito = valor
                c.save()
                if not c.credito:
                    c.meses = 0
                    c.recargo = 0
                    c.save()
                else:
                    if not c.porcentaje:
                        c.porcentaje = 10
                c.save()
                c.actualiza_valor()
                return ok_json()
            except Exception as ex:
                transaction.rollback()
                return bad_json(error=1)

        if action == 'act_meses':
            try:
                c = Factura.objects.get(id=int(request.POST['id']))
                valor = int(request.POST['valor'])
                c.meses = valor
                c.save()
                return ok_json()
            except Exception as ex:
                transaction.rollback()
                return bad_json(error=1)

        if action == 'act_recargo':
            try:
                c = Factura.objects.get(id=int(request.POST['id']))
                valor = int(request.POST['valor'])
                c.porcentaje = valor
                c.save()
                valor = null_to_numeric((c.subtotal * c.porcentaje) / 100, 2)
                c.recargo = valor
                c.save()
                c.actualiza_valor()
                return ok_json()
            except Exception as ex:
                transaction.rollback()
                return bad_json(error=1)

        if action == 'addcliente':
            try:
                form = ClienteForm(request.POST)
                if form.is_valid():
                    c = Factura.objects.get(id=int(request.POST['id']))
                    if Cliente.objects.filter(identificacion=form.cleaned_data['identificacion']).exists():
                        return bad_json(transaction, error=18)
                    personaadmin = Cliente(nombres=form.cleaned_data['nombres'],
                                           apellidos=form.cleaned_data['apellidos'],
                                           identificacion=form.cleaned_data['identificacion'],
                                           tipoidentificacion=form.cleaned_data['tipoidentificacion'],
                                           provincia=form.cleaned_data['provincia'],
                                           canton=form.cleaned_data['canton'],
                                           sector=form.cleaned_data['sector'],
                                           direccion=form.cleaned_data['direccion'],
                                           telefonomovil=form.cleaned_data['telefonomovil'],
                                           telefonofijo=form.cleaned_data['telefonofijo'],
                                           email=form.cleaned_data['email'])
                    personaadmin.save(request)
                    c.cliente = personaadmin
                    c.save()
                    log(u'Adiciono cliente: %s' % personaadmin, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Nueva Venta'
                    i = IvaAplicado.objects.all()[0]
                    data['iva'] = i.nombre
                    data['p'] = i.porciento
                    numero = null_to_numeric(Factura.objects.aggregate(valor=Max('numeroreal'))['valor'], 0)
                    if 'id' in request.GET:
                        c = Factura.objects.get(id=int(request.GET['id']))
                    else:
                        c = Factura(fecha=datetime.now().date(), numeroreal=int(numero)+1)
                        c.save()
                        c.actualiza_numero()
                    data['c'] = c
                    data['det'] = c.detalles.all()
                    data['clientes'] = Cliente.objects.all()
                    return render_to_response("ventas/nueva.html", data)
                except Exception as ex:
                    pass

            if action == 'addcliente':
                try:
                    data['title'] = u'Adicionar Cliente'
                    form = ClienteForm()
                    data['form'] = form
                    data['venta'] = Factura.objects.get(id=int(request.GET['id']))
                    data['tipo_cedula'] = TipoIdentificacion.objects.filter(cedula=True)[0].id
                    return render_to_response("ventas/addcliente.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'addprod':
                try:
                    data['title'] = u'Adicionar Producto'
                    data['iva'] = 12
                    data['venta'] = c = Factura.objects.get(id=int(request.GET['id']))
                    data['p'] = 0.12
                    form = SalidaProductoForm(initial={'porcentaje': 12})
                    form.editar(sucursal)
                    data['form'] = form
                    return render_to_response("ventas/addproducto.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'detalle':
                try:
                    data['title'] = u'Productos vendidos'
                    data['c'] = c = Factura.objects.get(id=int(request.GET['id']))
                    form = InfoCompraProductoForm(initial={'numero': c.numero})
                    data['form'] = form
                    data['permite_modificar'] = False
                    return render_to_response("ventas/detalles.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'pdf':
                id = request.GET['id']
                compra = Factura.objects.get(id=id)
                i = IvaAplicado.objects.all()[0]
                if Factura.objects.filter(id=id):
                    # template = get_template('compras/report.html')
                    tpl = Template("{% include 'ventas/report.html' %}")
                    data = {'e': Institucion.objects.all()[0], 'c': compra, 'details': compra.detalles.all(), 'ivanombre': i.nombre}
                    html = tpl.render(Context(data))
                    # html = template.render(d)
                    result = BytesIO()
                    links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                    return HttpResponse(result.getvalue(), content_type='application/pdf')

            if action == 'confirmar':
                try:
                    data['title'] = u'Confirmar venta'
                    data['c'] = c = Factura.objects.get(id=int(request.GET['id']))
                    return render_to_response("ventas/confirmar.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Factura emitidas'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    ventas = Factura.objects.filter(Q(cliente__nombres__icontains=search) |
                                                    Q(cliente__apellidos__icontains=search) |
                                                    Q(cliente__identificacion__icontains=search) |
                                                    Q(numeroreal__icontains=search) |
                                                    Q(numero__icontains=search), sucursal=sucursal).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    ventas = Factura.objects.filter(id=ids, sucursal=sucursal).distinct()
                else:
                    ventas = Factura.objects.all()
                paging = MiPaginador(ventas, 25)
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
                Factura.objects.filter(finalizada=False).delete()
                return render_to_response("ventas/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/ventas')