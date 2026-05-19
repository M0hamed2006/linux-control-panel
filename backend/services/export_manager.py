import json
import csv
from datetime import datetime
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ExportManager:
    """تصدير البيانات"""
    
    @staticmethod
    def export_json(data, filename=None):
        """تصدير JSON"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(f"exports/{filename}", 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filename
    
    @staticmethod
    def export_csv(data, columns, filename=None):
        """تصدير CSV"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
        
        with open(f"exports/{filename}", 'w') as f:
            f.write(output.getvalue())
        
        return filename
    
    @staticmethod
    def export_pdf(title, data, filename=None):
        """تصدير PDF"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        try:
            doc = SimpleDocTemplate(f"exports/{filename}", pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # العنوان
            title_style = styles['Heading1']
            title_style.textColor = '#e94560'
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # البيانات
            if isinstance(data, dict):
                for key, value in data.items():
                    story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
                    story.append(Spacer(1, 6))
            
            doc.build(story)
            return filename
        except Exception as e:
            print(f"PDF Export Error: {e}")
            return None
    
    @staticmethod
    def export_stats(stats, filename=None):
        """تصدير إحصائيات"""
        if not filename:
            filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        formatted = {
            'timestamp': datetime.now().isoformat(),
            'stats': stats
        }
        
        return ExportManager.export_json(formatted, filename)
