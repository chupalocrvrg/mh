# -*- coding: utf-8 -*-
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, GrupoUsuarioForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import Administrativo, TipoIdentificacion, Persona, \
    PerfilGrupoInstitucion, GrupoInstitucion, Modulo, GrupoModulos
from django.template import RequestContext


@csrf_protect
@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def view(request):
    global ex
    data = informacionusuario(request)
    persona = request.session['persona']
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'addmodulogrupo':
            try:
                grupo = GrupoInstitucion.objects.get(pk=int(request.POST['id']))
                datos = json.loads(request.POST['lista'])
                for dato in datos:
                    modulo = Modulo.objects.get(pk=int(dato['id']))
                    if not GrupoModulos.objects.filter(grupoinstitucion=grupo, modulo=modulo).exists():
                        grupom = GrupoModulos(grupoinstitucion=grupo,
                                              modulo=modulo,
                                              modificable=True)
                        grupom.save(request)
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delmodulogrupo':
            try:
                grupo = GrupoInstitucion.objects.get(pk=int(request.POST['id']))
                datos = json.loads(request.POST['lista'])
                for dato in datos:
                    modulo = Modulo.objects.get(pk=int(dato['id']))
                    if GrupoModulos.objects.filter(grupoinstitucion=grupo, modulo=modulo).exists():
                        gm = GrupoModulos.objects.filter(grupoinstitucion=grupo, modulo=modulo)[0]
                        gm.delete()
                log(u'Eliminó módulos al grupo: %s' % grupo, request, "add")
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'permisosgrupo':
                try:
                    data['title'] = u'Permisos'
                    data['grupo'] = grupo = GrupoInstitucion.objects.get(pk=int(request.GET['id']))
                    # data['pg'] = pg = grupo.mi_permisogrupo()
                    # data['permisos_grupo'] = grupo.mi_permisogrupo().permiso.all()
                    # data['permisos'] = Permiso.objects.all().exclude(id__in=[x.id for x in pg.permiso.all()])
                    data['modulos_grupo'] = modulos = Modulo.objects.filter(grupomodulos__grupoinstitucion=grupo).distinct()
                    if grupo.administrativo:
                        data['modulos'] = Modulo.objects.filter(administrativo=True).exclude(id__in=modulos.values_list('id', flat=True)).order_by('id')
                    elif grupo.empleado:
                        data['modulos'] = Modulo.objects.filter(empleado=True).exclude(id__in=modulos.values_list('id', flat=True)).order_by('id')
                    return render_to_response("grupos_permisos/permisosgrupo.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass



            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Tipos de Usuarios del sistema'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    grupos = GrupoInstitucion.objects.filter(Q(grupo__name__icontains=search) |
                                                             Q(nombre__icontains=search)).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    grupos = GrupoInstitucion.objects.filter(id=ids).distinct()
                else:
                    grupos = GrupoInstitucion.objects.all()
                paging = MiPaginador(grupos, 25)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session and 'paginador_url' in request.session:
                        if request.session['paginador_url'] == 'grupos_permisos':
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
                request.session['paginador_url'] = 'grupos_permisos'
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data['search'] = search if search else ""
                data['ids'] = ids if ids else ""
                data['grupos'] = page.object_list
                return render_to_response("grupos_permisos/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')