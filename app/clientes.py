# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente
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
                form = ClienteForm(request.POST)
                if form.is_valid():
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
                    log(u'Adiciono cliente: %s' % personaadmin, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'edit':
            try:
                form = ClienteForm(request.POST)
                if form.is_valid():
                    personaadmin = Cliente.objects.get(id=int(request.POST['id']))
                    personaadmin.nombres = form.cleaned_data['nombres']
                    personaadmin.apellidos = form.cleaned_data['apellidos']
                    personaadmin.provincia=form.cleaned_data['provincia']
                    personaadmin.canton=form.cleaned_data['canton']
                    personaadmin.sector=form.cleaned_data['sector']
                    personaadmin.direccion=form.cleaned_data['direccion']
                    personaadmin.telefonomovil=form.cleaned_data['telefonomovil']
                    personaadmin.telefonofijo=form.cleaned_data['telefonofijo']
                    personaadmin.email=form.cleaned_data['email']
                    personaadmin.save()
                    log(u'Modifico personal administrativo: %s' % personaadmin, request, "edit")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delete':
            try:
                personaadmin = Cliente.objects.get(id=int(request.POST['id']))
                log(u'Elimino personal administrativo: %s' % personaadmin, request, "edit")
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
                    data['title'] = u'Adicionar Cliente'
                    form = ClienteForm()
                    data['form'] = form
                    data['tipo_cedula'] = TipoIdentificacion.objects.filter(cedula=True)[0].id
                    return render_to_response("clientes/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['title'] = u'Editar Cliente'
                    data['administrativo'] = cliente = Cliente.objects.get(id=int(request.GET['id']))
                    form = ClienteForm(initial={'nombres': cliente.nombres,
                                               'apellidos': cliente.apellidos,
                                               'tipoidentificacion': cliente.tipoidentificacion,
                                               'identificacion': cliente.identificacion,
                                               'provincia': cliente.provincia,
                                               'canton': cliente.canton,
                                               'sector': cliente.sector,
                                               'direccion': cliente.direccion,
                                               'telefonomovil': cliente.telefonomovil,
                                               'telefonofijo': cliente.telefonofijo,
                                               'email': cliente.email})
                    data['form'] = form
                    data['tipo_cedula'] = TipoIdentificacion.objects.filter(cedula=True)[0].id
                    return render_to_response("clientes/edit.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delete':
                try:
                    data['title'] = u'Eliminar Cliente'
                    data['cliente'] = cliente = Cliente.objects.get(id=int(request.GET['id']))
                    return render_to_response("clientes/delete.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Listado de Clientes'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    administrativos = Cliente.objects.filter(Q(nombres__icontains=search) |
                                                              Q(apellidos__icontains=search) |
                                                              Q(identificacion__icontains=search)).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    administrativos = Cliente.objects.filter(id=ids).distinct()
                else:
                    administrativos = Cliente.objects.all()
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
                return render_to_response("clientes/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')