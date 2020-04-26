# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
from datetime import datetime, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response

from app.email import send_html_mail
from app.form import CambioClaveForm, CambioPeriodoForm
from app.funciones import bad_json, ok_json, informacionusuario, log
from app.models import Empleado, Cliente, ManualProcedimientos, EmpleadoSucursal, Persona, Institucion


@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def panel(request):
    data = informacionusuario(request)
    data['empresa'] = empresa = request.session['empresa']
    data['sucursal'] = request.session['sucursal']
    perfil = request.session['perfilprincipal']
    topten = []
    for cliente in Cliente.objects.filter(factura__isnull=False,
                                          factura__valida=True).distinct().annotate(cantidadventas=Count('factura__id')).distinct().order_by('-cantidadventas')[:10]:
        topten.append((cliente, cliente.cantidadventas, cliente.valor_ventas()))
    data['toptenc'] = topten
    data['manuales'] = ManualProcedimientos.objects.all()
    return render(request, 'panel.html', data)


def logout_user(request):
    try:
        persona = request.session['persona']
    except:
        pass
    logout(request)
    return HttpResponseRedirect('/')



def cambiosucursal(request):
    global ex
    data = informacionusuario(request)
    persona = data['persona']
    if request.method == 'POST':
        try:
            form = CambioPeriodoForm(request.POST)
            if form.is_valid():
                data['sucursal'] = request.session['sucursal'] = form.cleaned_data['sucursal']
                return ok_json()
            else:
                return bad_json(error=6)
        except Exception as ex:
            transaction.rollback()
            return bad_json(mensaje=u"No se puede cambiar de periodo.")
    else:
        try:
            data['title'] = u'Cambio de sucursal'
            form = CambioPeriodoForm(initial={'sucursal': request.session['sucursal']})
            form.editar(persona)
            data['form'] = form
            data['path'] = request.GET['path']
            return render(request, 'sucursal.html', data)
        except Exception as ex:
            return HttpResponseRedirect('/')


@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def com_password(request):
    data = informacionusuario(request)
    if request.method == "POST":
        if 'action' in request.POST:
            action = request.POST['action']

            if action == 'cambiopass':
                try:
                    form = CambioClaveForm(request.POST)
                    if form.is_valid():
                        persona = data['persona']
                        usuario = User.objects.get(pk=persona.usuario.id)
                        if not usuario.check_password(form.cleaned_data['anterior']):
                            return bad_json(transaction, mensaje=u"Clave anterior no coincide.")
                        usuario.set_password(form.cleaned_data['nueva'])
                        persona.clave_cambiada()
                        return ok_json(transaction)
                    else:
                        return bad_json(transaction, error=6)
                except Exception as ex:
                    return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        try:
            data['form'] = CambioClaveForm(formwidth=5)
            return render(request, 'password.html', data)
        except Exception as ex:
            return HttpResponseRedirect('/')


@transaction.commit_on_success
def login_user(request):
    if request.method == 'POST':
        inputusuario = request.POST['inputusuario']
        inputPassword = request.POST['inputPassword']
        user = authenticate(username=inputusuario, password=inputPassword)
        if not User.objects.filter(username=inputusuario).exists():
            return HttpResponseRedirect('/login?mensaje=Credenciales incorrectas')
        user = authenticate(username=inputusuario, password=inputPassword)
        persona = None
        if Empleado.objects.filter(persona__usuario__username=inputusuario).exists():
            persona = Empleado.objects.filter(persona__usuario__username=inputusuario)[0]
            if not EmpleadoSucursal.objects.filter(empleado=persona).exists():
                return HttpResponseRedirect('/login?mensaje=No tiene asignada una sucursal')
        if not user:
            return HttpResponseRedirect('/login?mensaje=Credenciales incorrectas')
        if not user.is_active:
            return HttpResponseRedirect('/login?mensaje=Credenciales incorrectas')
        login(request, user)
        request.session['persona'] = persona
        request.session['perfilprincipal'] = persona.mi_perfil()
        request.session['timeout'] = datetime.now() + timedelta(minutes=persona.persona.sessiontime)
        login(request, user)
        return HttpResponseRedirect('/')
    else:
        ret = '/'
        if 'ret' in request.GET:
            ret = request.GET['ret']
        data = {"title": "Login",
                "return_url": ret,
                "background": random.randint(1, 4),
                "error": request.GET['error'] if 'error' in request.GET else "",
                "errorp": request.GET['errorp'] if 'errorp' in request.GET else "",
                'request': request}
        data = informacionusuario(request)
        data['usuario'] = None
        mensaje = ''
        if 'mensaje' in request.GET:
            data['mensaje'] = request.GET['mensaje']
        return render_to_response("login.html", data)



def login_user_empty(request):
    return HttpResponseRedirect("/")
