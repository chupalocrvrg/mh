# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm, ProveedorForm, PresupuestoForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente, Proveedor, PresupuestoCompra
from django.template import RequestContext


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
                form = PresupuestoForm(request.POST)
                if form.is_valid():
                    if PresupuestoCompra.objects.filter(anio=datetime.now().date().year).exists():
                        return bad_json(transaction, mensaje=u'Ya existe un presupuesto para este periodo')
                    personaadmin = PresupuestoCompra(anio=datetime.now().date().year,
                                                     fechai=datetime.now().date(),
                                                     mes=datetime.now().month,
                                                     fechaf=datetime.now().date(),
                                                     valor=form.cleaned_data['valor'])
                    personaadmin.save(request)
                    log(u'Adiciono presupuesto: %s' % personaadmin, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'edit':
            try:
                form = PresupuestoForm(request.POST)
                if form.is_valid():
                    personaadmin = PresupuestoCompra.objects.get(id=int(request.POST['id']))
                    if form.cleaned_data['valor'] < personaadmin.total_compras():
                        return bad_json(transaction, mensaje=u'No se puede poner un presupuesto menor a las compras realizadas')
                    personaadmin.valor=form.cleaned_data['valor']
                    personaadmin.save()
                    log(u'Modifico presupuesto: %s' % personaadmin, request, "edit")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delete':
            try:
                administrativo = PresupuestoCompra.objects.get(id=int(request.POST['id']))
                administrativo.delete()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'cerrar':
            try:
                administrativo = PresupuestoCompra.objects.get(id=int(request.POST['id']))
                administrativo.activo = False
                administrativo.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Presupuesto'
                    form = PresupuestoForm()
                    data['form'] = form
                    return render_to_response("presupuestos/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['title'] = u'Editar Presupuesto'
                    data['administrativo'] = administrativo = PresupuestoCompra.objects.get(id=int(request.GET['id']))
                    form = PresupuestoForm(initial={'valor': administrativo.valor})
                    data['form'] = form
                    return render_to_response("presupuestos/edit.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delete':
                try:
                    data['title'] = u'Eliminar Presupuesto'
                    data['prov'] = PresupuestoCompra.objects.get(id=int(request.GET['id']))
                    return render_to_response("presupuestos/delete.html", data,  context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'cerrar':
                try:
                    data['title'] = u'Cerrar Presupuesto'
                    data['prov'] = PresupuestoCompra.objects.get(id=int(request.GET['id']))
                    return render_to_response("presupuestos/cerrar.html", data,  context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Presupuestos para compras'
                search = None
                ids = None
                administrativos = PresupuestoCompra.objects.all()
                data['administrativos'] = administrativos
                return render_to_response("presupuestos/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')