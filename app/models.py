# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
from _ast import mod
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User, Group, Permission
from django.db import models
from django.db.models import Sum
from django.db.models.query_utils import Q
from django.db.models.query import QuerySet

from settings import EMAIL_REGISTRO_NUEVO_CLIENTE
from app.email import send_html_mail
from app.funciones import enletras



def id_search(param):
    try:
        return int(param)
    except:
        return 0

class CustomQuerySet(QuerySet):
    def delete(self):
        for i in self:
            i.delete()


class ActiveManager(models.Manager):
    def get_query_set(self):
        return CustomQuerySet(self.model, using=self._db)


COLORES_LISTA = (
    ('#CD5C5C', u'ROJO INDIO'),
    ('#F08080', u'CORAL CLARO'),
    ('#F08080', u'SALMON'),
    ('#E9967A', u'SALMON OSCURO'),
    ('#FF0000', u'CARMESÍ'),
    ('#8B0000', u'ROJO OSCURO'),
    ('#FFC0CB', u'ROSA'),
    ('#C71585', u'VIOLETA'),
    ('#FF6347', u'TOMATE'),
    ('#FF4500', u'NARANJA ROJIZO'),
    ('#FF8C00', u'NARANJA OSCURO'),
    ('#FFA500', u'NARANJA'),
    ('#FFD700', u'ORO'),
    ('#FFFF00', u'AMARILLO'),
    ('#FFFACD', u'LIMA'),
    ('#F0E68C', u'KHAKI'),
    ('#BDB76B', u'KHAKI OSCURO'),
    ('#E6E6FA', u'LAVANDA'),
    ('#FF00FF', u'FUCHSIA'),
    ('MAGENTA', u'MAGENTA'),
    ('#BA55D3', u'ORQUIDEA'),
    ('#800080', u'PURPURA'),
    ('#4B0082', u'INDIGO'),
    ('#00FF00', u'VERDE LIMÓN'),
    ('#32CD32', u'VERDE LIMÓN OSCURO'),
    ('#98FB98', u'VERDE PALIDO'),
    ('#90EE90', u'VERDE CLARO'),
    ('#2E8B57', u'VERDE MARINO'),
    ('#008000', u'VERDE'),
    ('#006400', u'VERDE OSCURO'),
    ('#4682B4', u'AZUL ACERO'),
    ('#ADD8E6', u'AZUL CLARO'),
    ('#0000FF', u'AZUL'),
    ('#00008B', u'AZUL OSCURO'),
    ('#D2691E', u'CHOCOLATE'),
    ('#A52A2A', u'CAFE'),
    ('#800000', u'MARRON'),
    ('#FFFFFF', u'BLANCO'),
    ('#F5F5F5', u'BLANCO HUMO'),
    ('#808080', u'GRIS'),
    ('#D3D3D3', u'GRIS CLARO'),
    ('#C0C0C0', u'PLATA'),
    ('#000000', u'NEGRO')
)


