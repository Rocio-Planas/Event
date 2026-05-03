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
        from pe_analytics.models import StoredReport
        from django.utils import timezone

        metrics = calculate_event_metrics(event_id)

        try:
            report = StoredReport.objects.create(
                event_id=event_id,
                total_attendance=metrics['total_attendance'],
                total_revenue=metrics['total_revenue'],
                avg_ticket_price=metrics['avg_ticket_price'],
                age_distribution=metrics['age_distribution'],
                gender_distribution=metrics['gender_distribution'],
                ticket_distribution=metrics['ticket_distribution'],
                created_at=timezone.now(),
            )

            pdf_buffer = generate_pdf_report(event_id, metrics)
            report.pdf_report.save(f'report_{event_id}_{report.id}.pdf', pdf_buffer, save=True)

            return JsonResponse({
                'success': True,
                'report_id': report.id,
                'pdf_url': report.pdf_report.url if report.pdf_report else None
            })
        except Exception as e:
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
    gender_distribution = {
        gender_labels.get(row['user__sexo'], 'No especificado'): row['cnt']
        for row in gender_qs
        if row['user__sexo']
    }

    return {
        'total_attendance': total_attendance,
        'total_revenue': total_revenue,
        'avg_ticket_price': avg_ticket_price,
        'ticket_distribution': ticket_distribution,
        'age_distribution': age_buckets,
        'gender_distribution': gender_distribution,
    }


def generate_pdf_report(event_id, metrics):
    Event = apps.get_model('in_person_events', 'Event')
    try:
        event = Event.objects.get(id=event_id)
        event_title = event.title
    except Event.DoesNotExist:
        event_title = f'Evento {event_id}'

    html_content = render_to_string('pe_analytics/pdf_report.html', {
        'event_title': event_title,
        'event_id': event_id,
        'metrics': metrics,
    })

    try:
        from weasyprint import HTML
        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer
    except Exception:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f'Reporte Analítico: {event_title}', styles['Title']))
        elements.append(Spacer(1, 12))

        data = [
            ['Métrica', 'Valor'],
            ['Total de Asistentes', str(metrics['total_attendance'])],
            ['Ingresos Totales', f'${float(metrics["total_revenue"]):.2f}'],
            ['Precio Promedio', f'${float(metrics["avg_ticket_price"]):.2f}'],
        ]
        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 12),
            ('BACKGROUND', (0, 1), (1, -1), colors.beige),
            ('GRID', (0, 0), (1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph('Distribución por Tipo de Ticket', styles['Heading2']))
        ticket_data = [['Tipo', 'Cantidad']]
        for ticket_type, count in metrics['ticket_distribution'].items():
            ticket_data.append([ticket_type, str(count)])
        ticket_table = Table(ticket_data, colWidths=[200, 100])
        ticket_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightblue),
            ('GRID', (0, 0), (1, -1), 1, colors.black),
        ]))
        elements.append(ticket_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer