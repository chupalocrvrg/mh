# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm, SucursalForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente, Sucursales
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
                form = SucursalForm(request.POST)
                if form.is_valid():
                    personaadmin = Sucursales(nombre=form.cleaned_data['nombre'],
                                           provincia=form.cleaned_data['provincia'],
                                           canton=form.cleaned_data['canton'],
                                           direccion=form.cleaned_data['direccion'])
                    personaadmin.save(request)
                    log(u'Adiciono sucursal: %s' % personaadmin, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'edit':
            try:
                form = SucursalForm(request.POST)
                if form.is_valid():
                    personaadmin = Sucursales.objects.get(id=int(request.POST['id']))
                    personaadmin.nombre = form.cleaned_data['nombre']
                    personaadmin.provincia=form.cleaned_data['provincia']
                    personaadmin.canton=form.cleaned_data['canton']
                    personaadmin.direccion=form.cleaned_data['direccion']
                    personaadmin.save()
                    log(u'Modifico sucursal: %s' % personaadmin, request, "edit")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delete':
            try:
                personaadmin = Sucursales.objects.get(id=int(request.POST['id']))
                log(u'Elimino sucursal: %s' % personaadmin, request, "edit")
                personaadmin.delete()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Sucursal'
                    form = SucursalForm()
                    data['form'] = form
                    return render_to_response("sucursales/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['title'] = u'Editar Sucursal'
                    data['administrativo'] = cliente = Sucursales.objects.get(id=int(request.GET['id']))
                    form = SucursalForm(initial={'nombre': cliente.nombre,
                                               'provincia': cliente.provincia,
                                               'canton': cliente.canton,
                                               'direccion': cliente.direccion})
                    data['form'] = form
                    return render_to_response("sucursales/edit.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delete':
                try:
                    data['title'] = u'Eliminar Sucursal'
                    data['cliente'] = cliente = Sucursales.objects.get(id=int(request.GET['id']))
                    return render_to_response("sucursales/delete.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Listado de Sucursales'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    administrativos = Sucursales.objects.filter(Q(nombre__icontains=search) |
                                                              Q(provincia__nombre__icontains=search) |
                                                              Q(canton__nombre__icontains=search)).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    administrativos = Sucursales.objects.filter(id=ids).distinct()
                else:
                    administrativos = Sucursales.objects.all()
                paging = MiPaginador(administrativos, 25)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session and 'paginador_url' in request.session:
                        if request.session['paginador_url'] == 'clientes':
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
                request.session['paginador_url'] = 'clientes'
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data['search'] = search if search else ""
                data['ids'] = ids if ids else ""
                data['administrativos'] = page.object_list
                return render_to_response("sucursales/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')