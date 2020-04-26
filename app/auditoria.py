# -*- coding: utf-8 -*-
from django.contrib.admin.models import LogEntry
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
    data['persona'] = persona = request.session['persona']
    if request.method == 'POST':
        action = request.POST['action']

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Acciones de usuarios'
                search = None
                ids = None
                data['acciones'] = LogEntry.objects.all().order_by('-action_time')
                return render_to_response("auditoria/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')