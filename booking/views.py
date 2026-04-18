import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from .models import Appointment, StoreConfig

def get_config():
    config = StoreConfig.objects.first()
    if not config:
        config = StoreConfig.objects.create()
    return config

def booking_wizard(request, token=None):
    appointment = None
    if token:
        appointment = get_object_or_404(Appointment, token=token)

    if request.method == 'POST':
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        client_name = request.POST.get('client_name')
        client_last_name = request.POST.get('client_last_name')
        phone = request.POST.get('phone')

        try:
            date_obj = parse_date(date_str)
            time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
            
            if appointment:
                # Update existing
                appointment.date = date_obj
                appointment.time = time_obj
                appointment.client_name = client_name
                appointment.client_last_name = client_last_name
                appointment.phone = phone
                appointment.status = 'pending' # Reset status if it was cancelled
                appointment.save()
            else:
                # Create new
                appointment = Appointment.objects.create(
                    date=date_obj,
                    time=time_obj,
                    client_name=client_name,
                    client_last_name=client_last_name,
                    phone=phone
                )
            return redirect('booking_success_with_token', token=appointment.token)
        except Exception as e:
            return HttpResponse(f"Error procesando turno: {str(e)}", status=400)

    # For GET request, render the main page
    today = datetime.date.today()
    days = []
    for i in range(30):
        d = today + datetime.timedelta(days=i)
        if d.weekday() != 6: # No domingos
            days.append(d)

    return render(request, 'booking/booking_wizard.html', {
        'days': days,
        'appointment': appointment
    })

def get_available_times(request, date_str):
    try:
        selected_date = parse_date(date_str)
    except:
        return HttpResponse("Fecha inválida", status=400)

    config = get_config()
    
    # Obtener turnos ocupados
    occupied_appointments = Appointment.objects.filter(
        date=selected_date
    ).exclude(status='cancelled').exclude(status='absent')
    
    occupied_times = [app.time.strftime('%H:%M') for app in occupied_appointments]

    # Generar todos los slots
    start_time = datetime.datetime.combine(selected_date, config.open_time)
    end_time = datetime.datetime.combine(selected_date, config.close_time)
    
    slots = []
    current_time = start_time
    # Solo mostrar turnos en el futuro si es hoy
    now = datetime.datetime.now()

    while current_time < end_time:
        t_str = current_time.strftime('%H:%M')
        
        # Validar si el slot ya está ocupado o ya pasó (si es hoy)
        is_past = selected_date == now.date() and current_time.time() <= now.time()
        is_occupied = t_str in occupied_times

        # No mostrar bloques que ya pasaron en tiempo real
        if not is_past:
            slots.append({
                'time': t_str,
                'available': not is_occupied
            })
            
        current_time += datetime.timedelta(minutes=config.interval_minutes)

    return render(request, 'booking/partials/time_slots.html', {'slots': slots, 'date': date_str})

def booking_success(request, token=None):
    appointment = None
    if token:
        appointment = get_object_or_404(Appointment, token=token)
    return render(request, 'booking/booking_success.html', {'appointment': appointment})

def manage_appointment(request, token):
    appointment = get_object_or_404(Appointment, token=token)
    config = get_config()
    
    # Calcular si se puede cancelar
    appointment_datetime = datetime.datetime.combine(appointment.date, appointment.time)
    # Hacer offset aware if settings.USE_TZ is True
    from django.conf import settings
    if settings.USE_TZ:
        appointment_datetime = timezone.make_aware(appointment_datetime)
    
    now = timezone.now()
    diff = appointment_datetime - now
    can_cancel = diff.total_seconds() > (config.cancellation_limit_hours * 3600)
    
    return render(request, 'booking/manage_appointment.html', {
        'appointment': appointment,
        'can_cancel': can_cancel,
        'config': config
    })

def cancel_appointment(request, token):
    appointment = get_object_or_404(Appointment, token=token)
    config = get_config()
    
    appointment_datetime = datetime.datetime.combine(appointment.date, appointment.time)
    from django.conf import settings
    if settings.USE_TZ:
        appointment_datetime = timezone.make_aware(appointment_datetime)
        
    diff = appointment_datetime - timezone.now()
    
    if diff.total_seconds() > (config.cancellation_limit_hours * 3600):
        appointment.status = 'cancelled'
        appointment.save()
        return redirect('manage_appointment', token=token)
    else:
        return HttpResponse("No se puede cancelar con tan poca antelación.", status=403)
def admin_calendar_view(request):
    # Solo staff puede ver
    if not request.user.is_staff:
        return redirect('admin:index')
    return render(request, 'booking/admin_calendar.html')

def admin_calendar_events(request):
    if not request.user.is_staff:
        return JsonResponse([], safe=False)
        
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    appointments = Appointment.objects.all()
    if start and end:
        appointments = appointments.filter(date__range=[start.split('T')[0], end.split('T')[0]])
        
    events = []
    for app in appointments:
        color = '#D6A4A4' # Rosa viejo default
        if app.status == 'cancelled': color = '#e3342f'
        elif app.status == 'completed': color = '#38c172'
        elif app.status == 'absent': color = '#718096'
        
        start_dt = datetime.datetime.combine(app.date, app.time).isoformat()
        # Asumimos 30 min duration para visualización
        end_dt = (datetime.datetime.combine(app.date, app.time) + datetime.timedelta(minutes=30)).isoformat()
        
        events.append({
            'title': f"{app.client_name} {app.client_last_name}",
            'start': start_dt,
            'end': end_dt,
            'url': f"/admin/booking/appointment/{app.id}/change/",
            'backgroundColor': color,
            'borderColor': color,
        })
        
    return JsonResponse(events, safe=False)
