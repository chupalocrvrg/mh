# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm, EmpresaForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente, Institucion, IvaAplicado
from django.template import RequestContext


@login_required(redirect_field_name='ret', login_url='/login')
@transaction.commit_on_success
def view(request):
    global ex
    data = informacionusuario(request)
    persona = request.session['persona']
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'edit':
            try:
                form = EmpresaForm(request.POST)
                if form.is_valid():
                    empresa = Institucion.objects.all()[0]
                    dato = empresa.dato_institucion()
                    iva = IvaAplicado.objects.all()[0]
                    empresa.nombre = form.cleaned_data['nombre']
                    dato.ruc = form.cleaned_data['ruc']
                    dato.provincia=form.cleaned_data['provincia']
                    dato.canton=form.cleaned_data['canton']
                    dato.sector=form.cleaned_data['sector']
                    dato.direccion=form.cleaned_data['direccion']
                    dato.telefonofijo=form.cleaned_data['telefonofijo']
                    dato.email=form.cleaned_data['email']
                    dato.margenutilidad=form.cleaned_data['utilidad']
                    iva.porciento=form.cleaned_data['iva']
                    dato.save()
                    empresa.save()
                    log(u'Modifico dato empresa: %s' % dato, request, "edit")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'edit':
                try:
                    data['title'] = u'Editar Informacion'
                    data['empresa'] = empresa = Institucion.objects.all()[0]
                    dato = empresa.dato_institucion()
                    data['iva'] = iva = IvaAplicado.objects.all()[0]
                    form = EmpresaForm(initial={'nombre': empresa.nombre,
                                               'ruc': dato.ruc,
                                               'provincia': dato.provincia,
                                               'canton': dato.canton,
                                               'sector': dato.sector,
                                               'direccion': dato.direccion,
                                               'telefonofijo': dato.telefonofijo,
                                               'utilidad': dato.margenutilidad,
                                               'iva': iva.porciento,
                                               'email': dato.email})
                    data['form'] = form
                    return render_to_response("administracion/edit.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Configuración de parámetros'
                data['empresa'] = Institucion.objects.all()[0]
                return render_to_response("administracion/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')