# -*- coding: utf-8 -*-
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.form import AdministrativoForm, ProductoForm, DatosForm, ClonarProductoForm, ServicioForm
from app.funciones import informacionusuario, MiPaginador, url_back, bad_json, puede_generar_usuario, ok_json, log, \
    generar_usuario, resetear_clave
from app.models import TipoIdentificacion, Persona, Empleado, PerfilUsuario, Modulo, GrupoModulos, Producto, \
    LineaProducto, Marca, Inventario, TipoServicio, Presentacion
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
                form = ProductoForm(request.POST)
                if form.is_valid():
                    p = Producto(nombre=form.cleaned_data['nombre'],
                                 detalles=form.cleaned_data['detalles'],
                                 linea=form.cleaned_data['linea'],
                                 color=form.cleaned_data['color'],
                                 presentacion=form.cleaned_data['presentacion'],
                                 marca=form.cleaned_data['marca'])
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'adds':
            try:
                form = ServicioForm(request.POST)
                if form.is_valid():
                    p = Producto(nombre=form.cleaned_data['nombre'],
                                 detalles=form.cleaned_data['detalles'],
                                 tiposervicio=form.cleaned_data['tipo'],
                                 servicio=True,
                                 costo=form.cleaned_data['costo'])
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'edit':
            try:
                form = ProductoForm(request.POST)
                if form.is_valid():
                    p = Producto.objects.get(id=int(request.POST['id']))
                    p.nombre=form.cleaned_data['nombre']
                    p.presentacion=form.cleaned_data['presentacion']
                    p.detalles=form.cleaned_data['detalles']
                    p.linea=form.cleaned_data['linea']
                    p.marca=form.cleaned_data['marca']
                    p.color=form.cleaned_data['color']
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'edits':
            try:
                form = ServicioForm(request.POST)
                if form.is_valid():
                    p = Producto.objects.get(id=int(request.POST['id']))
                    p.nombre=form.cleaned_data['nombre']
                    p.detalles=form.cleaned_data['detalles']
                    p.tiposervicio=form.cleaned_data['tipo']
                    p.costo=form.cleaned_data['costo']
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'clonar':
            try:
                form = ClonarProductoForm(request.POST)
                if form.is_valid():
                    p = Producto.objects.get(id=int(request.POST['id']))
                    if p.talla == form.cleaned_data['talla']:
                        return bad_json(transaction, mensaje=u'No puede clonar un producto con la misma talla')
                    pnuevo = Producto(nombre=p.nombre,
                                      detalles=p.detalles,
                                      linea=p.linea,
                                      proveedor=p.proveedor,
                                      marca=p.marca,
                                      talla=form.cleaned_data['talla'])
                    pnuevo.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'addlinea':
            try:
                form = DatosForm(request.POST)
                if form.is_valid():
                    p = LineaProducto(nombre=form.cleaned_data['nombre'])
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'editlinea':
            try:
                form = DatosForm(request.POST)
                if form.is_valid():
                    p = LineaProducto.objects.get(id=int(request.POST['id']))
                    p.nombre = form.cleaned_data['nombre']
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'addpres':
            try:
                form = DatosForm(request.POST)
                if form.is_valid():
                    p = Presentacion(nombre=form.cleaned_data['nombre'])
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'editpres':
            try:
                form = DatosForm(request.POST)
                if form.is_valid():
                    p = Presentacion.objects.get(id=int(request.POST['id']))
                    p.nombre = form.cleaned_data['nombre']
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'addmarca':
            try:
                form = DatosForm(request.POST)
                if form.is_valid():
                    p = Marca(nombre=form.cleaned_data['nombre'])
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'editmarca':
            try:
                form = DatosForm(request.POST)
                if form.is_valid():
                    p = Marca.objects.get(id=int(request.POST['id']))
                    p.nombre = form.cleaned_data['nombre']
                    p.save()
                    return ok_json(transaction)
                else:
                    return bad_json(transaction, error=6)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delpres':
            try:
                p = Presentacion.objects.get(id=int(request.POST['id']))
                p.delete()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)


        if action == 'dellinea':
            try:
                p = LineaProducto.objects.get(id=int(request.POST['id']))
                p.delete()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        if action == 'delmarca':
            try:
                p = Marca.objects.get(id=int(request.POST['id']))
                p.delete()
                return ok_json(transaction)
            except Exception as ex:
                return bad_json(transaction, error=1)

        return bad_json(transaction, error=0)
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'add':
                try:
                    data['title'] = u'Adicionar Artículo'
                    form = ProductoForm()
                    data['form'] = form
                    return render_to_response("inventario/add.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'adds':
                try:
                    data['title'] = u'Adicionar Servicio'
                    form = ServicioForm()
                    data['form'] = form
                    return render_to_response("inventario/adds.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'presentaciones':
                try:
                    data['title'] = u'Presentaciones de artículos'
                    data['lineas'] = Presentacion.objects.all()
                    return render_to_response("inventario/presentaciones.html", data)
                except Exception as ex:
                    pass

            if action == 'lineas':
                try:
                    data['title'] = u'Líneas de artículos'
                    data['lineas'] = LineaProducto.objects.all()
                    return render_to_response("inventario/lineas.html", data)
                except Exception as ex:
                    pass

            if action == 'delpres':
                try:
                    data['title'] = u'Eliminar Presentación'
                    data['linea'] = linea = Presentacion.objects.get(id=int(request.GET['id']))
                    return render_to_response("clientes/delpres.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'dellinea':
                try:
                    data['title'] = u'Eliminar Linea'
                    data['linea'] = linea = LineaProducto.objects.get(id=int(request.GET['id']))
                    return render_to_response("clientes/dellinea.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delmarca':
                try:
                    data['title'] = u'Eliminar Marca'
                    data['linea'] = linea = Marca.objects.get(id=int(request.GET['id']))
                    return render_to_response("clientes/delmarca.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'delmodelo':
                try:
                    data['title'] = u'Eliminar Modelo'
                    data['linea'] = linea = TipoServicio.objects.get(id=int(request.GET['id']))
                    return render_to_response("clientes/delmodelo.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'addpres':
                try:
                    data['title'] = u'Adicionar Presentación'
                    form = DatosForm()
                    data['form'] = form
                    return render_to_response("inventario/addpres.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'addlinea':
                try:
                    data['title'] = u'Adicionar Linea'
                    form = DatosForm()
                    data['form'] = form
                    return render_to_response("inventario/addlinea.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'editpres':
                try:
                    data['title'] = u'Editar Presentación'
                    data['linea'] = linea = Presentacion.objects.get(id=int(request.GET['id']))
                    form = DatosForm(initial={'nombre': linea.nombre})
                    data['form'] = form
                    return render_to_response("inventario/editpres.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'editlinea':
                try:
                    data['title'] = u'Editar Linea'
                    data['linea'] = linea = LineaProducto.objects.get(id=int(request.GET['id']))
                    form = DatosForm(initial={'nombre': linea.nombre})
                    data['form'] = form
                    return render_to_response("inventario/editlinea.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'modelos':
                try:
                    data['title'] = u'Modelos de artículos'
                    data['modelos'] = TipoServicio.objects.all()
                    return render_to_response("inventario/modelos.html", data)
                except Exception as ex:
                    pass

            if action == 'addmodelo':
                try:
                    data['title'] = u'Adicionar Modelo'
                    form = DatosForm()
                    data['form'] = form
                    return render_to_response("inventario/addmodelo.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'editmodelo':
                try:
                    data['title'] = u'Editar Modelo'
                    data['modelo'] = modelo = TipoServicio.objects.get(id=int(request.GET['id']))
                    form = DatosForm(initial={'nombre': modelo.nombre})
                    data['form'] = form
                    return render_to_response("inventario/editmodelo.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'marcas':
                try:
                    data['title'] = u'Marcas de artículos'
                    data['marcas'] = Marca.objects.all()
                    return render_to_response("inventario/marcas.html", data)
                except Exception as ex:
                    pass

            if action == 'movimientos':
                try:
                    data['title'] = u'Movimientos del artículo'
                    data['inv'] = inv = Inventario.objects.get(id=int(request.GET['id']))
                    data['movimientos'] = inv.kardexinventario_set.all().order_by('-fechaingreso')
                    return render_to_response("inventario/movimientos.html", data)
                except Exception as ex:
                    pass

            if action == 'addmarca':
                try:
                    data['title'] = u'Adicionar Marca'
                    form = DatosForm()
                    data['form'] = form
                    return render_to_response("inventario/addmarca.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'editmarca':
                try:
                    data['title'] = u'Editar Marca'
                    data['marca'] = marca = Marca.objects.get(id=int(request.GET['id']))
                    form = DatosForm(initial={'nombre': marca.nombre})
                    data['form'] = form
                    return render_to_response("inventario/editmarca.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'edit':
                try:
                    data['title'] = u'Editar Artículo'
                    data['art'] = art = Producto.objects.get(id=int(request.GET['id']))
                    form = ProductoForm(initial={'linea': art.linea,
                                                 'nombre': art.nombre,
                                                 'detalles': art.detalles,
                                                 'color': art.color,
                                                 'presentacion': art.presentacion,
                                                 'marca': art.marca})
                    data['form'] = form
                    return render_to_response("inventario/edit.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'edits':
                try:
                    data['title'] = u'Editar Servicio'
                    data['art'] = art = Producto.objects.get(id=int(request.GET['id']))
                    form = ServicioForm(initial={'tipo': art.tiposervicio,
                                                 'nombre': art.nombre,
                                                 'detalles': art.detalles,
                                                 'costo': art.costo})
                    data['form'] = form
                    return render_to_response("inventario/edits.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            if action == 'clonar':
                try:
                    data['title'] = u'Clonar Artículo'
                    data['art'] = art = Producto.objects.get(id=int(request.GET['id']))
                    form = ClonarProductoForm(initial={'linea': art.linea,
                                                 'nombre': art.nombre,
                                                 'color': art.color,
                                                 'detalles': art.detalles,
                                                 'modelo': art.modelo,
                                                 'marca': art.marca})
                    data['form'] = form
                    return render_to_response("inventario/clonar.html", data, context_instance=RequestContext(request))
                except Exception as ex:
                    pass

            return url_back(request, ex=ex if 'ex' in locals() else None)

        else:
            try:
                data['title'] = u'Listado de personal administrativo'
                search = None
                ids = None
                if 's' in request.GET:
                    search = request.GET['s'].strip()
                    productos = Producto.objects.filter(Q(nombre__icontains=search) |
                                                        Q(linea__nombre__icontains=search) |
                                                        Q(marca__nombre__icontains=search)).distinct()
                elif 'id' in request.GET:
                    ids = request.GET['id']
                    productos = Producto.objects.filter(id=ids).distinct()
                else:
                    productos = Producto.objects.all()
                paging = MiPaginador(productos, 25)
                p = 1
                try:
                    paginasesion = 1
                    if 'paginador' in request.session and 'paginador_url' in request.session:
                        if request.session['paginador_url'] == 'inventario':
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
                request.session['paginador_url'] = 'inventario'
                data['paging'] = paging
                data['rangospaging'] = paging.rangos_paginado(p)
                data['page'] = page
                data['search'] = search if search else ""
                data['ids'] = ids if ids else ""
                data['productos'] = page.object_list
                return render_to_response("inventario/view.html", data, context_instance=RequestContext(request))
            except Exception as ex:
                return HttpResponseRedirect('/')