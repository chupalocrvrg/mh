# coding=utf-8
from datetime import datetime

import os
from django import forms
from django.forms import DateTimeInput, CheckboxSelectMultiple
from django.utils.safestring import mark_safe

from settings import TIPO_RUBRO_ESPECIE_VALORADA_ID
from app.models import TipoIdentificacion, Provincia, Canton, TipoPerfilUsuario, LineaProducto, Marca, Producto, \
    COLORES_LISTA, Proveedor, CompraProducto, Factura, Sucursales, TipoServicio, Presentacion



class CambioClaveForm(forms.Form):
    anterior = forms.CharField(label=u'Contraseña anterior', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))
    nueva = forms.CharField(label=u'Nueva contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))
    repetir = forms.CharField(label=u'Repetir contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))


class CambioPeriodoForm(forms.Form):
    sucursal = forms.ModelChoiceField(Sucursales.objects.all(), label=u'Sucursales', widget=forms.Select(attrs={'class': 'form-control', 'formwidth': '400'}))

    def editar(self, persona):
        self.fields['sucursal'].queryset = Sucursales.objects.filter(empleadosucursal__empleado=persona)


class TipoAdministrativoForm(forms.Form):
    tipoempleado = forms.ModelChoiceField(label=u"Tipo Empleado", required=False, queryset=TipoPerfilUsuario.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))


class AdministrativoForm(forms.Form):
    nombre1 = forms.CharField(label=u"1er Nombre", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre2 = forms.CharField(label=u"2do Nombre", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido1 = forms.CharField(label=u"1er Apellido", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido2 = forms.CharField(label=u"2do Apellido", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipoempleado = forms.ModelChoiceField(label=u"Tipo Empleado", required=False, queryset=TipoPerfilUsuario.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    tipoidentificacion = forms.ModelChoiceField(label=u"Tipo Identificación", required=False, queryset=TipoIdentificacion.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    identificacion = forms.CharField(label=u"Identificación", max_length=13, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    provincia = forms.ModelChoiceField(label=u"Provincia de residencia", queryset=Provincia.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    canton = forms.ModelChoiceField(label=u"Cantón de residencia", queryset=Canton.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    sector = forms.CharField(label=u"Sector", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label=u"Calle Principal", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion2 = forms.CharField(label=u"Calle Secundaria", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    referencia = forms.CharField(label=u"Referencia", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero = forms.CharField(label=u"Número de domicilio", max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonomovil = forms.CharField(label=u"Teléfono Movil", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonofijo = forms.CharField(label=u"Teléfono Fijo", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label=u"Correo Electrónico", max_length=240, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sueldo = forms.FloatField(label=u"Sueldo base", required=False, initial="0.00", widget=forms.TextInput(attrs={'class': 'form-control imp-numbersmall', 'decimales': '2'}))

    def editar(self, administrativo):
        deshabilitar_campo(self, 'tipoidentificacion')
        deshabilitar_campo(self, 'tipoempleado')
        deshabilitar_campo(self, 'identificacion')


class ClienteForm(forms.Form):
    nombres = forms.CharField(label=u"Nombres", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidos = forms.CharField(label=u"Apellidos", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipoidentificacion = forms.ModelChoiceField(label=u"Tipo Identificación", required=False, queryset=TipoIdentificacion.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    identificacion = forms.CharField(label=u"Identificación", max_length=13, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    provincia = forms.ModelChoiceField(label=u"Provincia de residencia", queryset=Provincia.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    canton = forms.ModelChoiceField(label=u"Cantón de residencia", queryset=Canton.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    sector = forms.CharField(label=u"Sector", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label=u"Calle Principal", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonomovil = forms.CharField(label=u"Teléfono Movil", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonofijo = forms.CharField(label=u"Teléfono Fijo", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label=u"Correo Electrónico", max_length=240, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def editar(self, administrativo):
        deshabilitar_campo(self, 'tipoidentificacion')
        deshabilitar_campo(self, 'identificacion')


class SucursalForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    provincia = forms.ModelChoiceField(label=u"Provincia de residencia", queryset=Provincia.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    canton = forms.ModelChoiceField(label=u"Cantón de residencia", queryset=Canton.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label=u"Calle Principal", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class EmpresaForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    ruc = forms.CharField(label=u"RUC", max_length=13, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    provincia = forms.ModelChoiceField(label=u"Provincia de residencia", queryset=Provincia.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    canton = forms.ModelChoiceField(label=u"Cantón de residencia", queryset=Canton.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    sector = forms.CharField(label=u"Sector", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label=u"Calle Principal", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonofijo = forms.CharField(label=u"Teléfono Fijo", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label=u"Correo Electrónico", max_length=240, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    utilidad = forms.FloatField(initial='0', required=False, label=u'Utilidad', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))
    iva = forms.FloatField(initial='0', required=False, label=u'IVA', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))


class ProveedorForm(forms.Form):
    razonsocial = forms.CharField(label=u"Razon social", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    representante = forms.CharField(label=u"Representante", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipoidentificacion = forms.ModelChoiceField(label=u"Tipo Identificación", required=False, queryset=TipoIdentificacion.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    identificacion = forms.CharField(label=u"Identificación", max_length=13, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    provincia = forms.ModelChoiceField(label=u"Provincia de residencia", queryset=Provincia.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    canton = forms.ModelChoiceField(label=u"Cantón de residencia", queryset=Canton.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    sector = forms.CharField(label=u"Sector", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label=u"Calle Principal", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonomovil = forms.CharField(label=u"Teléfono Movil", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonofijo = forms.CharField(label=u"Teléfono Fijo", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label=u"Correo Electrónico", max_length=240, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def editar(self, administrativo):
        deshabilitar_campo(self, 'tipoidentificacion')
        deshabilitar_campo(self, 'identificacion')


class PresupuestoForm(forms.Form):
    valor = forms.FloatField(initial='0', required=False, label=u'Valor', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))


class GastoForm(forms.Form):
    fecha = forms.CharField(label=u"Fecha ", initial=datetime.now().date(), required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    descripcion = forms.CharField(label=u"Información", max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    costo = forms.FloatField(initial='0', required=False, label=u'Costo', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))


class MiCuentaForm(forms.Form):
    nombre1 = forms.CharField(label=u"1er Nombre", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nombre2 = forms.CharField(label=u"2do Nombre", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido1 = forms.CharField(label=u"1er Apellido", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellido2 = forms.CharField(label=u"2do Apellido", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipoidentificacion = forms.ModelChoiceField(label=u"Tipo Identificación", required=False, queryset=TipoIdentificacion.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    identificacion = forms.CharField(label=u"Identificación", max_length=13, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    nacimiento = forms.DateField(label=u"Fecha Nacimiento", initial=datetime.now().date(), required=False, input_formats=['%d-%m-%Y'], widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'form-control selectorfecha', 'onkeydown': 'return false;'}))
    provincia = forms.ModelChoiceField(label=u"Provincia de residencia", queryset=Provincia.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    canton = forms.ModelChoiceField(label=u"Cantón de residencia", queryset=Canton.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    sector = forms.CharField(label=u"Sector", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label=u"Calle Principal", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion2 = forms.CharField(label=u"Calle Secundaria", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    referencia = forms.CharField(label=u"Referencia", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    numero = forms.CharField(label=u"Número de domicilio", max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonomovil = forms.CharField(label=u"Teléfono Movil", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonofijo = forms.CharField(label=u"Teléfono Fijo", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(label=u"Correo Electrónico", max_length=240, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    emailinst = forms.CharField(label=u"Correo Electrónico Institucional", max_length=240, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def editar(self, perfil):
        self.fields['tipoidentificacion'].queryset = TipoIdentificacion.objects.filter(institucion=perfil.persona.institucion).exclude( ruc=True)
        self.fields['provincia'].queryset = Provincia.objects.filter(institucion=perfil.persona.institucion)
        self.fields['canton'].queryset = Canton.objects.filter(provincia=perfil.persona.provincia)
        deshabilitar_campo(self, 'tipoidentificacion')
        deshabilitar_campo(self, 'identificacion')
        deshabilitar_campo(self, 'nombre1')
        deshabilitar_campo(self, 'nombre2')
        deshabilitar_campo(self, 'apellido1')
        deshabilitar_campo(self, 'apellido2')
        deshabilitar_campo(self, 'tipoidentificacion')
        deshabilitar_campo(self, 'identificacion')
        deshabilitar_campo(self, 'nacimiento')
        deshabilitar_campo(self, 'emailinst')
        deshabilitar_campo(self, 'sexo')
        if perfil.es_representante():
            del self.fields['emailinst']
        if perfil.es_alumno():
            deshabilitar_campo(self, 'etnia')
            deshabilitar_campo(self, 'nacionalidadindigena')
            deshabilitar_campo(self, 'sangre')
            deshabilitar_campo(self, 'paisnacimiento')
            deshabilitar_campo(self, 'provincia')
            deshabilitar_campo(self, 'canton')
            deshabilitar_campo(self, 'parroquia')
            deshabilitar_campo(self, 'sector')
            deshabilitar_campo(self, 'direccion')
            deshabilitar_campo(self, 'direccion2')
            deshabilitar_campo(self, 'referencia')
            deshabilitar_campo(self, 'numero')


class NoticiaForm(forms.Form):
    # tiponoticia = forms.ModelChoiceField(label=u"Tipo de noticia", required=False, queryset=TipoNoticia.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    nombre = forms.CharField(label=u"Titulo", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    cuerpo = forms.CharField(label=u"Contenido", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}))
    desde = forms.DateField(label=u"Desde", initial=datetime.now().date(), input_formats=['%d-%m-%Y'], widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'form-control selectorfecha', 'onkeydown': 'return false;'}), required=False)
    hasta = forms.DateField(label=u"Hasta", initial=datetime.now().date(), input_formats=['%d-%m-%Y'], widget=DateTimeInput(format='%d-%m-%Y', attrs={'class': 'form-control selectorfecha', 'onkeydown': 'return false;'}), required=False)
    activo = forms.BooleanField(label=u"Activa", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control lcs_switch'}))
    profesor = forms.BooleanField(label=u"Profesores", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control lcs_switch'}))
    representante = forms.BooleanField(label=u"Representantes", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control lcs_switch'}))
    estudiante = forms.BooleanField(label=u"Estudiantes", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control lcs_switch'}))
    administrativo = forms.BooleanField(label=u"Administrativos", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control lcs_switch'}))
    archivo = ExtFileField(label=u'Archivo', required=False, help_text=u'Tamaño máximo permitido 4Mb, en formato jpg', ext_whitelist=(".jpg", ".png"), max_upload_size=4194304, widget=forms.FileInput(attrs={'class': 'form-control-file'}))


class ManualForm(forms.Form):
    nombre = forms.CharField(label=u"Titulo", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    detalles = forms.CharField(label=u"Objetivos / Especificaciones", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}))
    archivo = ExtFileField(label=u'Archivo de respaldo', required=False, help_text=u'Tamaño máximo permitido 4Mb, en formato pdf, docx', ext_whitelist=(".pdf", ".docx"), max_upload_size=4194304, widget=forms.FileInput(attrs={'class': 'form-control-file'}))


class TraspasoForm(forms.Form):
    origen = forms.ModelChoiceField(label=u"Origen", required=False, queryset=Sucursales.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    destino = forms.ModelChoiceField(label=u"Destino", required=False, queryset=Sucursales.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    producto = forms.ModelChoiceField(label=u"Producto", required=False, queryset=Producto.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    cantidad = forms.IntegerField(initial='0', required=False, label=u'Cantidad', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))
    motivo = forms.CharField(label=u"Motivo", widget=forms.Textarea(attrs={'class': 'form-control color', 'rows': '4'}))


class ProductoForm(forms.Form):
    linea = forms.ModelChoiceField(label=u"Linea", required=False, queryset=LineaProducto.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    nombre = forms.CharField(label=u"Nombre", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    detalles = forms.CharField(label=u"Detalles", widget=forms.Textarea(attrs={'class': 'form-control color', 'rows': '4'}))
    color =  forms.ChoiceField(COLORES_LISTA, label=u'Color', required=False, widget=forms.Select(attrs={'class': 'form-control imp-50 select', 'colores': 'true'}))
    marca = forms.ModelChoiceField(label=u"Marca", required=False, queryset=Marca.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    presentacion = forms.ModelChoiceField(label=u"Presentación", required=False, queryset=Presentacion.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))


class ServicioForm(forms.Form):
    tipo = forms.ModelChoiceField(label=u"Tipo", required=False, queryset=TipoServicio.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    nombre = forms.CharField(label=u"Nombre", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    detalles = forms.CharField(label=u"Detalles", widget=forms.Textarea(attrs={'class': 'form-control color', 'rows': '4'}))
    costo = forms.FloatField(initial='0', required=False, label=u'Costo', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))


class DevolucionForm(forms.Form):
    factura = forms.ModelChoiceField(label=u"Factura", required=False,  queryset=CompraProducto.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    motivo = forms.CharField(label=u"Motivo",  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}))


class DevolucionFacturaForm(forms.Form):
    factura = forms.ModelChoiceField(label=u"Factura", required=False,  queryset=Factura.objects.all(), widget=forms.Select(attrs={'class': 'form-control select'}))
    motivo = forms.CharField(label=u"Motivo",
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}))


class ClonarProductoForm(forms.Form):
    linea = forms.ModelChoiceField(label=u"Linea", required=False, queryset=LineaProducto.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}))
    nombre = forms.CharField(label=u"Nombre", max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}))
    detalles = forms.CharField(label=u"Detalles", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'disabled': 'disabled'}))
    color = forms.CharField(label=u"Color", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control imp-100'}))
    marca = forms.ModelChoiceField(label=u"Marca", required=False, queryset=Marca.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}))


class CompraProductoForm(forms.Form):
    articulo = forms.ModelChoiceField(label=u"Articulo", required=False, queryset=Producto.objects.filter(servicio=False), widget=forms.Select(attrs={'class': 'form-control select'}))
    cantidad = forms.IntegerField(initial='0', required=False, label=u'Cantidad', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))
    costo = forms.FloatField(initial='0', required=False, label=u'Costo', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))
    subtotal = forms.FloatField(initial='0', required=False, label=u'Subtotal', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    porcentaje = forms.FloatField(initial='0', required=False, label=u'Porciento IVA', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    iva = forms.FloatField(initial='0', required=False, label=u'IVA', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    total = forms.FloatField(initial='0', required=False, label=u'Total', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled' }))


class SalidaProductoForm(forms.Form):
    articulo = forms.ModelChoiceField(label=u"Articulo", required=False, queryset=Producto.objects.filter(inventario__cantidad__gt=0).distinct(), widget=forms.Select(attrs={'class': 'form-control select'}))
    disponible = forms.FloatField(initial='0', required=False, label=u'Stock Disponible', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    otras = forms.FloatField(initial='0', required=False, label=u'En otras sucursales', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    cantidad = forms.IntegerField(initial='0', required=False, label=u'Cantidad', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))
    costo = forms.FloatField(initial='0', required=False, label=u'Costo', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))
    subtotal = forms.FloatField(initial='0', required=False, label=u'Subtotal', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    porcentaje = forms.FloatField(initial='0', required=False, label=u'Porciento IVA', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    iva = forms.FloatField(initial='0', required=False, label=u'IVA', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled'}))
    descuento = forms.FloatField(initial='0', required=False, label=u'Descuento', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center'}))
    total = forms.FloatField(initial='0', required=False, label=u'Total', widget=forms.TextInput(attrs={'class': 'form-control imp-number-center', 'disabled': 'disabled' }))

    def editar(self, sucursal):
        self.fields['articulo'].queryset = Producto.objects.filter(inventario__cantidad__gt=0, inventario__sucursal=sucursal).distinct()


class InfoCompraProductoForm(forms.Form):
    numero = forms.CharField(label=u"Factura", max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'form-control imp-50', 'disabled': 'disabled'}))


class DatosForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))


class ProductoCompraForm(forms.Form):
    producto = forms.CharField(label=u"Nombre", max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))


class GrupoInstitucionForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class TurnoForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    horainicio = forms.TimeField(label=u"Comienza", input_formats=['%H:%M'], widget=forms.TextInput(attrs={'class': 'form-control datetimepicker-input', 'data-target': "#datetimepicker3"}))
    horafin = forms.TimeField(label=u"Termina", input_formats=['%H:%M'], widget=forms.TextInput(attrs={'class': 'form-control datetimepicker-input', 'data-target': "#datetimepicker3"}))


class CargoInstitucionForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    responsable = forms.IntegerField(initial='0', required=False, label=u'Responsable', widget=forms.TextInput(attrs={'select2search': 'true', 'class': 'form-control select2advance'}))

    def editar(self, cargo):
        if cargo.mi_responsable():
            self.fields['responsable'].widget.attrs['descripcion'] = cargo.mi_responsable().persona.flexbox_repr()


class TipoRubroForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    alias = forms.CharField(label=u"Alias", max_length=3, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class CajeroInstitucionForm(forms.Form):
    persona = forms.IntegerField(initial='0', required=False, label=u'Persona', widget=forms.TextInput(attrs={'select2search': 'true', 'class': 'form-control select2advance'}))


class InstitucionForm(forms.Form):
    nombre = forms.CharField(label=u"Nombre", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    ruc = forms.CharField(label=u"RUC", max_length=13, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telefonofijo = forms.CharField(label=u"Teléfono Fijo", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    provincia = forms.ModelChoiceField(label=u"Provincia de residencia", queryset=Provincia.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    canton = forms.ModelChoiceField(label=u"Cantón de residencia", queryset=Canton.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    sector = forms.CharField(label=u"Sector", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(label=u"Calle Principal", max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dominiocorreo = forms.CharField(label=u"Dominio", max_length=240, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    correopropio = forms.BooleanField(label=u"Usa servidor de correo propio", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    contribuyenteespecial = forms.BooleanField(label=u"Es contribuyente especial", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    background = ExtFileField(label=u'Imagen Institucional', required=False, help_text=u'Tamaño máximo permitido 4Mb, en formato jpg', ext_whitelist=(".jpg", ".png"), max_upload_size=4194304, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def editar(self, institucion):
        self.fields['provincia'].queryset = Provincia.objects.filter(institucion=institucion)
        self.fields['canton'].queryset = Canton.objects.filter(provincia=institucion.dato_institucion().provincia)


class InstitucionArchivoForm(forms.Form):
    background = ExtFileField(label=u'Imagen Institucional', required=False, help_text=u'Tamaño máximo permitido 4Mb, en formato jpg', ext_whitelist=(".jpg", ".png"), max_upload_size=4194304, widget=forms.FileInput(attrs={'class': 'form-control'}))