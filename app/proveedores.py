# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm, ProveedorForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente, Proveedor
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
                form = ProveedorForm(request.POST)
                if form.is_valid():
                    if Proveedor.objects.filter(identificacion=form.cleaned_data['identificacion']).exists():
                        return bad_json(transaction, error=18)
                    personaadmin = Proveedor(razonsocial=form.cleaned_data['razonsocial'],
                                           representante=form.cleaned_data['representante'],
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
                form = ProveedorForm(request.POST)
                if form.is_valid():
                    personaadmin = Proveedor.objects.get(id=int(request.POST['id']))
                    personaadmin.razonsocial = form.cleaned_data['razonsocial']
                    personaadmin.representante=form.cleaned_data['representante']
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
                administrativo = Proveedor.objects.get(id=int(request.POST['id']))
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
                    data['title'] = u'Adicionar Proveedor'
                    form = ProveedorForm()
                    data['form'] = form
                    data['tipo_cedula'] = TipoIdentificacion.objects.filter(cedula=True)[0].id
                    return render_to_response("proveedores/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['title'] = u'Editar Proveedor'
                    data['administrativo'] = administrativo = Proveedor.objects.get(id=int(request.GET['id']))
                    form = ProveedorForm(initial={'razonsocial': administrativo.razonsocial,
                                                       'representante': administrativo.representante,
                                                       'tipoidentificacion': administrativo.tipoidentificacion,
                                                       'identificacion': administrativo.identificacion,
                                                       'provincia': administrativo.provincia,
                                                       'canton': administrativo.canton,
                                                       'sector': administrativo.sector,
                                                       'direccion': administrativo.direccion,
                                                       'telefonomovil': administrativo.telefonomovil,
                                                       'telefonofijo': administrativo.telefonofijo,
                                                       'email': administrativo.email})
                    data['form'] = form
                    data['tipo_cedula'] = TipoIdentificacion.objects.filter(cedula=True)[0].id
                    return render_to_response("proveedores/edit.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delete':
                try:
                    data['title'] = u'Eliminar Proveedor'
                    data['prov'] = Proveedor.objects.get(id=int(request.GET['id']))
                    return render_to_response("proveedores/delete.html", data,  context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Listado de Proveedores'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    administrativos = Proveedor.objects.filter(Q(razonsocial__icontains=search) |
                                                              Q(representante__icontains=search) |
                                                              Q(identificacion__icontains=search)).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    administrativos = Proveedor.objects.filter(id=ids).distinct()
                else:
                    administrativos = Proveedor.objects.all()
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
                return render_to_response("proveedores/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')