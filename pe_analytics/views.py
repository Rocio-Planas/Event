import json
from io import BytesIO
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Count
from django.apps import apps
from django.template.loader import render_to_string
from django.conf import settings


@method_decorator(login_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    template_name = 'pe_analytics/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.kwargs.get('event_id')

        Event = apps.get_model('in_person_events', 'Event')
        event = get_object_or_404(Event, id=event_id)

        metrics = calculate_event_metrics(event_id)

        context['event'] = event
        context['event_id'] = event_id
        context['total_attendance'] = metrics['total_attendance']
        context['total_revenue'] = metrics['total_revenue']
        context['avg_ticket_price'] = metrics['avg_ticket_price']
        context['age_distribution'] = json.dumps(metrics['age_distribution'])
        context['gender_distribution'] = json.dumps(metrics['gender_distribution'])
        context['ticket_distribution'] = json.dumps(metrics['ticket_distribution'])
        context['registrations_timeline'] = json.dumps(metrics['registrations_timeline'])
        context['active_page'] = 'analiticas'

        return context


@method_decorator(login_required, name='dispatch')
class AnalyticsStatsAPIView(View):
    def get(self, request, event_id):
        metrics = calculate_event_metrics(event_id)

        data = {
            'total_attendance': metrics['total_attendance'],
            'total_revenue': float(metrics['total_revenue']),
            'avg_ticket_price': float(metrics['avg_ticket_price']),
            'age_distribution': metrics['age_distribution'],
            'gender_distribution': metrics['gender_distribution'],
            'ticket_distribution': metrics['ticket_distribution'],
        }
        return JsonResponse({'success': True, 'data': data})


@method_decorator(login_required, name='dispatch')
class ExportReportView(View):
    def post(self, request, event_id):
        metrics = calculate_event_metrics(event_id)

        try:
            charts_json = request.POST.get('charts', '{}')
            import json
            charts = json.loads(charts_json) if charts_json else {}
            
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Charts received: {len(charts)} items - keys: {list(charts.keys())}")
            
            pdf_buffer = generate_pdf_report(event_id, metrics, charts)
            
            from django.http import HttpResponse
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="reporte_analiticas_{event_id}.pdf"'
            return response
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


def calculate_event_metrics(event_id):
    from decimal import Decimal
    
    Registration = apps.get_model('pe_registration', 'Registration')

    registrations = Registration.objects.filter(
        event_id=event_id,
        status=Registration.Status.CONFIRMADA
    ).select_related('user', 'ticket_type')

    total_attendance = registrations.count()

    revenue_agg = registrations.aggregate(total=Sum('ticket_type__price'))
    total_revenue = revenue_agg['total'] or 0
    if isinstance(total_revenue, Decimal):
        total_revenue = float(total_revenue)

    avg_agg = registrations.aggregate(avg=Avg('ticket_type__price'))
    avg_ticket_price = avg_agg['avg'] or 0
    if isinstance(avg_ticket_price, Decimal):
        avg_ticket_price = float(avg_ticket_price)

    TicketType = apps.get_model('pe_registration', 'TicketType')
    ticket_dist_qs = registrations.values('ticket_type__name').annotate(cnt=Count('id'))
    ticket_distribution = {
        d['ticket_type__name'] or 'General': d['cnt']
        for d in ticket_dist_qs
    }
    
    from django.db.models.functions import TruncDate
    registrations_by_date = registrations.annotate(reg_date=TruncDate('registration_date')).values('reg_date').annotate(cnt=Count('id')).order_by('reg_date')
    registrations_timeline = {
        str(r['reg_date'].strftime('%Y-%m-%d')): r['cnt']
        for r in registrations_by_date
        if r['reg_date']
    }

    age_buckets = {'0-17': 0, '18-25': 0, '26-35': 0, '36-45': 0, '46-60': 0, '60+': 0}
    for reg in registrations:
        user = reg.user
        if hasattr(user, 'get_edad'):
            age = user.get_edad()
        else:
            age = None
        if age is None:
            continue
        if age <= 17:
            age_buckets['0-17'] += 1
        elif age <= 25:
            age_buckets['18-25'] += 1
        elif age <= 35:
            age_buckets['26-35'] += 1
        elif age <= 45:
            age_buckets['36-45'] += 1
        elif age <= 60:
            age_buckets['46-60'] += 1
        else:
            age_buckets['60+'] += 1

    Usuario = apps.get_model('usuarios', 'Usuario')
    gender_qs = registrations.values('user__sexo').annotate(cnt=Count('id'))
    gender_labels = dict(Usuario.SEXOS) if hasattr(Usuario, 'SEXOS') else {'M': 'Masculino', 'F': 'Femenino', 'O': 'Otro', 'N': 'Prefiero no decirlo'}
    
    gender_distribution = {'Masculino': 0, 'Femenino': 0, 'Otro': 0, 'Prefiero no decirlo': 0}
    for row in gender_qs:
        if row['user__sexo']:
            label = gender_labels.get(row['user__sexo'], 'Otro')
            gender_distribution[label] = row['cnt']

    return {
        'total_attendance': total_attendance,
        'total_revenue': total_revenue,
        'avg_ticket_price': avg_ticket_price,
        'ticket_distribution': ticket_distribution,
        'age_distribution': age_buckets,
        'gender_distribution': gender_distribution,
        'registrations_timeline': registrations_timeline,
    }


def generate_pdf_report(event_id, metrics, charts=None):
    if charts is None:
        charts = {}
    Event = apps.get_model('in_person_events', 'Event')
    try:
        event = Event.objects.get(id=event_id)
        event_title = event.title
    except Event.DoesNotExist:
        event_title = f'Evento {event_id}'

    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"generate_pdf_report called with {len(charts)} charts")
    
    import base64
    import tempfile
    import os
    
    chart_files = {}
    for chart_name, base64_data in charts.items():
        if base64_data and base64_data.startswith('data:image'):
            header, data = base64_data.split(',', 1)
            img_data = base64.b64decode(data)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.write(img_data)
            temp_file.close()
            chart_files[chart_name] = temp_file.name
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f'Reporte Analítico: {event_title}', styles['Title']))
    elements.append(Spacer(1, 12))

    from datetime import datetime
    elements.append(Spacer(1, 20))

    elements.append(Paragraph('Métricas Principales', styles['Heading2']))
    metrics_data = [
        ['Métrica', 'Valor'],
        ['Total de Asistentes', str(metrics['total_attendance'])],
        ['Ingresos Totales', f'${float(metrics["total_revenue"]):.2f}'],
        ['Precio Promedio', f'${float(metrics["avg_ticket_price"]):.2f}'],
    ]
    metrics_table = Table(metrics_data, colWidths=[200, 200])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.lightgrey),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 20))

    if chart_files:
        elements.append(Paragraph('Gráficos', styles['Heading2']))
        
        img_width = 250
        img_height = 180
        
        chart_order = ['distributionChart', 'pieChart', 'ageChart', 'genderChart']
        for i, chart_name in enumerate(chart_order):
            if chart_name in chart_files:
                try:
                    img = Image(chart_files[chart_name], width=img_width, height=img_height)
                    elements.append(img)
                    if (i + 1) % 2 == 0:
                        elements.append(Spacer(1, 10))
                    else:
                        elements.append(Spacer(1, 10))
                except Exception as e:
                    logger.error(f"Error adding image {chart_name}: {e}")
        
        elements.append(Spacer(1, 20))

    elements.append(Paragraph('Distribución por Tipo de Ticket', styles['Heading2']))
    ticket_data = [['Tipo', 'Cantidad']]
    for ticket_type, count in metrics['ticket_distribution'].items():
        ticket_data.append([ticket_type, str(count)])
    if len(ticket_data) > 1:
        ticket_table = Table(ticket_data, colWidths=[250, 100])
        ticket_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('GRID', (0, 0), (1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ]))
        elements.append(ticket_table)

    elements.append(Spacer(1, 15))
    elements.append(Paragraph('Distribución por Edad', styles['Heading2']))
    age_data = [['Grupo de Edad', 'Cantidad']]
    for age_group, count in metrics['age_distribution'].items():
        age_data.append([age_group, str(count)])
    if len(age_data) > 1:
        age_table = Table(age_data, colWidths=[250, 100])
        age_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
            ('GRID', (0, 0), (1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ]))
        elements.append(age_table)

    elements.append(Spacer(1, 15))
    elements.append(Paragraph('Distribución por Género', styles['Heading2']))
    gender_data = [['Género', 'Cantidad']]
    for gender, count in metrics['gender_distribution'].items():
        gender_data.append([gender, str(count)])
    if len(gender_data) > 1:
        gender_table = Table(gender_data, colWidths=[250, 100])
        gender_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightyellow),
            ('GRID', (0, 0), (1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ]))
        elements.append(gender_table)

    elements.append(Spacer(1, 30))
    elements.append(Paragraph(f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))

    doc.build(elements)
    
    for temp_file in chart_files.values():
        try:
            os.unlink(temp_file)
        except:
            pass
    
    buffer.seek(0)
    return buffer