# coding=utf-8
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib.auth.models import Permission

from settings import MANAGERS

from app.models import *

class ModeloBaseTabularAdmin(admin.TabularInline):
    exclude = ("usuario_creacion", "fecha_creacion", "usuario_modificacion", "fecha_modificacion")


class ModeloBaseAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super(ModeloBaseAdmin, self).get_actions(request)
        if request.user.username not in [x[0] for x in MANAGERS]:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return request.user.username in [x[0] for x in MANAGERS]

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.username in [x[0] for x in MANAGERS]

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("usuario_creacion", "fecha_creacion", "usuario_modificacion", "fecha_modificacion", "status")
        form = super(ModeloBaseAdmin, self).get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if request.user.username not in [x[0] for x in MANAGERS]:
            raise Exception('Sin permiso a modificacion.')
        else:
            obj.save(request)


admin.site.register(Provincia, ModeloBaseAdmin)
admin.site.register(Canton, ModeloBaseAdmin)
admin.site.register(Institucion, ModeloBaseAdmin)
admin.site.register(PerfilUsuario, ModeloBaseAdmin)
admin.site.register(GrupoModulos, ModeloBaseAdmin)
admin.site.register(Modulo, ModeloBaseAdmin)
admin.site.register(DatoInstitucion, ModeloBaseAdmin)


