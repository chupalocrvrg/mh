# -*- coding: utf-8 -*-
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ClienteForm, EmpresaForm, GastoForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave, convertir_fecha_invertida
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Cliente, Institucion, IvaAplicado, \
    ANIO_LISTADO, MESES_LISTADO, Gastos, DetalleGastos
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
                form = GastoForm(request.POST)
                if form.is_valid():
                    g = Gastos(descripcion=form.cleaned_data['descripcion'],
                               fecha=convertir_fecha_invertida(form.cleaned_data['fecha']),
                               total=form.cleaned_data['costo'],
                               sueldo=False,
                               finalizado=True)
                    g.save(request)
                    log(u'Adiciono gasto: %s' % g, request, "add")
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        elif action == 'act_adicional':
            try:
                pago = DetalleGastos.objects.get(pk=request.POST['id'])
                pago.adicional = float(request.POST['valor'])
                pago.save()
                pago.gasto.actualiza_total()
                valor = round(pago.total, 2)
                return ok_json(transaction, data={ "final": str(valor)})
            except Exception as ex:
                return bad_json(transaction, error=1)

        elif action == 'act_descuento':
            try:
                pago = DetalleGastos.objects.get(pk=request.POST['id'])
                pago.descuento = float(request.POST['valor'])
                pago.save()
                pago.gasto.actualiza_total()
                valor = round(pago.total, 2)
                return ok_json(transaction, data={"final": str(valor)})
            except Exception as ex:
                return bad_json(transaction, error=1)

        elif action == 'cerrar':
            try:
                pago = Gastos.objects.get(pk=request.POST['id'])
                pago.finalizado = True
                pago.save()
                pago.actualiza_total()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        elif action == 'generar':
            try:
                anio = int(request.POST['anio'])
                mes = int(request.POST['mes'])
                fecha = date(anio, mes, 1)
                if Gastos.objects.filter(sueldo=True, fecha__year=anio, fecha__month=mes).exists():
                    return bad_json(transaction, mensaje=u'Ya existe un Pago en esta fecha')
                g = Gastos(fecha=fecha,
                           sueldo=True)
                g.save()
                for e in Empleado.objects.all():
                    d = DetalleGastos(gasto=g,
                                      empleado=e,
                                      adicional=0,
                                      descuento=0,
                                      total=0)
                    d.save()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Gasto'
                    form = GastoForm()
                    data['form'] = form
                    return render_to_response("gastos/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'otros':
                try:
                    data['title'] = u'Gastos Operativos'
                    data['gastos'] = Gastos.objects.filter(sueldo=False)
                    return render_to_response("gastos/otros.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                anio = datetime.now().year
                mes = datetime.now().month
                pago = None
                if 'anio_otro' in request.session:
                    anio = int(request.session['anio_otro'])
                if 'anio_otro' in request.GET:
                    request.session['anio_otro'] = anio = int(request.GET['anio_otro'])
                if 'mes_otro' in request.session:
                    mes = int(request.session['mes_otro'])
                if 'mes_otro' in request.GET:
                    request.session['mes_otro'] = mes = int(request.GET['mes_otro'])
                if Gastos.objects.filter(sueldo=True, fecha__year=anio, fecha__month=mes).exists():
                    pago = Gastos.objects.filter(sueldo=True, fecha__year=anio, fecha__month=mes)[0]
                data['title'] = u'Gastos por pago de sueldos'
                data['anios'] = ANIO_LISTADO
                data['meses'] = MESES_LISTADO
                data['empresa'] = Institucion.objects.all()[0]
                data['pago'] = pago
                data['anio'] = anio
                data['mes'] = mes
                return render_to_response("gastos/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')