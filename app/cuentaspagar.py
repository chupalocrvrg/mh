# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import os
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import Template
from django.template.context import RequestContext, Context
from django.template.loader import get_template
from io import BytesIO

from xhtml2pdf import pisa

from settings import MEDIA_ROOT, MEDIA_URL
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

        if action == 'pagar':
            try:
                c = CuotasCompras.objects.get(id=int(request.POST['id']))
                c.pagada = True
                c.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'cuotas':
                try:
                    data['title'] = u'Cuotas'
                    data['c'] = c = CompraProducto.objects.get(id=int(request.GET['id']))
                    data['detalles'] = c.cuotascompras_set.all()
                    return render_to_response("cuentaspagar/detalles.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'pagar':
                try:
                    data['title'] = u'Pagar'
                    data['c'] = c = CuotasCompras.objects.get(id=int(request.GET['id']))
                    return render_to_response("cuentaspagar/confirmar.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Listado de cuentas por pagar'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    compras = CompraProducto.objects.filter(Q(proveedor__razonsocial__icontains=search) |
                                                            Q(numerodocumento__icontains=search), sucursal=sucursal, credito=True).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    compras = CompraProducto.objects.filter(id=ids, sucursal=sucursal, credito=True).distinct()
                else:
                    compras = CompraProducto.objects.filter(sucursal=sucursal, credito=True)
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
                return render_to_response("cuentaspagar/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')