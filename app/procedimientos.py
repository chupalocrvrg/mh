# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm, ProveedorForm, ManualForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente, Proveedor, ManualProcedimientos
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
                form = ManualForm(request.POST, request.FILES)
                if form.is_valid():
                    nfile = None
                    if 'archivo' in request.FILES:
                        nfile = request.FILES['archivo']
                    noticia = ManualProcedimientos(detalles=form.cleaned_data['detalles'],
                                                   fecha=datetime.now().date(),
                                                   nombre=form.cleaned_data['nombre'],
                                                   archivo=nfile)
                    noticia.save()
                    log(u'Adiciono noticia: %s' % noticia, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delete':
            try:
                administrativo = ManualProcedimientos.objects.get(id=int(request.POST['id']))
                administrativo.delete()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Manual'
                    form = ManualForm()
                    data['form'] = form
                    return render_to_response("procedimientos/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delete':
                try:
                    data['title'] = u'Eliminar Manual'
                    data['prov'] = ManualProcedimientos.objects.get(id=int(request.GET['id']))
                    return render_to_response("procedimientos/delete.html", data,  context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Manuales de procedimientos'
                data['manuales'] = ManualProcedimientos.objects.all()
                return render_to_response("procedimientos/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')