class Institucion(models.Model):
    nombre = models.CharField(default='', max_length=300, verbose_name=u'Nombre')
    alias = models.CharField(default='', max_length=30, verbose_name=u'Alias')
    keymap = models.CharField(default='', max_length=300, verbose_name=u'Key Map')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name_plural = u"Institucion"
        db_table = "empresa"
        ordering = ['nombre']
        unique_together = ['alias']

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("Institucion.objects.filter(Q(nombre__contains='%s') | Q(alias__contains='%s') | Q(id=id_search('%s')))" % (q, q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def dato_institucion(self):
        if self.datoinstitucion_set.exists():
            datos = self.datoinstitucion_set.all()[0]
        else:
            datos = DatoInstitucion(institucion=self)
            datos.save()
        return datos

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        self.alias = null_to_text(self.alias, nospaces=True, lower=True)
        super(Institucion, self).save(*args, **kwargs)


class TipoIdentificacion(models.Model):
    nombre = models.CharField(default='', max_length=100, verbose_name=u'Nombre')
    cedula = models.BooleanField(default=False, verbose_name=u'Cedula')
    ruc = models.BooleanField(default=False, verbose_name=u'Ruc')
    pasaporte = models.BooleanField(default=False, verbose_name=u'Pasaporte')
    codigo = models.CharField(default='', max_length=3, verbose_name=u'Codigo')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name_plural = u"TipoIdentificacion"
        ordering = ['nombre']
        db_table = "tipoidentificacion"
        unique_together = ['nombre', ]

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("TipoIdentificacion.objects.filter(Q(nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(TipoIdentificacion, self).save(*args, **kwargs)


class Provincia(models.Model):
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name_plural = u"Provincia"
        ordering = ['nombre']
        db_table = "provincia"
        unique_together = ['nombre', ]

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("Provincia.objects.filter(Q(nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def mis_cantones(self):
        return self.canton_set.all()

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(Provincia, self).save(*args, **kwargs)


class Canton(models.Model):
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia")
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name_plural = u"Canton"
        ordering = ['nombre']
        db_table = "canton"
        unique_together = ['provincia', 'nombre']

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("Canton.objects.filter(Q(nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(Canton, self).save(*args, **kwargs)


class Sucursales(models.Model):
    empresa = models.ForeignKey(Institucion, blank=True, null=True, verbose_name=u"Provincia")
    nombre = models.CharField(default='', max_length=100, verbose_name=u"Nombre")
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia de residencia")
    canton = models.ForeignKey(Canton, blank=True, null=True, verbose_name=u"Cantón de residencia")
    sector = models.CharField(default='', max_length=100, verbose_name=u"Sector")
    direccion = models.CharField(default='', max_length=100, verbose_name=u"Calle principal")


    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name_plural = u"Canton"
        ordering = ['nombre']
        db_table = "sucursal"

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("Sucursal.objects.filter(Q(nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def usando(self):
        return self.empleadosucursal_set.exists()

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        self.direccion = null_to_text(self.direccion)
        super(Sucursales, self).save(*args, **kwargs)


class DatoInstitucion(models.Model):
    institucion = models.ForeignKey(Institucion, verbose_name=u"Regimen educativo")
    ruc = models.CharField(default='', max_length=13, verbose_name=u'RUC')
    telefonofijo = models.CharField(default='', max_length=50, verbose_name=u"Teléfono fijo")
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia de residencia")
    canton = models.ForeignKey(Canton, blank=True, null=True, verbose_name=u"Cantón de residencia")
    sector = models.CharField(default='', max_length=100, verbose_name=u"Sector")
    direccion = models.CharField(default='', max_length=100, verbose_name=u"Calle principal")
    paginaweb = models.CharField(default='', blank=True, max_length=200, verbose_name=u"Página web")
    email = models.CharField(default='', blank=True, max_length=200, verbose_name=u"Página web")
    latitud = models.FloatField(default=0, verbose_name=u"Latitud")
    longitud = models.FloatField(default=0, verbose_name=u"Longitud")
    margenutilidad = models.FloatField(default=0, verbose_name=u"Longitud")
    logo = models.FileField(blank=True, null=True, upload_to='logo/', verbose_name=u"Imagen institucional")

    def __unicode__(self):
        return u'%s' % self.institucion

    class Meta:
        verbose_name_plural = u"DatoInstitucion"
        db_table = "info_empresa"
        unique_together = ['institucion']

    def save(self, *args, **kwargs):
        self.ruc = null_to_text(self.ruc)
        self.telefonofijo = null_to_text(self.telefonofijo)
        self.sector = null_to_text(self.sector)
        self.direccion = null_to_text(self.direccion)
        self.paginaweb = null_to_text(self.paginaweb, lower=True)
        self.email = null_to_text(self.email, lower=True)
        super(DatoInstitucion, self).save(*args, **kwargs)


class Persona(models.Model):
    nombre1 = models.CharField(default='', max_length=50, verbose_name=u'1er Nombre')
    nombre2 = models.CharField(default='', max_length=50, verbose_name=u'2do Nombre')
    apellido1 = models.CharField(default='', max_length=50, verbose_name=u"1er Apellido")
    apellido2 = models.CharField(default='', max_length=50, verbose_name=u"2do Apellido")
    identificacion = models.CharField(default='', max_length=13, verbose_name=u"Identificacion")
    tipoidentificacion = models.ForeignKey(TipoIdentificacion, verbose_name=u'Tipo de indentificacion', blank=True, null=True)
    nacimiento = models.DateField(verbose_name=u"Fecha de nacimiento")
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia de residencia")
    canton = models.ForeignKey(Canton, blank=True, null=True, verbose_name=u"Cantón de residencia")
    sector = models.CharField(default='', max_length=100, verbose_name=u"Sector de residencia")
    direccion = models.CharField(default='', max_length=100, verbose_name=u"Calle principal")
    direccion2 = models.CharField(default='', max_length=100, verbose_name=u"Calle secundaria")
    referencia = models.CharField(default='', max_length=100, verbose_name=u"Referencia")
    numero = models.CharField(default='', max_length=15, verbose_name=u"Numero de domicilio")
    telefonomovil = models.CharField(default='', max_length=50, verbose_name=u"Teléfono movil")
    telefonofijo = models.CharField(default='', max_length=50, verbose_name=u"Teléfono fijo")
    email = models.CharField(default='', max_length=300, verbose_name=u"Correo electrónico")
    usuario = models.ForeignKey(User, null=True, verbose_name=u'Usuario')
    sessiontime = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s %s %s %s' % (self.apellido1, self.apellido2, self.nombre1, self.nombre2)

    class Meta:
        verbose_name_plural = u"Persona"
        db_table = "persona"
        ordering = ['apellido1', 'apellido2', 'nombre1', 'nombre2']

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        qq = q.split(' ')
        if len(qq) >= 2:
            return eval(("Persona.objects.filter(apellido1__contains='%s', apellido2__contains='%s')" % (qq[0], qq[1])) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))
        return eval(("Persona.objects.filter(Q(nombre1__contains='%s') | Q(nombre2__contains='%s') | Q(apellido1__contains='%s') | Q(apellido2__contains='%s') | Q(identificacion__contains='%s') | Q(id=id_search('%s')))" % (q, q, q, q, q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def lista_perfiles(self):
        return TipoPerfilUsuario.objects.filter(perfilusuario__persona=self).distinct()

    def generar_clave_verificacion(self):
        clave = ''
        for i in range(15):
            clave += random.choice('0123456789ABCDEF')
        return clave

    def direccion_completa(self):
        return u"%s %s %s %s %s %s %s" % ((self.provincia.nombre + ",") if self.provincia else "",
                                          (self.sector + ",") if self.sector else "",
                                          (self.direccion + ",") if self.direccion else "",
                                          (self.direccion2 + ",") if self.direccion2 else "",
                                          self.numero)

    def telefonos(self):
        data = []
        if self.telefonofijo:
            data.append(self.telefonofijo)
        if self.telefonomovil:
            data.append(self.telefonomovil)
        return data

    def activo(self):
        return self.usuario.is_active

    def nombre_completo(self):
        return u'%s %s %s %s' % (self.nombre1, self.nombre2, self.apellido1, self.apellido2)

    def nombre_completo_inverso(self):
        return u'%s %s %s %s' % (self.apellido1, self.apellido2, self.nombre1, self.nombre2)

    def nombre_completo_simple(self):
        return u'%s %s' % (self.nombre1, self.apellido1[0] if self.apellido1 else "")

    def nombre_iniciales(self):
        return u"%s" % (self.nombre1[:3])

    def mi_cumpleannos(self):
        hoy = datetime.now().date()
        nacimiento = self.nacimiento
        if nacimiento.day == hoy.day and nacimiento.month == hoy.month:
            return True
        return False

    def edad(self):
        edad = 0
        hoy = datetime.now().date()
        nac = self.nacimiento
        if hoy.year > nac.year:
            try:
                edad = hoy.year - nac.year
                if hoy.month <= nac.month:
                    if hoy.month == nac.month:
                        if hoy.day < nac.day:
                            edad -= 1
                    else:
                        edad -= 1
            except:
                pass
        return edad

    def empleado(self):
        if self.empleado_set.exists():
            return self.empleado_set.all()[0]
        return None

    def notificar_recuperacion_clave(self):
        if self.solicito_cambio_clave():
            recuperacion = self.datos_cambio_clave()
            send_html_mail("Notificación de recuperación de clave del SGC.", "emails/recuperar.html",
                           {'datos': recuperacion}, [self.email], [])

    def notificar_cambio_clave_exitoso(self):
        send_html_mail("Cambio exitoso de contraseña del SGC.", "emails/cambioexitoso.html", {}, [self.email], [])

    def mis_modulos(self, tipo):
        if tipo == 1:
            return Modulo.objects.filter(grupomodulos__grupoinstitucion__perfilgrupoinstitucion__perfilusuario__in=self.mis_perfilesusuarios(), administrativo=True).distinct()
        if tipo == 2:
            return Modulo.objects.filter(grupomodulos__grupoinstitucion__perfilgrupoinstitucion__perfilusuario__in=self.mis_perfilesusuarios(), empleado=True).distinct()

    def save(self, *args, **kwargs):
        self.nombre1 = null_to_text(self.nombre1)
        self.nombre2 = null_to_text(self.nombre2)
        self.apellido1 = null_to_text(self.apellido1)
        self.apellido2 = null_to_text(self.apellido2)
        self.identificacion = null_to_text(self.identificacion)
        self.sector = null_to_text(self.sector)
        self.direccion = null_to_text(self.direccion)
        self.direccion2 = null_to_text(self.direccion2)
        self.referencia = null_to_text(self.referencia)
        self.numero = null_to_text(self.numero)
        self.telefonofijo = null_to_text(self.telefonofijo)
        self.telefonomovil = null_to_text(self.telefonomovil)
        self.email = null_to_text(self.email, lower=True, nospaces=True)
        super(Persona, self).save(*args, **kwargs)


class Proveedor(models.Model):
    razonsocial = models.CharField(default='', max_length=300, verbose_name=u'1er Nombre')
    representante = models.CharField(default='', max_length=50, verbose_name=u'2do Nombre')
    identificacion = models.CharField(default='', max_length=13, verbose_name=u"Identificacion")
    tipoidentificacion = models.ForeignKey(TipoIdentificacion, verbose_name=u'Tipo de indentificacion', blank=True, null=True)
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia de residencia")
    canton = models.ForeignKey(Canton, blank=True, null=True, verbose_name=u"Cantón de residencia")
    sector = models.CharField(default='', max_length=100, verbose_name=u"Sector de residencia")
    direccion = models.CharField(default='', max_length=100, verbose_name=u"Calle principal")
    telefonomovil = models.CharField(default='', max_length=50, verbose_name=u"Teléfono movil")
    telefonofijo = models.CharField(default='', max_length=50, verbose_name=u"Teléfono fijo")
    email = models.CharField(default='', max_length=300, verbose_name=u"Correo electrónico")

    def __unicode__(self):
        return u'%s - %s' % (self.razonsocial, self.representante)

    class Meta:
        verbose_name_plural = u"Proveedor"
        db_table = "proveedor"

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("Proveedor.objects.filter(razonsocial__contains='%s', representante__contains='%s')" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def total_compras(self):
        return self.compraproducto_set.count()

    def save(self, *args, **kwargs):
        self.razonsocial = null_to_text(self.razonsocial)
        self.representante = null_to_text(self.representante)
        self.identificacion = null_to_text(self.identificacion)
        self.sector = null_to_text(self.sector)
        self.direccion = null_to_text(self.direccion)
        self.telefonofijo = null_to_text(self.telefonofijo)
        self.telefonomovil = null_to_text(self.telefonomovil)
        self.email = null_to_text(self.email, lower=True, nospaces=True)
        super(Proveedor, self).save(*args, **kwargs)


class Cliente(models.Model):
    nombres = models.CharField(default='', max_length=300, verbose_name=u'1er Nombre')
    apellidos = models.CharField(default='', max_length=50, verbose_name=u'2do Nombre')
    identificacion = models.CharField(default='', max_length=13, verbose_name=u"Identificacion")
    tipoidentificacion = models.ForeignKey(TipoIdentificacion, verbose_name=u'Tipo de indentificacion', blank=True, null=True)
    provincia = models.ForeignKey(Provincia, blank=True, null=True, verbose_name=u"Provincia de residencia")
    canton = models.ForeignKey(Canton, blank=True, null=True, verbose_name=u"Cantón de residencia")
    sector = models.CharField(default='', max_length=100, verbose_name=u"Sector de residencia")
    direccion = models.CharField(default='', max_length=100, verbose_name=u"Calle principal")
    telefonomovil = models.CharField(default='', max_length=50, verbose_name=u"Teléfono movil")
    telefonofijo = models.CharField(default='', max_length=50, verbose_name=u"Teléfono fijo")
    email = models.CharField(default='', max_length=300, verbose_name=u"Correo electrónico")

    def __unicode__(self):
        return u'%s  %s' % (self.nombres, self.apellidos)

    class Meta:
        verbose_name_plural = u"Clientes"
        db_table = "cliente"

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("Proveedor.objects.filter(nombres__contains='%s', apellidos__contains='%s')" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def total_ventas(self):
        return self.factura_set.count()

    def valor_ventas(self):
        valor = self.factura_set.filter(valida=True).distinct().aggregate(suma=Sum('total'))['suma']
        if valor:
            return valor
        return 0

    def save(self, *args, **kwargs):
        self.nombres = null_to_text(self.nombres)
        self.apellidos = null_to_text(self.apellidos)
        self.identificacion = null_to_text(self.identificacion)
        self.sector = null_to_text(self.sector)
        self.direccion = null_to_text(self.direccion)
        self.telefonofijo = null_to_text(self.telefonofijo)
        self.telefonomovil = null_to_text(self.telefonomovil)
        self.email = null_to_text(self.email, lower=True, nospaces=True)
        super(Cliente, self).save(*args, **kwargs)


class IvaAplicado(models.Model):
    nombre = models.CharField(max_length=300, verbose_name=u'Nombre')
    porciento = models.FloatField(default=0, verbose_name=u'Porciento')
    codigo = models.IntegerField(default=0, verbose_name=u'Codigo')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name_plural = u"IvaAplicado"
        ordering = ['porciento']
        db_table = "datos_iva"
        unique_together = ['nombre', ]

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("IvaAplicado.objects.filter(Q(nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(IvaAplicado, self).save(*args, **kwargs)


class Empleado(models.Model):
    persona = models.ForeignKey(Persona)
    sueldo = models.FloatField(default=0)
    cargo = models.CharField(default='', max_length=300, verbose_name=u"Correo electrónico")
    email = models.CharField(default='', max_length=300, verbose_name=u"Correo electrónico")
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s' % self.persona

    class Meta:
        verbose_name_plural = u"Empleado"
        db_table = "empleados"
        ordering = ['persona__apellido1', 'persona__apellido2', 'persona__nombre1', 'persona__nombre2']
        unique_together = ['persona']

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        qq = q.split(' ')
        if len(qq) >= 2:
            return eval(("Empleado.objects.filter(persona__apellido1__contains='%s', persona__apellido2__contains='%s')" % (qq[0], qq[1])) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))
        return eval(("Empleado.objects.filter(Q(persona__nombre1__contains='%s') | Q(persona__nombre2__contains='%s') | Q(persona__apellido1__contains='%s') | Q(persona__apellido2__contains='%s') | Q(persona__identificacion__contains='%s') | Q(id=id_search('%s')))" % (q, q, q, q, q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def mi_perfil(self):
        return self.perfilusuario_set.all()[0]

    def tiene_permiso(self, modulo):
        return GrupoModulos.objects.filter(perfil=self.mi_perfil(), modulo__id=modulo)

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def persona_user(self, usuario):
        return Persona.objects.get(usuario=usuario)

    def save(self, *args, **kwargs):
        self.cargo = null_to_text(self.cargo)
        super(Empleado, self).save(*args, **kwargs)


class TipoPerfilUsuario(models.Model):
    nombre = models.CharField(max_length=300, verbose_name=u'Nombre')

    def __unicode__(self):
        return u'%s ' % self.nombre

    class Meta:
        verbose_name_plural = u"TipoPerfilUsuario"
        ordering = ['nombre']
        db_table = "tipoempleado"
        unique_together = ['nombre']

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("TipoPerfilUsuario.objects.filter(Q(nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.__unicode__()

    def flexbox_alias(self):
        return [self.id, self.flexbox_repr()]

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(TipoPerfilUsuario, self).save(*args, **kwargs)


class PerfilUsuario(models.Model):
    tipoperfilusuario = models.ForeignKey(TipoPerfilUsuario, blank=True, null=True, verbose_name=u'Tipo Perfil Usuario')
    empleado = models.ForeignKey(Empleado, blank=True, null=True, verbose_name=u'Empleado')
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s' % self.tipoperfilusuario

    class Meta:
        ordering = ['empleado', ]
        db_table = "empleado_tipo"


class EmpleadoSucursal(models.Model):
    sucursal = models.ForeignKey(Sucursales, blank=True, null=True, verbose_name=u'Tipo Perfil Usuario')
    empleado = models.ForeignKey(Empleado, blank=True, null=True, verbose_name=u'Empleado')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "empleado_sucursal"


class Modulo(models.Model):
    nombre = models.CharField(default='', max_length=50, verbose_name=u'Nombre')
    descripcion = models.CharField(default='', max_length=150, verbose_name=u'Descripcion')

    def __unicode__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name_plural = u"Modulos"
        ordering = ['nombre']
        db_table = "lista_modulos"
        unique_together = ['nombre']

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("Modulo.objects.filter(Q(nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return self.nombre + ' - ' + str(self.id)

    def flexbox_alias(self):
        return [self.id, self.nombre]


class GrupoModulos(models.Model):
    perfil = models.ForeignKey(PerfilUsuario, blank=True, null=True, verbose_name=u'Grupo de usuarios')
    modulo = models.ForeignKey(Modulo, verbose_name=u'Modulo')
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s' % self.perfil.empleado

    class Meta:
        verbose_name_plural = u"GrupoModulos"
        db_table = "acceso_perfil"
        unique_together = ['perfil', 'modulo']
        ordering = ['perfil', 'modulo']


class LineaProducto(models.Model):
    nombre = models.CharField(default='', max_length=50, verbose_name=u'Nombre')

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = u"LineaProducto"
        db_table = "tipo_producto"

    def en_uso(self):
        return self.producto_set.exists()

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(LineaProducto, self).save(*args, **kwargs)


class TipoServicio(models.Model):
    nombre = models.CharField(default='', max_length=50, verbose_name=u'Nombre')

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = u"LineaProducto"
        db_table = "TipoServicio"

    def en_uso(self):
        return self.producto_set.exists()

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(TipoServicio, self).save(*args, **kwargs)


class Marca(models.Model):
    nombre = models.CharField(default='', max_length=50, verbose_name=u'Nombre')

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = u"Marca"
        db_table = "marca"

    def en_uso(self):
        return self.producto_set.exists()

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(Marca, self).save(*args, **kwargs)


class Presentacion(models.Model):
    nombre = models.CharField(default='', max_length=50, verbose_name=u'Nombre')

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = u"Marca"
        db_table = "Presentacion"

    def en_uso(self):
        return self.producto_set.exists()

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        super(Presentacion, self).save(*args, **kwargs)


class Producto(models.Model):
    nombre = models.CharField(default='', max_length=50, verbose_name=u'Nombre')
    color = models.CharField(default='', max_length=50, verbose_name=u'Nombre')
    detalles = models.CharField(default='', max_length=3000, verbose_name=u'Nombre')
    linea = models.ForeignKey(LineaProducto, blank=True, null=True, verbose_name=u'TipoInsumoMaterial')
    presentacion = models.ForeignKey(Presentacion, blank=True, null=True, verbose_name=u'TipoInsumoMaterial')
    tiposervicio = models.ForeignKey(TipoServicio, blank=True, null=True, verbose_name=u'TipoInsumoMaterial')
    marca = models.ForeignKey(Marca, verbose_name=u'UnidadMedida', blank=True, null=True)
    servicio = models.BooleanField(default=False)
    costo = models.FloatField(default=0)

    def representacion(self):
        if not self.servicio:
            return self.linea.nombre + " - " + self.nombre + " - " + self.presentacion.nombre
        else:
            return self.tiposervicio.nombre + " - " + self.nombre + " - " + str(self.costo)

    def __unicode__(self):
        return self.representacion()

    class Meta:
        verbose_name_plural = u"Producto"
        db_table = "articulo"
        ordering = ('nombre',)

    def mi_inventario(self):
        if self.inventario_set.exists():
            i = self.inventario_set.all()[0]
        else:
            i = Inventario(articulo=self)
            i.save()
        return i

    def mi_inventario_sucursal(self, sucursal):
        if self.inventario_set.filter(sucursal=sucursal).exists():
            i = self.inventario_set.filter(sucursal=sucursal)[0]
        else:
            i = Inventario(articulo=self, sucursal=sucursal)
            i.save()
        return i

    def stock_sucursal(self, sucursal):
        return null_to_numeric(self.inventario_set.filter(sucursal=sucursal).aggregate(valor=Sum('cantidad'))['valor'], 2)

    def stock_total(self):
        return null_to_numeric(self.inventario_set.aggregate(valor=Sum('cantidad'))['valor'], 2)

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        self.color = null_to_text(self.color)
        self.detalles = null_to_text(self.detalles)
        super(Producto, self).save(*args, **kwargs)


class Inventario(models.Model):
    sucursal = models.ForeignKey(Sucursales, blank=True, null=True, verbose_name=u'Tipo Perfil Usuario')
    articulo = models.ForeignKey(Producto)
    cantidad = models.FloatField(default=0)
    costo = models.FloatField(default=0, verbose_name=u'Costo')
    precioventa = models.FloatField(default=0, verbose_name=u'Costo')
    valor = models.FloatField(default=0, verbose_name=u'Valor')

    def __unicode__(self):
        return unicode(self.articulo.nombre) + ' - Cant: ' + str(self.cantidad) + ' - Cu: $' + str(self.costo)

    class Meta:
        verbose_name = u'Inventario'
        verbose_name_plural = u'Inventarios'
        db_table = "inventario"
        ordering = ('articulo__id',)

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("InventarioInsumo.objects.filter(Q(articulo__nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return "%s" % (self.articulo.nombre)

    def flexbox_alias(self):
        return [str(self.id), self.articulo.nombre, self.articulo.linea.id, self.articulo.marca.id, str(self.costo)]


class KardexInventario(models.Model):
    ingreso = models.BooleanField(default=True)
    inventario = models.ForeignKey(Inventario)
    fechaingreso = models.DateTimeField()
    cantidad = models.FloatField(default=0)
    costo = models.FloatField(default=0, verbose_name=u'Costo')
    valor = models.FloatField(default=0, verbose_name=u'Valor')
    precioventa = models.FloatField(default=0, verbose_name=u'Costo')
    disponible = models.FloatField(default=0)

    def __unicode__(self):
        return unicode(self.inventario.articulo.representacion()) + ' - Disp: ' + str(self.disponible) + ' - Cu: $' + str(self.precioventa)

    class Meta:
        verbose_name = u'Inventario'
        verbose_name_plural = u'Inventarios'
        db_table = "kardex"
        ordering = ('inventario__id',)

    @staticmethod
    def flexbox_query(q, filtro=None, exclude=None, cantidad=None):
        return eval(("KardexInventario.objects.filter(Q(inventario__articulo__nombre__contains='%s') | Q(inventario__articulo__linea__nombre__contains='%s') | Q(id=id_search('%s')))" % (q, q, q)) + (".filter(%s)" % filtro if filtro else "") + (".exclude(%s)" % exclude if exclude else "") + ".distinct()" + ("[:%s]" % cantidad if cantidad else ""))

    def flexbox_repr(self):
        return "%s" % (self.inventario.articulo.nombre)

    def flexbox_alias(self):
        return [str(self.id), self.inventario.articulo.nombre, self.inventario.articulo.linea.id, self.inventario.articulo.marca.id, str(self.costo)]


class Detallecompra(models.Model):
    articulo = models.ForeignKey(Producto, blank=True, null=True)
    cantidad = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)
    costo = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __unicode__(self):
        return unicode(self.articulo.nombre) + ' - Cant: ' + str(self.cantidad) + ' - Cu: $' + str(self.costo)

    class Meta:
        verbose_name = u'Detalle Ingreso insumo'
        verbose_name_plural = u'Detalles Ingreso de insumos'
        db_table = "lista_compra"
        ordering = ('articulo',)

    def calcular_valor(self):
        return round(self.cantidad * self.costo, 2)


MESES_LISTADO = (
    (1, u'ENERO'),
    (2, u'FEBRERO'),
    (3, u'MARZO'),
    (4, u'ABRIL'),
    (5, u'MAYO'),
    (6, u'JUNIO'),
    (7, u'JULIO'),
    (8, u'AGOSTO'),
    (9, u'SEPTIEMBRE'),
    (10, u'OCTUBRE'),
    (11, u'NOVIEMBRE'),
    (12, u'DICIEMBRE')
)

ANIO_LISTADO = (
    (2018, u'2018'),
    (2019, u'2019'),
    (2020, u'2020'),
    (2021, u'2021'),
    (2022, u'2022'),
    (2023, u'2023'),
    (2024, u'2024'),
    (2025, u'2025')
)

class AnioFiscal(models.Model):
    anio = models.IntegerField(default=datetime.now().year)

    def __unicode__(self):
        return str(self.anio)

    class Meta:
        verbose_name = u"Anio"
        verbose_name_plural = u"Anio"
        db_table = "anio_fiscal"
        ordering = ('-anio',)


class PresupuestoCompra(models.Model):
    valor = models.FloatField(default=0)
    anio = models.IntegerField(default=int(datetime.now().year))
    fechai = models.DateField()
    fechaf = models.DateField(blank=True, null=True)
    mes = models.IntegerField(choices=MESES_LISTADO)
    activo = models.BooleanField(default=True)
    permiteexceder = models.BooleanField(default=False)

    def repr_id(self):
        return str(self.id).zfill(4)

    def valor_compras(self):
        if self.compraproducto_set.exists():
            return round(self.compraproducto_set.aggregate(valor=Sum('valor'))['valor'], 2)
        return 0

    def saldo(self):
        vc = self.valor_compras()
        return self.valor - vc

    def total_compras(self):
        return self.compraproducto_set.count()


class CompraProducto(models.Model):
    proveedor = models.ForeignKey(Proveedor, blank=True, null=True)
    sucursal = models.ForeignKey(Sucursales, blank=True, null=True)
    presupuesto = models.ForeignKey(PresupuestoCompra, blank=True, null=True)
    numerodocumento = models.CharField(max_length=20, blank=True, null=True)
    fecha = models.DateField()
    usuario = models.ForeignKey(User, blank=True, null=True)
    productos = models.ManyToManyField(Detallecompra)
    finalizada = models.BooleanField(default=False)
    credito = models.BooleanField(default=False)
    meses = models.IntegerField(default=0)
    subtotal = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __unicode__(self):
        return self.numerodocumento + " - " + self.proveedor.razonsocial

    class Meta:
        verbose_name = u'Ingreso de Insumos '
        verbose_name_plural = u'Ingreso de Insumos'
        db_table = "compras"
        ordering = ('-fecha',)

    def genera_cuota(self):
        from funciones import proximafecha
        valor = self.valor
        vc = null_to_numeric(valor / self.meses, 2)
        fecha = datetime.now().date()
        fechavence = fecha + timedelta(days=1)
        self.cuotascompras_set.all().delete()
        for i in range(1, int(self.meses) + 1):
            cuota = CuotasCompras(compra=self,
                                  cuota=i,
                                  valor=vc,
                                  fechalimite=fechavence)
            cuota.save()
            fechavence = proximafecha(fechavence, 3).date()
        valorc = null_to_numeric(self.cuotascompras_set.aggregate(valor=Sum('valor'))['valor'], 2)
        ultima = self.cuotascompras_set.all().order_by('-cuota')[0]
        faltante = 0
        excddente = 0
        if valor > valorc:
            faltante = valor - valorc
            ultima.valor += faltante
            ultima.save()
        elif valorc > valor:
            excedente = valorc - valor
            ultima.valor -= excedente
            ultima.save()

    def total_ingreso(self):
        return self.productos.all().aggregate(Sum('valor'))['valor__sum']

    def repr_id(self):
        return str(self.id).zfill(4)

    def cantidad_productos(self):
        return self.productos.all().count()

    def valor_compra(self):
        valor = self.productos.aggregate(suma=Sum('valor'))['suma']
        if valor:
            return valor
        return 0

    def subtotal_compra(self):
        valor = self.productos.aggregate(suma=Sum('subtotal'))['suma']
        if valor:
            return valor
        return 0

    def iva_compra(self):
        valor = self.productos.aggregate(suma=Sum('iva'))['suma']
        if valor:
            return valor
        return 0

    def actualiza_valor(self):
        self.subtotal = self.subtotal_compra()
        self.iva = self.iva_compra()
        self.valor = self.valor_compra()
        self.save()

    def cuotas(self):
        return self.cuotascompras_set.count()

    def vencidas(self):
        return self.cuotascompras_set.filter(fechalimite__lt=datetime.now().date(), pagada=False).count()

    def saldo(self):
        return self.valor - null_to_numeric(self.cuotascompras_set.filter(pagada=True).aggregate(valor=Sum('valor'))['valor'], 2)


class DevolucionCompraProducto(models.Model):
    compra = models.ForeignKey(CompraProducto, blank=True, null=True)
    motivo = models.TextField(max_length=20, blank=True, null=True)
    fecha = models.DateField()
    usuario = models.ForeignKey(User, blank=True, null=True)
    productos = models.ManyToManyField(Detallecompra)
    valor = models.FloatField(default=0)

    def __unicode__(self):
        return self.motivo

    class Meta:
        verbose_name = u'Ingreso de Insumos '
        verbose_name_plural = u'Ingreso de Insumos'
        db_table = "devolucion_compras"
        ordering = ('fecha',)


class DetalleDevolucion(models.Model):
    devolucion = models.ForeignKey(DevolucionCompraProducto, blank=True, null=True)
    detalle = models.ForeignKey(Detallecompra, blank=True, null=True)
    cantidad = models.FloatField(default=0)
    costo = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __unicode__(self):
        return unicode(self.detalle.articulo.nombre) + ' - Cant: ' + str(self.cantidad) + ' - Cu: $' + str(self.costo)

    class Meta:
        verbose_name = u'Detalle Ingreso insumo'
        verbose_name_plural = u'Detalles Ingreso de insumos'
        db_table = "detalle_devolucion"
        ordering = ('detalle__articulo',)

    def calcular_valor(self):
        return round(self.cantidad * self.costo, 2)



class ContratoEmpleado(models.Model):
    empleado = models.ForeignKey(Empleado)
    fechadesde = models.DateField()
    fechahasta = models.DateField()
    activo = models.BooleanField(default=True)
    observaciones = models.TextField()

    class Meta:
        verbose_name = u"ContratoEmpleado"
        verbose_name_plural = u"ContratoEmpleado"
        db_table = "ContratoEmpleado"


class Asistencia(models.Model):
    anio = models.ForeignKey(AnioFiscal)
    mes = models.IntegerField(choices=MESES_LISTADO)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = u"Asistencia"
        verbose_name_plural = u"Asistencia"
        db_table = "asistencia"
        ordering = ('-mes',)


class RegistroAsistencia(models.Model):
    asistencia = models.ForeignKey(Asistencia)
    fecha = models.DateField()
    observaciones = models.TextField()

    def __unicode__(self):
        return str(self.asistencia.anio)

    class Meta:
        verbose_name = u"RegistroAsistencia"
        verbose_name_plural = u"registroasistencia"
        db_table = "registro_asistencia"
        ordering = ('-fecha',)


class DetalleAsistencia(models.Model):
    empleado = models.ForeignKey(Empleado)
    registroasistencia = models.ForeignKey(RegistroAsistencia)
    asistio = models.BooleanField(default=False)
    falto = models.BooleanField(default=False)
    justificado = models.BooleanField(default=False)
    motivo = models.TextField()
    archivo = models.FileField(blank=True, null=True, upload_to='justificaciones/', verbose_name=u"Imagen institucional")


class DetalleFactura(models.Model):
    producto = models.ForeignKey(Producto, blank=True, null=True)
    cantidad = models.FloatField(default=0)
    precio = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    descuento = models.FloatField(default=0)
    valoriva = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __unicode__(self):
        return "%s" % (self.cantidad)

    class Meta:
        verbose_name = u"Detalle Factura"
        verbose_name_plural = u"Detalles Facturas"
        db_table = "detalle_factura"

    def calcular_valor(self):
        return round(self.cantidad * self.precio, 2)


class Factura(models.Model):
    cliente = models.ForeignKey(Cliente, blank=True, null=True)
    empleado = models.ForeignKey(Empleado, blank=True, null=True)
    sucursal = models.ForeignKey(Sucursales, blank=True, null=True)
    numero = models.CharField(max_length=50)
    numeroreal = models.IntegerField(default=0)
    fecha = models.DateField()
    subtotal = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    descuento = models.FloatField(default=0)
    total = models.FloatField(default=0)
    detalles = models.ManyToManyField(DetalleFactura)
    pagado = models.FloatField(default=0)
    cancelada = models.BooleanField(default=False)
    valida = models.BooleanField(default=True)
    finalizada = models.BooleanField(default=False)
    credito = models.BooleanField(default=False)
    meses = models.FloatField(default=0)
    porcentaje = models.FloatField(default=0)
    recargo = models.FloatField(default=0)

    def __unicode__(self):
        return "%s - %s" % (self.numero, self.cliente)

    class Meta:
        verbose_name = u"Factura"
        verbose_name_plural = u"Facturas"
        db_table = "factura"
        ordering = ('numero', 'cliente')

    def repr_id(self):
        return '001-001-' + str(self.id).zfill(9)

    def repr_numero(self):
        return '001-001-' + str(self.numeroreal).zfill(9)

    def saldo_pendiente(self):
        return self.total - self.pagado

    def esta_cancelada(self):
        return self.saldo_pendiente() == 0

    def cantidad_productos(self):
        return self.detalles.all().count()

    def actualiza_numero(self):
        self.numero = self.repr_numero()
        self.save()

    def valor_compra(self):
        if self.credito:
            recargo = null_to_numeric((self.subtotal * self.porcentaje) / 100, 2)
        else:
            recargo = 0
        self.recargo = recargo
        valor = self.detalles.aggregate(suma=Sum('valor'))['suma']
        if valor:
            return valor + self.recargo
        return 0

    def subtotal_compra(self):
        valor = self.detalles.aggregate(suma=Sum('subtotal'))['suma']
        if valor:
            return valor
        return 0

    def iva_compra(self):
        valor = self.detalles.aggregate(suma=Sum('iva'))['suma']
        if valor:
            return valor
        return 0

    def descuento_compra(self):
        valor = self.detalles.aggregate(suma=Sum('descuento'))['suma']
        if valor:
            return valor
        return 0

    def cuotas(self):
        return self.cuotasfacturas_set.count()

    def vencidas(self):
        return self.cuotasfacturas_set.filter(fechalimite__lt=datetime.now().date(), pagada=False).count()

    def saldo(self):
        return self.total - null_to_numeric(self.cuotasfacturas_set.filter(pagada=True).aggregate(valor=Sum('valor'))['valor'], 2)

    def genera_cuota(self):
        from funciones import proximafecha
        valor = self.total
        vc = null_to_numeric(valor / self.meses, 2)
        fecha = datetime.now().date()
        fechavence = fecha + timedelta(days=1)
        for i in range(1, int(self.meses) + 1):
            cuota = CuotasFacturas(factura=self,
                                   cuota=i,
                                   valor=vc,
                                   fechalimite=fechavence)
            cuota.save()
            fechavence = proximafecha(fechavence, 3).date()
        valorc = null_to_numeric(self.cuotasfacturas_set.aggregate(valor=Sum('valor'))['valor'], 2)
        ultima = self.cuotasfacturas_set.all().order_by('-cuota')[0]
        faltante = 0
        excddente = 0
        if valor > valorc:
            faltante = valor - valorc
            ultima.valor += faltante
            ultima.save()
        elif valorc > valor:
            excedente = valorc - valor
            ultima.valor -= excedente
            ultima.save()

    def actualiza_valor(self):
        self.subtotal = self.subtotal_compra()
        self.iva = self.iva_compra()
        self.total = self.valor_compra()
        self.descuento = self.descuento_compra()
        self.save()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.cancelada = self.esta_cancelada()
        super(Factura, self).save(force_insert, force_update, using)


class DevolucionFactura(models.Model):
    factura = models.ForeignKey(Factura, blank=True, null=True)
    motivo = models.TextField(max_length=20, blank=True, null=True)
    fecha = models.DateField()
    usuario = models.ForeignKey(User, blank=True, null=True)
    productos = models.ManyToManyField(DetalleFactura)
    valor = models.FloatField(default=0)

    def __unicode__(self):
        return self.motivo

    class Meta:
        verbose_name = u'Ingreso de Insumos '
        verbose_name_plural = u'Ingreso de Insumos'
        db_table = "devolucion_factura"
        ordering = ('fecha',)


class DetalleDevolucionFactura(models.Model):
    devolucion = models.ForeignKey(DevolucionFactura, blank=True, null=True)
    detalle = models.ForeignKey(DetalleFactura, blank=True, null=True)
    cantidad = models.FloatField(default=0)
    costo = models.FloatField(default=0)
    iva = models.FloatField(default=0)
    valor = models.FloatField(default=0)

    def __unicode__(self):
        return unicode(self.detalle.producto.nombre) + ' - Cant: ' + str(self.cantidad) + ' - Cu: $' + str(self.costo)

    class Meta:
        verbose_name = u'Detalle Ingreso insumo'
        verbose_name_plural = u'Detalles Ingreso de insumos'
        db_table = "detalle_devolucion_factura"
        ordering = ('detalle__producto',)

    def calcular_valor(self):
        return round(self.cantidad * self.costo, 2)


class Gastos(models.Model):
    fecha = models.DateField()
    sueldo = models.BooleanField(default=True)
    descripcion = models.CharField(default='', max_length=300)
    finalizado = models.BooleanField(default=False)
    total = models.FloatField(default=0)

    def __unicode__(self):
        return "%s " % (str(self.fecha))

    class Meta:
        verbose_name = u"Gastos"
        verbose_name_plural = u"Gastos"
        db_table = "gastos"
        ordering = ('fecha', )

    def repr_id(self):
        return '001-001-' + str(self.id).zfill(9)

    def get_mes(self):
        mes = int(self.fecha.month)
        return MESES_LISTADO[mes - 1][1]

    def valor_compra(self):
        valor = self.detallegastos_set.aggregate(suma=Sum('total'))['suma']
        if valor:
            return valor
        return 0

    def mis_detalles(self):
        return self.detallegastos_set.all()

    def actualiza_total(self):
        self.total = self.valor_compra()
        self.save()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.descripcion = null_to_text(self.descripcion)
        super(Gastos, self).save(force_insert, force_update, using)



class DetalleGastos(models.Model):
    gasto = models.ForeignKey(Gastos, blank=True, null=True)
    empleado = models.ForeignKey(Empleado, blank=True, null=True)
    adicional = models.FloatField(default=0)
    descuento = models.FloatField(default=0)
    total = models.FloatField(default=0)

    class Meta:
        verbose_name = u"DetalleGastos"
        verbose_name_plural = u"DetalleGastos"
        db_table = "detalle_gasto"
        ordering = ('empleado', )

    def actualiza_total(self):
        base = self.empleado.sueldo
        total = base + self.adicional - self.descuento
        return total

    def save(self, *args, **kwargs):
        self.total = self.actualiza_total()
        super(DetalleGastos, self).save(*args, **kwargs)


class Traspasos(models.Model):
    fecha = models.DateField()
    origen = models.ForeignKey(Sucursales, related_name="+", blank=True, null=True)
    destino = models.ForeignKey(Sucursales, related_name="+", blank=True, null=True)
    producto  = models.ForeignKey(Producto,  blank=True, null=True)
    motivo = models.TextField(default='')
    cantidad = models.FloatField(default=0)

    class Meta:
        verbose_name = u"DetalleGastos"
        verbose_name_plural = u"DetalleGastos"
        db_table = "Traspasos"


class CuotasFacturas(models.Model):
    factura = models.ForeignKey(Factura, blank=True, null=True)
    cuota = models.IntegerField(default=0)
    valor = models.FloatField(default=0)
    adicional = models.FloatField(default=0)
    descuento = models.FloatField(default=0)
    total = models.FloatField(default=0)
    fechalimite = models.DateField()
    pagada = models.BooleanField(False)
    
    def vencida(self):
        if not self.pagada:
            if self.fechalimite < datetime.now().date():
                return True
        return False

    class Meta:
        verbose_name = u"DetalleGastos"
        verbose_name_plural = u"DetalleGastos"
        db_table = "CuotasFacturas"


class CuotasCompras(models.Model):
    compra = models.ForeignKey(CompraProducto, blank=True, null=True)
    cuota = models.IntegerField(default=0)
    valor = models.FloatField(default=0)
    adicional = models.FloatField(default=0)
    descuento = models.FloatField(default=0)
    total = models.FloatField(default=0)
    fechalimite = models.DateField()
    pagada = models.BooleanField(False)

    class Meta:
        verbose_name = u"DetalleGastos"
        verbose_name_plural = u"DetalleGastos"
        db_table = "CuotasCompras"

    def vencida(self):
        if not self.pagada:
            if self.fechalimite < datetime.now().date():
                return True
        return False

    def actualiza_valor(self):
        return null_to_numeric(self.valor + self.adicional - self.descuento)

    def save(self, *args, **kwargs):
        self.total = self.actualiza_valor()
        super(CuotasCompras, self).save(*args, **kwargs)


class ManualProcedimientos(models.Model):
    nombre = models.TextField()
    fecha = models.DateField()
    detalles = models.TextField()
    archivo = models.FileField(blank=True, null=True, upload_to='documentos/', verbose_name=u"Imagen institucional")


    class Meta:
        verbose_name = u"DetalleGastos"
        verbose_name_plural = u"DetalleGastos"
        db_table = "manual_procedimientos"

    def save(self, *args, **kwargs):
        self.nombre = null_to_text(self.nombre)
        self.detalles = null_to_text(self.detalles)
        super(ManualProcedimientos, self).save(*args, **kwargs)


class Promocion(models.Model):
    observaciones = models.TextField()
    imagen = models.FileField(blank=True, null=True, upload_to='promociones/', verbose_name=u"Imagen institucional")
    fechadesde = models.DateField()
    fechahasta = models.DateField()
    activa = models.BooleanField(default=True)

    def __unicode__(self):
        return self.observaciones

    class Meta:
        verbose_name = u"RegistroAsistencia"
        verbose_name_plural = u"registroasistencia"
        db_table = "promocion"
        ordering = ('-fechadesde',)

    def save(self, *args, **kwargs):
        self.observaciones = null_to_text(self.observaciones)
        super(Promocion, self).save(*args, **kwargs)