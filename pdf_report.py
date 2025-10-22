from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_LEFT
import json

with open("report_info.json", "r", encoding="utf-8") as f:
    info = json.load(f)

class AudioReportGenerator:
    def __init__(self, filename, page_size=(17 * inch, 30 * inch)):
        self.doc = SimpleDocTemplate(filename, pagesize=page_size)
        self.styles = getSampleStyleSheet()
        self._set_styles()
        self.story = []

    def _set_styles(self):
        self.styles.add(ParagraphStyle(
            name='NormalLeft',
            parent=self.styles['Normal'],
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=4
        ))
        self.styles.add(ParagraphStyle(
            name='HeadingLeft',
            parent=self.styles['Heading2'],
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=6
        ))

    def add_paragraph(self, text, style='NormalLeft', font_size=None, space_after=0, bold=False):
        if bold:
            text = f"<b>{text}</b>"
        if font_size:
            custom_style = ParagraphStyle(
                name=f"{style}_custom_{font_size}",
                parent=self.styles[style],
                fontSize=font_size
            )
            self.story.append(Paragraph(text, custom_style))
        else:
            self.story.append(Paragraph(text, self.styles[style]))
        if space_after:
            self.story.append(Spacer(1, space_after))

    def add_table(self, data, col_widths=None, h_align='LEFT', style_extra=None):
        table = Table(data, colWidths=col_widths, hAlign=h_align)
        style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ])
        if style_extra:
            style.add(*style_extra)
        table.setStyle(style)
        self.story.append(table)

    def load_image(self, path, max_width=5* inch, max_height=5 * inch):
        img_reader = ImageReader(path)
        orig_width, orig_height = img_reader.getSize()
        scale = min(max_width / orig_width, max_height / orig_height)
        return Image(path, width=orig_width * scale, height=orig_height * scale, hAlign='LEFT')
    
    def add_image(self, image_path, max_width=5 * inch, max_height=5 * inch):
        img = self.load_image(image_path, max_width, max_height)
        self.story.append(img)

    def build(self):
        self.doc.build(self.story)


report = AudioReportGenerator("simple_report.pdf")
img_path = "C:/Users/chimtsen/APx500_Python_Guide/audio_report/graph/48k/DNR.png"

report.add_paragraph(info["source_info"].get('Source', ''), style='HeadingLeft', font_size=16, space_after=12)
report.add_table([
    ['Date', info["source_info"].get('Date', '')],
    ['Source', info["source_info"].get('Source', '')],
    ['Sink', info["sink_info"].get('Sink', '')],
    ['Codec', info["source_info"].get('Codec', '')],
    ['Bit rate', info["source_info"].get('Bit rate', '')],
    ['Prerequisite', info["source_info"].get('Prerequisite', '')],
    ['Others', info["source_info"].get('Others', '')]
], col_widths=[1.5 * inch, 5.5 * inch])

for text in ["QHS:", "Logo:", "Lossless enabled?", "Low Latency mode with 48kHz:", "SWB"]:
    report.add_paragraph(text, bold=True)

for item in ['<para leftIndent="10">• Uplink bandwidth</para>', '<para leftIndent="10">• Downlink bandwidth</para>']:
    report.add_paragraph(item)
    report.add_image(img_path)

img_path = "C:/Users/chimtsen/APx500_Python_Guide/audio_report/graph/48k/DNR.png"
img = report.load_image(img_path)

# 48kHz DNR
report.add_paragraph("48kHz", bold=True)
report.add_paragraph('<para leftIndent="10">• DNR</para>')
report.add_table([
    ['R2.1', 'R3(Left)', 'R3(Right)'],
    [img, img, img]
])

# 48kHz Frequency Response
report.add_paragraph('<para leftIndent="10">• Frequency Response</para>')
report.add_table([
    ['R2.1', 'R3'],
    [img, ''],
    [img, ''],
    [img, ''],
    [img, '']
])

# 48kHz Multitone
report.add_paragraph('<para leftIndent="10">• Multitone</para>')
report.add_table([
    ['R2.1', 'R3'],
    [img, ''],
    [img, '']
])

# 96kHz DNR
report.add_paragraph("96kHz",bold=True)
report.add_paragraph('<para leftIndent="10">• DNR</para>')
report.add_table([
    ['R2.1', 'R3(Left)', 'R3(Right)'],
    [img, '', '']
])

# 96kHz Frequency Response
report.add_paragraph('<para leftIndent="10">• Frequency Response</para>')
report.add_table([
    ['R2.1', 'R3'],
    [img, ''],
    [img, ''],
    [img, ''],
    [img, '']
])

# 96kHz Multitone
report.add_paragraph('<para leftIndent="10">• Multitone</para>')
report.add_table([
    ['R2.1', 'R3'],
    [img, ''],
    [img, '']
])

report.build()