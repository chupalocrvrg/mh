# -*- coding: utf-8 -*-
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, TipoAdministrativoForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Modulo, GrupoModulos, Sucursales, \
    EmpleadoSucursal
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
                form = AdministrativoForm(request.POST)
                if form.is_valid():
                    if Persona.objects.filter(identificacion=form.cleaned_data['identificacion']).exists():
                        return bad_json(transaction, error=18)
                    personaadmin = Persona(nombre1=form.cleaned_data['nombre1'],
                                           nombre2=form.cleaned_data['nombre2'],
                                           apellido1=form.cleaned_data['apellido1'],
                                           apellido2=form.cleaned_data['apellido2'],
                                           identificacion=form.cleaned_data['identificacion'],
                                           tipoidentificacion=form.cleaned_data['tipoidentificacion'],
                                           nacimiento=form.cleaned_data['nacimiento'],
                                           provincia=form.cleaned_data['provincia'],
                                           canton=form.cleaned_data['canton'],
                                           sector=form.cleaned_data['sector'],
                                           direccion=form.cleaned_data['direccion'],
                                           numero=form.cleaned_data['numero'],
                                           referencia=form.cleaned_data['referencia'],
                                           telefonomovil=form.cleaned_data['telefonomovil'],
                                           telefonofijo=form.cleaned_data['telefonofijo'],
                                           email=form.cleaned_data['email'])
                    personaadmin.save(request)
                    administrativo = Empleado(persona=personaadmin,
                                                    email=form.cleaned_data['email'],
                                              sueldo=form.cleaned_data['sueldo'])
                    administrativo.save(request)
                    tipousuario = PerfilUsuario(tipoperfilusuario=form.cleaned_data['tipoempleado'],
                                                empleado=administrativo)
                    tipousuario.save()
                    usuario = generar_usuario(form.cleaned_data['identificacion'], form.cleaned_data['identificacion'])
                    personaadmin.usuario = usuario
                    personaadmin.save()
                    log(u'Adiciono personal administrativo: %s' % administrativo, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'edit':
            try:
                form = TipoAdministrativoForm(request.POST)
                if form.is_valid():
                    administrativo = Empleado.objects.get(id=int(request.POST['id']))
                    perfil = administrativo.mi_perfil()
                    perfil.tipoperfilusuario = form.cleaned_data['tipoempleado']
                    perfil.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'des':
            try:
                administrativo = Empleado.objects.get(id=int(request.POST['id']))
                perfil = administrativo.mi_perfil()
                perfil.activo = False
                perfil.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'act':
            try:
                administrativo = Empleado.objects.get(id=int(request.POST['id']))
                perfil = administrativo.mi_perfil()
                perfil.activo = True
                perfil.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'addmodulogrupo':
            try:
                grupo = PerfilUsuario.objects.get(pk=int(request.POST['id']))
                datos = json.loads(request.POST['lista'])
                for dato in datos:
                    modulo = Modulo.objects.get(pk=int(dato['id']))
                    if not GrupoModulos.objects.filter(perfil=grupo, modulo=modulo).exists():
                        grupom = GrupoModulos(perfil=grupo,
                                              modulo=modulo)
                        grupom.save(request)
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delmodulogrupo':
            try:
                grupo = PerfilUsuario.objects.get(pk=int(request.POST['id']))
                datos = json.loads(request.POST['lista'])
                for dato in datos:
                    modulo = Modulo.objects.get(pk=int(dato['id']))
                    if GrupoModulos.objects.filter(perfil=grupo, modulo=modulo).exists():
                        gm = GrupoModulos.objects.filter(perfil=grupo, modulo=modulo)[0]
                        gm.delete()
                log(u'Eliminó módulos al grupo: %s' % grupo, request, "add")
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'addsucursal':
            try:
                grupo = Empleado.objects.get(pk=int(request.POST['id']))
                datos = json.loads(request.POST['lista'])
                for dato in datos:
                    modulo = Sucursales.objects.get(pk=int(dato['id']))
                    if not EmpleadoSucursal.objects.filter(empleado=grupo, sucursal=modulo).exists():
                        grupom = EmpleadoSucursal(empleado=grupo, sucursal=modulo)
                        grupom.save(request)
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delsucursal':
            try:
                grupo = Empleado.objects.get(pk=int(request.POST['id']))
                datos = json.loads(request.POST['lista'])
                for dato in datos:
                    modulo = Sucursales.objects.get(pk=int(dato['id']))
                    if EmpleadoSucursal.objects.filter(empleado=grupo, sucursal=modulo).exists():
                        gm = EmpleadoSucursal.objects.filter(empleado=grupo, sucursal=modulo)[0]
                        gm.delete()
                log(u'Eliminó sucursal al empleado: %s' % grupo, request, "add")
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Administrativo'
                    form = AdministrativoForm()
                    data['form'] = form
                    data['tipo_cedula'] = TipoIdentificacion.objects.filter(cedula=True)[0].id
                    return render_to_response("adm_administrativos/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['title'] = u'Editar Tipo'
                    data['administrativo'] = administrativo = Empleado.objects.get(id=int(request.GET['id']))
                    form = TipoAdministrativoForm(initial={'tipoempleado': administrativo.mi_perfil().tipoperfilusuario})
                    data['form'] = form
                    return render_to_response("usuarios/edit.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'info':
                try:
                    data['title'] = u'Información del usuario'
                    data['empleado'] = empleado = Empleado.objects.get(pk=request.GET['id'])
                    data['usuario'] = empleado.persona.usuario
                    return render_to_response("usuarios/info.html", data)
                except Exception as ex:
                    pass

            if action == 'permisos':
                try:
                    data['title'] = u'Permisos'
                    data['empleado'] = empleado = Empleado.objects.get(pk=int(request.GET['id']))
                    data['grupo'] = perfil = empleado.mi_perfil()
                    data['modulos_grupo'] = modulos = Modulo.objects.filter(grupomodulos__perfil=perfil).distinct()
                    data['modulos'] = Modulo.objects.all().exclude(grupomodulos__perfil=perfil)
                    return render_to_response("usuarios/permisosgrupo.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'sucursales':
                try:
                    data['title'] = u'Sucursales a las que el usuario tiene acceso'
                    data['empleado'] = empleado = Empleado.objects.get(pk=int(request.GET['id']))
                    data['modulos_grupo'] = modulos = Sucursales.objects.filter(empleadosucursal__empleado=empleado).distinct()
                    data['modulos'] = Sucursales.objects.all().exclude(empleadosucursal__empleado=empleado)
                    return render_to_response("usuarios/sucursales.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'des':
                try:
                    data['title'] = u'Desactivar acceso de usuario'
                    data['c'] = c = Empleado.objects.get(id=int(request.GET['id']))
                    return render_to_response("usuarios/des.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'act':
                try:
                    data['title'] = u'Activar acceso de usuario'
                    data['c'] = c = Empleado.objects.get(id=int(request.GET['id']))
                    return render_to_response("usuarios/act.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Usuarios del sistema'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    ss = search.split(' ')
                    if len(ss) == 1:
                        administrativos = Empleado.objects.filter(Q(persona__nombre1__icontains=search) |
                                                                  Q(persona__nombre2__icontains=search) |
                                                                  Q(persona__apellido1__icontains=search) |
                                                                  Q(persona__apellido2__icontains=search) |
                                                                  Q(persona__identificacion__icontains=search) |
                                                                  Q(perfilusuario__tipoperfilusuario__nombre__icontains=search), persona__usuario__isnull=False).distinct()
                    else:
                        administrativos = Empleado.objects.filter(Q(persona__apellido1__icontains=ss[0]) &
                                                                  Q(persona__apellido2__icontains=ss[1]), persona__usuario__isnull=False).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    administrativos = Empleado.objects.filter(id=ids, persona__usuario__isnull=False).distinct()
                else:
                    administrativos = Empleado.objects.filter(persona__usuario__isnull=False)
                paging = MiPaginador(administrativos, 25)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session and 'paginador_url' in request.session:
                        if request.session['paginador_url'] == 'adm_administrativos':
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
                request.session['paginador_url'] = 'adm_administrativos'
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data['search'] = search if search else ""
                data['ids'] = ids if ids else ""
                data['administrativos'] = page.object_list
                return render_to_response("usuarios/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')