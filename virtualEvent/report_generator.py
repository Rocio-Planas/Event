from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


def generate_event_pdf(context):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )
    styles = getSampleStyleSheet()

    # Colores personalizados
    verde_principal = colors.HexColor("#2E7D32")  # verde oscuro agradable
    azul_tabla = colors.HexColor("#E3F2FD")  # azul muy claro
    azul_grafico = colors.HexColor("#1E88E5")  # azul vivo pero suave
    gris_claro = colors.HexColor("#F5F5F5")
    gris_borde = colors.HexColor("#BDBDBD")

    # Estilos de texto
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=verde_principal,
        fontSize=18,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        textColor=azul_grafico,
        fontSize=14,
        spaceBefore=10,
        spaceAfter=6,
        borderPadding=0,
    )
    normal_style = styles["Normal"]
    custom_style = ParagraphStyle(
        "Custom",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.darkblue,
    )

    desc_style = ParagraphStyle(
        "Description",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.black,
        wordWrap="CJK",
    )

    story = []
    event = context["event"]
    analytics = context["analytics"]

    # Título
    story.append(Paragraph(f"Reporte del Evento: {event.title}", title_style))
    story.append(Spacer(1, 0.15 * inch))
    story.append(
        Paragraph(
            f"Generado el: {context['generated_at'].strftime('%d/%m/%Y %H:%M')}",
            normal_style,
        )
    )
    story.append(Spacer(1, 0.25 * inch))

    # Información general
    story.append(Paragraph("Información General", heading_style))
    story.append(Spacer(1, 0.05 * inch))

    desc_paragraph = Paragraph(event.description, desc_style)

    data = [
        ["Fecha del evento:", event.start_datetime.strftime("%d/%m/%Y %H:%M")],
        ["Duración (minutos):", event.duration_minutes],
        ["Tipo de acceso:", "Público" if event.privacy == "public" else "Privado"],
        ["Categoría:", event.category],
        ["Descripción:", desc_paragraph],  
    ]
    table = Table(data, colWidths=[2 * inch, 4 * inch])
    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    gris_claro,
                ),  # fondo gris claro para etiquetas
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    colors.white,
                ),  # fondo blanco para valores
                ("GRID", (0, 0), (-1, -1), 0.5, gris_borde),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    verde_principal,
                ),  # texto de etiquetas en verde
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),  # etiquetas alineadas a la derecha
                ("ALIGN", (1, 0), (1, -1), "LEFT"),  # valores a la izquierda
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.25 * inch))

    # Métricas de participación
    story.append(Paragraph("Métricas de Participación", heading_style))
    story.append(Spacer(1, 0.05 * inch))
    metrics_data = [
        ["Espectadores únicos:", analytics.unique_viewers],
        ["Total mensajes:", context["total_messages"]],
        ["Manos levantadas:", analytics.total_hands],
        ["Votos en encuestas:", analytics.total_poll_votes],
        ["Satisfacción media:", f"{analytics.average_satisfaction} / 5"],
        ["Tiempo medio visualización:", f"{analytics.average_watch_time} min"],
    ]
    metrics_table = Table(metrics_data, colWidths=[2.5 * inch, 2 * inch])
    metrics_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    azul_tabla,
                ),  # fondo azul claro para etiquetas
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    colors.white,
                ),  # fondo blanco para valores
                ("GRID", (0, 0), (-1, -1), 0.5, gris_borde),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TEXTCOLOR", (0, 0), (0, -1), azul_grafico),  # texto etiquetas en azul
                ("ALIGN", (1, 0), (1, -1), "CENTER"),  # valores centrados
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ]
        )
    )
    story.append(metrics_table)
    story.append(Spacer(1, 0.25 * inch))

    # Gráfica de mensajes por hora (reducimos altura para evitar salto de página)
    if context["messages_per_hour"]:
        story.append(Paragraph("Mensajes por Hora", heading_style))
        story.append(Spacer(1, 0.05 * inch))
        hours = sorted(context["messages_per_hour"].keys())
        counts = [context["messages_per_hour"][h] for h in hours]
        # Reducimos tamaño del gráfico para que quepa en la misma página
        drawing = Drawing(400, 160)  # altura reducida de 200 a 160
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 40  # mover un poco hacia arriba
        bc.width = 300
        bc.height = 100  # altura de las barras reducida
        bc.data = [counts]
        category_names = [h[11:16] for h in hours]
        bc.categoryAxis.categoryNames = category_names
        bc.categoryAxis.labels.angle = 45
        bc.categoryAxis.labels.fontSize = 8
        bc.categoryAxis.labels.textAnchor = "start"
        bc.valueAxis.valueMin = 0
        bc.bars[0].fillColor = azul_grafico  # color azul agradable
        drawing.add(bc)
        story.append(drawing)
        story.append(Spacer(1, 0.15 * inch))

    # Preguntas anónimas
    anonymous_questions = context["anonymous_questions"]
    if anonymous_questions.exists():
        story.append(PageBreak())
        story.append(Paragraph("Preguntas Anónimas Recibidas", heading_style))
        story.append(Spacer(1, 0.1 * inch))
        for q in anonymous_questions[:20]:
            story.append(Paragraph(f"• {q.content}", custom_style))
            story.append(Spacer(1, 0.05 * inch))

    # Construir PDF
    doc.build(story)
    pdf_buffer = buffer.getvalue()
    buffer.close()
    return pdf_buffer
