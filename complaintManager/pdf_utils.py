from django.utils.translation import ugettext_lazy as _
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.linecharts import SampleHorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table,\
    TableStyle, Image
from .models import Division, Log, ComplaintImages
import datetime
from reportlab.lib import utils


class PdfPrint:

    # initialize class
    def __init__(self, buffer, pageSize):
        self.buffer = buffer
        # default format is A4
        if pageSize == 'A4':
            self.pageSize = A4
        self.width, self.height = self.pageSize

    def pageNumber(self, canvas, doc):
        number = canvas.getPageNumber()
        canvas.drawCentredString(100*mm, 15*mm, str(number))

    def title_draw(self, x, y, text):
        chart_title = Label()
        chart_title.x = x
        chart_title.y = y
        chart_title.fontName = 'FreeSansBold'
        chart_title.fontSize = 16
        chart_title.textAnchor = 'middle'
        chart_title.setText(text)
        return chart_title

    def legend_draw(self, labels, chart, **kwargs):
        legend = Legend()
        chart_type = kwargs['type']
        legend.fontName = 'FreeSans'
        legend.fontSize = 13
        legend.strokeColor = None
        if 'x' in kwargs:
            legend.x = kwargs['x']
        if 'y' in kwargs:
            legend.y = kwargs['y']
        legend.alignment = 'right'
        if 'boxAnchor' in kwargs:
            legend.boxAnchor = kwargs['boxAnchor']
        if 'columnMaximum' in kwargs:
            legend.columnMaximum = kwargs['columnMaximum']
        # x-distance between neighbouring swatche\s
        legend.deltax = 0
        lcolors = legendcolors
        if chart_type == 'line':
            lcolors = [colors.red, colors.blue]
        legend.colorNamePairs = zip(lcolors, labels)

        for i, color in enumerate(lcolors):
            if chart_type == 'line':
                chart.lines[i].fillColor = color
            elif chart_type == 'pie':
                chart.slices[i].fillColor = color
            elif chart_type == 'bar':
                chart.bars[i].fillColor = color
        return legend

    def line_chart_draw(self, values, days):
        nr_days = len(days)
        min_temp = min(min(values[0]), min(values[1]))
        d = Drawing(0, 170)
        # draw line chart
        chart = SampleHorizontalLineChart()
        # set width and height
        chart.width = 350
        chart.height = 135
        # set data values
        chart.data = values
        # use(True) or not(False) line between points
        chart.joinedLines = True
        # set font desired
        chart.lineLabels.fontName = 'FreeSans'
        # set color for the plot area border and interior area
        chart.strokeColor = colors.white
        chart.fillColor = colors.lightblue
        # set lines color and width
        chart.lines[0].strokeColor = colors.red
        chart.lines[0].strokeWidth = 2
        chart.lines[1].strokeColor = colors.blue
        chart.lines[1].strokeWidth = 2
        # set symbol for points
        chart.lines.symbol = makeMarker('Square')
        # set format for points from chart
        chart.lineLabelFormat = '%2.0f'
        # for negative axes intersect should be under zero
        chart.categoryAxis.joinAxisMode = 'bottom'
        # set font used for axes
        chart.categoryAxis.labels.fontName = 'FreeSans'
        if nr_days > 7:
            chart.categoryAxis.labels.angle = 45
            chart.categoryAxis.labels.boxAnchor = 'e'
        chart.categoryAxis.categoryNames = days
        # change y axe format
        chart.valueAxis.labelTextFormat = '%2.0f °C'
        chart.valueAxis.valueStep = 10
        if min_temp > 0:
            chart.valueAxis.valueMin = 0
        llabels = ['Max temp', 'Min temp']
        d.add(self.title_draw(250, 180, _('Temperatures statistics')))
        d.add(chart)
        d.add(self.legend_draw(llabels, chart, x=400, y=150, type='line'))
        return d

    def pie_chart_draw(self, values, llabels):
        d = Drawing(10, 150)
        # chart
        pc = Pie()
        pc.x = 0
        pc.y = 50
        # set data
        pc.data = values
        # set labels
        pc.labels = get_percentage(values)
        # set the link line between slice and it's label
        pc.sideLabels = 1
        # set width and color for slices
        pc.slices.strokeWidth = 0
        pc.slices.strokeColor = None
        d.add(self.title_draw(250, 180,
                              _('Precipitation probability statistics')))
        d.add(pc)
        d.add(self.legend_draw(llabels, pc, x=300, y=150, boxAnchor='ne',
                               columnMaximum=12, type='pie'))
        return d

    def vertical_bar_chart_draw(self, values, days, llabels):
        d = Drawing(0, 170)
        #  chart
        bc = VerticalBarChart()
        # set width and height
        bc.height = 125
        bc.width = 470
        # set data
        bc.data = values
        # set distance between bars elements
        bc.barSpacing = 0.5

        # set labels position under the x axe
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        # set name displayed for x axe
        bc.categoryAxis.categoryNames = days

        # set label format for each bar
        bc.barLabelFormat = '%d'
        # set distance between top of bar and it's label
        bc.barLabels.nudge = 7

        # set some charactestics for the Y axe
        bc.valueAxis.labelTextFormat = '%d km/h'
        bc.valueAxis.valueMin = 0

        d.add(self.title_draw(250, 190, _('Wind speed statistics')))
        d.add(bc)
        d.add(self.legend_draw(llabels, bc, x=480, y=165, boxAnchor='ne',
                               columnMaximum=1, type='bar'))
        # d.add(bcl)
        return d

    def individual_report(self, complaint, title):
        # set some characteristics for pdf document
        doc = SimpleDocTemplate(
            self.buffer,
            rightMargin=72,
            leftMargin=72,
            topMargin=30,
            bottomMargin=72,
            pagesize=self.pageSize)

        # a collection of styles offer by the library
        styles = getSampleStyleSheet()
        # add custom paragraph style
        styles.add(ParagraphStyle(
            name="TableHeader", fontSize=11, alignment=TA_CENTER))
        styles.add(ParagraphStyle(
            name="ParagraphTitle", fontSize=11, alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(
            name="Justify", alignment=TA_JUSTIFY))
        # list used for elements added into document
        data = []
        data.append(Paragraph(title, styles['Title']))
        data.append(Spacer(1,48))
        table_data = []
        table_data.append(
            ['Nama Pelapor', ': ' + complaint.member.user.first_name + ' ' + complaint.member.user.last_name])
        table_data.append(
            ['Nomor Telepon Pelapor', ': ' + complaint.member.phone])
        table_data.append(
            ['E-mail Pelapor', ': ' + complaint.member.user.email])
        table_data.append(
            ['Kategori Sumber Pelapor', ': ' + str(complaint.member.role)])
        table_data.append(
            ['Rincian Pelapor', ': ' + str(complaint.member.role.origin)])
        table_data.append(
            ['Judul Keluhan', ': ' + complaint.title])
        divisi_list = []
        for division in complaint.assigned_divisions.all():
            divisi_list.append(division.code)
        divisi_string = ", ".join(divisi_list)
        table_data.append(
            ['Jenis Keluhan', ': ' + divisi_string])
        table_data.append(
            ['Deskripsi Keluhan', ': ' + complaint.description])
        if (complaint.status == 'S'):
            status = 'Submitted'
        elif (complaint.status == 'P'):
            status = 'On Progress'
        else:
            status = 'Finished'
        table_data.append(
            ['Status Keluhan', ': ' + status])
        table_data.append(
            ['Leader', ': ' + complaint.leader.name])
        table_data.append(
            ['Lokasi Kejadian', ': ' + complaint.location.name])
        # create document
        table = Table(table_data)
        table.hAlign = 'LEFT'
        data.append(table)
        data.append(Spacer(1, 24))
        data.append(Paragraph('Log Perubahan: ', styles['Justify']))
        logtable_data = []
        logtable_data.append([
            Paragraph('Tanggal', styles['TableHeader']),
            Paragraph('Deskripsi Perubahan', styles['TableHeader']),
            Paragraph('Diubah Oleh', styles['TableHeader'])])
        logs = Log.objects.filter(complaint=complaint)
        for log in logs:
            date = str(log.date.strftime("%d-%m-%Y"))
            logtable_data.append([date, log.description, log.creator])
        logtable = Table(logtable_data)
        logtable.hAlign = 'LEFT'
        logtable.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
             ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
             ('BACKGROUND', (0, 0), (-1, 0), colors.gray)]))
        data.append(Spacer(1, 12))
        data.append(logtable)
        data.append(Spacer(1, 24))
        data.append(Paragraph('Media: ', styles['Justify']))
        images = ComplaintImages.objects.filter(complaint=complaint)
        for image in images:
            # img = Image('http://127.0.0.1:8888/media/' + str(image.src))
            img = utils.ImageReader('http://127.0.0.1:8888/media/' + str(image.src))
            iw, ih = img.getSize()
            aspect = ih / float(iw)
            if iw > ih:
                width = 300
                data.append(Image('http://127.0.0.1:8888/media/' + str(image.src), width, width * aspect))
            else:
                height = 300
                data.append(Image('http://127.0.0.1:8888/media/' + str(image.src), height / aspect, height))
        # insert a blank space
        data.append(Spacer(1, 12))

        # create document
        doc.build(data, onFirstPage=self.pageNumber, onLaterPages=self.pageNumber)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf

    def collective_report(self, complaints, title, dateduration):
        # set some characteristics for pdf document
        doc = SimpleDocTemplate(
            self.buffer,
            rightMargin=40,
            leftMargin=40,
            topMargin=30,
            bottomMargin=72,
            pagesize=self.pageSize)

        # a collection of styles offer by the library
        styles = getSampleStyleSheet()
        # add custom paragraph style
        styles.add(ParagraphStyle(
            name="TableHeader", fontSize=11, alignment=TA_CENTER))
        styles.add(ParagraphStyle(
            name="ParagraphTitle", fontSize=11, alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(
            name="Justify", alignment=TA_JUSTIFY))
        # list used for elements added into document
        data = []
        data.append(Paragraph(title, styles['Title']))
        # insert a blank space
        data.append(Spacer(1, 24))
        data.append(Paragraph(dateduration, styles['ParagraphTitle']))
        data.append(Spacer(1, 12))
        table_data = []
        # table header
        table_data.append([
            Paragraph('Tanggal', styles['TableHeader']),
            Paragraph('Deskripsi', styles['TableHeader']),
            Paragraph('Status', styles['TableHeader']),
            Paragraph('Divisi yang Mengerjakan', styles['TableHeader']),
            Paragraph('Prioritas', styles['TableHeader']),
            Paragraph('Pemberi Keluhan', styles['TableHeader']),
            Paragraph('Asal Instansi Pelapor', styles['TableHeader']),
            Paragraph('Asal Pelapor', styles['TableHeader'])])
        for complaint in complaints:
            # add a row to table
            divisi_list = []
            for division in complaint.assigned_divisions.all():
                divisi_list.append(division.code)
            divisi_string = ", ".join(divisi_list)
            if (complaint.status == 'S'):
                status = 'Dilaporkan'
            elif (complaint.status == 'P'):
                status = 'Dalam Pengerjaan'
            else:
                status = 'Selesai'
            table_data.append(
                [complaint.reported.strftime('%d-%m-%Y'),
                 Paragraph(complaint.description, styles['Justify']),
                 Paragraph(status, styles['Justify']),
                 Paragraph(divisi_string, styles['Justify']),
                 Paragraph(str(complaint.priority), styles['Justify']),
                 Paragraph(complaint.member.user.first_name, styles['Justify']),
                 Paragraph(complaint.member.role.origin.name, styles['Justify']),
                 Paragraph(str(complaint.member.role), styles['Justify'])])
        # create table
        wh_table = Table(table_data)
        wh_table.hAlign = 'LEFT'
        wh_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
             ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
             ('BACKGROUND', (0, 0), (-1, 0), colors.gray)]))
        data.append(wh_table)
        data.append(Spacer(1, 36))
        #for ...
        divisions = Division.objects.all()
        divtable_data = []
        for division in divisions:
            divtable_data.append(
                [division.code, ': '+ division.name])
        # create document
        div_table = Table(divtable_data)
        div_table.hAlign = 'LEFT'
        data.append(div_table)
        doc.build(data, onFirstPage=self.pageNumber,
                  onLaterPages=self.pageNumber)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf