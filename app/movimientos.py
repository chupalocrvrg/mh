# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm, ProveedorForm, ManualForm, TraspasoForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente, Proveedor, ManualProcedimientos, \
    Traspasos
from django.template import RequestContext
from datetime import *

@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def view(request):
    global ex
    data = informacionusuario(request)
    persona = request.session['persona']
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'add':
            try:
                form = TraspasoForm(request.POST, request.FILES)
                if form.is_valid():
                    p = form.cleaned_data['producto']
                    inv = p.mi_inventario_sucursal(form.cleaned_data['origen'])
                    if form.cleaned_data['cantidad'] > inv.cantidad:
                        return bad_json(transaction, mensaje=u'La cantidad a traspasar no puede ser mayor al stock %s' % inv.cantidad )
                    noticia = Traspasos(origen=form.cleaned_data['origen'],
                                        fecha=datetime.now().date(),
                                        destino=form.cleaned_data['destino'],
                                        producto=form.cleaned_data['producto'],
                                        motivo=form.cleaned_data['motivo'],
                                        cantidad=form.cleaned_data['cantidad'])
                    noticia.save()
                    inv.cantidad -= form.cleaned_data['cantidad']
                    inv.save()
                    inv2 = p.mi_inventario_sucursal(form.cleaned_data['destino'])
                    inv2.cantidad += form.cleaned_data['cantidad']
                    inv2.save()
                    log(u'Adiciono traspaso: %s' % noticia, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delete':
            try:
                t = Traspasos.objects.get(id=int(request.POST['id']))
                p = t.producto
                inv = p.mi_inventario_sucursal(t.destino)
                if t.cantidad > inv.cantidad:
                    return bad_json(transaction,  mensaje=u'No se puede revertir, las unidades se vendieron - stock actual:  %s' % inv.cantidad)
                inv.cantidad -= t.cantidad
                inv.save()
                inv2 = p.mi_inventario_sucursal(t.origen)
                inv2.cantidad += t.cantidad
                inv2.save()
                t.delete()
                log(u'Elimino traspaso: %s' % t, request, "del")
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Traspaso'
                    form = TraspasoForm()
                    data['form'] = form
                    return render_to_response("traspasos/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delete':
                try:
                    data['title'] = u'Revertir traspaso'
                    data['prov'] = Traspasos.objects.get(id=int(request.GET['id']))
                    return render_to_response("traspasos/delete.html", data,  context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Movimientos entre sucursales'
                data['manuales'] = Traspasos.objects.all()
                return render_to_response("traspasos/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')