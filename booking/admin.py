from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Appointment, StoreConfig

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'client_name', 'client_last_name', 'phone', 'status', 'whatsapp_link')
    list_filter = ('status', 'date')
    search_fields = ('client_name', 'client_last_name', 'phone')
    date_hierarchy = 'date'
    list_editable = ('status',)

    def whatsapp_link(self, obj):
        if not obj.phone:
            return "-"
        
        # Generar el path de gestión
        path = reverse('manage_appointment', args=[obj.token])
        
        # Mensaje base
        mensaje_base = f"Hola {obj.client_name}, te escribo para confirmar tu turno del día {obj.date.strftime('%d/%m/%Y')} a las {obj.time.strftime('%H:%M')} hs. Puedes gestionarlo o cancelarlo aquí: "
        
        # Limpiar telefono
        telefono = obj.phone.replace(" ", "").replace("-", "").replace("+", "")
        
        # Botón con JS para capturar el dominio actual dinámicamente
        return format_html(
            '<a href="javascript:void(0)" onclick="const msg = \'{}\' + window.location.origin + \'{}\'; window.open(\'https://wa.me/{}?text=\' + encodeURIComponent(msg), \'_blank\')" style="background-color:#25D366; color:white; padding:4px 8px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:10px;">✉️ WhatsApp</a>',
            mensaje_base, path, telefono
        )
    
    whatsapp_link.short_description = 'Contactar'
@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'open_time', 'close_time', 'interval_minutes')

    def has_add_permission(self, request):
        # We only want one configuration globally
        if self.model.objects.count() > 0:
            return False
        return super().has_add_permission(request)
