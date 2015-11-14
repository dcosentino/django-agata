# -*- coding: utf-8 -*-

from django.contrib import admin


def save_with_date_and_owner(self, request, obj, form, change):
    if not change:
        obj.owner = request.user
        obj.save()
    else:
        if request.user.is_superuser or obj.owner == request.user:
            obj.save()
        else:
            raise PermissionDenied("Non sei il proprietario di questo oggetto, quindi non puoi modificarlo")

class WithDateAndOwnerAdmin_show(admin.ModelAdmin):
    exclude = ('owner',)
    raw_id_fields = ['owner']
    def save_model(self, request, obj, form, change):
        save_with_date_and_owner(self, request, obj, form, change)

    def delete_model(self, request, obj):
        if request.user.is_superuser or obj.owner == request.user:
            obj.delete()
        else:
            raise Exception("Non sei il proprietario di questo oggetto, quindi non puoi eliminarlo")

class WithDateAndOwnerAdmin(WithDateAndOwnerAdmin_show):
    #se non sei superutente vedi solo le cose tue
    def queryset(self, request):
        if not request.user.is_superuser:
            return super(WithDateAndOwnerAdmin,self).queryset(request).filter(owner=request.user)
        else:
            return super(WithDateAndOwnerAdmin,self).queryset(request)



class WithDateAndOwnerAdminStackedInline(admin.StackedInline):
    def save_model(self, request, obj, form, change):
        save_with_date_and_owner(self, request, obj, form, change)


class WithDateAndOwnerAdminTabularInline(admin.TabularInline):
    raw_id_fields = ['owner']
    def save_model(self, request, obj, form, change):
        save_with_date_and_owner(self, request, obj, form, change)
