# -*- coding: utf-8 -*-
import json
import os
from io import BytesIO

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, Template
from django.template.context import Context
from xhtml2pdf import pisa

from settings import MEDIA_ROOT, MEDIA_URL
from app.form import ClienteForm
from app.funciones import informacionusuario, url_back, bad_json, ok_json, log, convertir_fecha, \
    convertir_fecha_invertida
from app.models import TipoIdentificacion, Cliente, Institucion, Proveedor, Producto, CompraProducto, Factura, Gastos


@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def view(request):
    global ex
    data = informacionusuario(request)
    persona = request.session['persona']
    if request.method == 'POST':
        action = request.POST['action']


        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'clientes':
                clientes = Cliente.objects.all()
                tpl = Template("{% include 'reportes/clientes.html' %}")
                data = {'e': Institucion.objects.all()[0], 'clientes': clientes}
                html = tpl.render(Context(data))
                result = BytesIO()
                links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                return HttpResponse(result.getvalue(), content_type='application/pdf')

            if action == 'proveedores':
                proveedores = Proveedor.objects.all()
                tpl = Template("{% include 'reportes/proveedores.html' %}")
                data = {'e': Institucion.objects.all()[0], 'proveedores': proveedores}
                html = tpl.render(Context(data))
                result = BytesIO()
                links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                return HttpResponse(result.getvalue(), content_type='application/pdf')

            if action == 'inventario':
                try:
                    productos = Producto.objects.all()
                    tpl = Template("{% include 'reportes/productos.html' %}")
                    data = {'e': Institucion.objects.all()[0], 'productos': productos}
                    html = tpl.render(Context(data))
                    result = BytesIO()
                    links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                    return HttpResponse(result.getvalue(), content_type='application/pdf')
                except Exception as ex:
                    pass

            if action == 'compras':
                try:
                    fechai = convertir_fecha_invertida(request.GET['fi'])
                    fechaf = convertir_fecha_invertida(request.GET['ff'])
                    compras = CompraProducto.objects.filter(fecha__gte=fechai, fecha__lte=fechaf, finalizada=True).distinct()
                    tpl = Template("{% include 'reportes/compras.html' %}")
                    data = {'e': Institucion.objects.all()[0], 'compras': compras, 'fi': fechai, 'ff': fechaf}
                    html = tpl.render(Context(data))
                    result = BytesIO()
                    links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                    return HttpResponse(result.getvalue(), content_type='application/pdf')
                except Exception as ex:
                    pass

            if action == 'ventas':
                try:
                    fechai = convertir_fecha_invertida(request.GET['fi'])
                    fechaf = convertir_fecha_invertida(request.GET['ff'])
                    ventas = Factura.objects.filter(fecha__gte=fechai, fecha__lte=fechaf, finalizada=True).distinct()
                    tpl = Template("{% include 'reportes/ventas.html' %}")
                    data = {'e': Institucion.objects.all()[0], 'ventas': ventas, 'fi': fechai, 'ff': fechaf}
                    html = tpl.render(Context(data))
                    result = BytesIO()
                    links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                    return HttpResponse(result.getvalue(), content_type='application/pdf')
                except Exception as ex:
                    pass

            if action == 'gastos':
                try:
                    fechai = convertir_fecha_invertida(request.GET['fi'])
                    fechaf = convertir_fecha_invertida(request.GET['ff'])
                    gastos = Gastos.objects.filter(fecha__gte=fechai, fecha__lte=fechaf).distinct()
                    tpl = Template("{% include 'reportes/gastos.html' %}")
                    data = {'e': Institucion.objects.all()[0], 'gastos': gastos, 'fi': fechai, 'ff': fechaf}
                    html = tpl.render(Context(data))
                    result = BytesIO()
                    links = lambda uri, rel: os.path.join(MEDIA_ROOT, uri.replace(MEDIA_URL, ''))
                    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='UTF-8', link_callback=links)
                    return HttpResponse(result.getvalue(), content_type='application/pdf')
                except Exception as ex:
                    pass


            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Configuración de parámetros'
                data['empresa'] = Institucion.objects.all()[0]
                data['hoy'] = datetime.now().date()
                return render_to_response("reportes/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')