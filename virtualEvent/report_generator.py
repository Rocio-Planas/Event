from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


def generate_event_pdf(context):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']

    # Estilo personalizado
    custom_style = ParagraphStyle(
        'Custom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.darkblue,
    )

    story = []
    event = context['event']
    analytics = context['analytics']

    # Título
    story.append(Paragraph(f"Reporte del Evento: {event.title}", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"Generado el: {context['generated_at'].strftime('%d/%m/%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 0.3*inch))

    # Información general
    story.append(Paragraph("Información General", heading_style))
    story.append(Spacer(1, 0.1*inch))
    data = [
        ["Fecha del evento:", event.start_datetime.strftime('%d/%m/%Y %H:%M')],
        ["Duración (minutos):", event.duration_minutes],
        ["Tipo de acceso:", "Público" if event.privacy == 'public' else "Privado"],
        ["Categoría:", event.category],
        ["Descripción:", event.description[:200] + "..." if len(event.description) > 200 else event.description],
    ]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))

    # Métricas de participación
    story.append(Paragraph("Métricas de Participación", heading_style))
    story.append(Spacer(1, 0.1*inch))
    metrics_data = [
        ["Espectadores únicos:", analytics.unique_viewers],
        ["Total mensajes:", context['total_messages']],
        ["Manos levantadas:", analytics.total_hands],
        ["Votos en encuestas:", analytics.total_poll_votes],
        ["Satisfacción media:", f"{analytics.average_satisfaction} / 5"],
        ["Tiempo medio visualización:", f"{analytics.average_watch_time} min"],
    ]
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 0.3*inch))

    # Gráfica de mensajes por hora
    if context['messages_per_hour']:
        story.append(Paragraph("Mensajes por Hora", heading_style))
        story.append(Spacer(1, 0.1*inch))
        # Preparar datos
        hours = sorted(context['messages_per_hour'].keys())
        counts = [context['messages_per_hour'][h] for h in hours]
        drawing = Drawing(400, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.width = 300
        bc.height = 120
        bc.data = [counts]
        # Mostrar solo la hora (HH:00)
        category_names = [h[11:16] for h in hours]
        bc.categoryAxis.categoryNames = category_names
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.labels.fontSize = 8
        bc.valueAxis.valueMin = 0
        bc.bars[0].fillColor = colors.blue
        drawing.add(bc)
        story.append(drawing)
        story.append(Spacer(1, 0.2*inch))

    # Preguntas anónimas
    anonymous_questions = context['anonymous_questions']
    if anonymous_questions.exists():
        story.append(PageBreak())
        story.append(Paragraph("Preguntas Anónimas Recibidas", heading_style))
        story.append(Spacer(1, 0.1*inch))
        for q in anonymous_questions[:20]:  # límite de 20
            story.append(Paragraph(f"• {q.content}", custom_style))
            story.append(Spacer(1, 0.05*inch))

    # Construir PDF
    doc.build(story)
    pdf_buffer = buffer.getvalue()
    buffer.close()
    return pdf_buffer
