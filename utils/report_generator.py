"""
Professional PDF Report Generator for PixelForensics
Creates detailed, forensic-grade analysis reports
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import hashlib
import os
from io import BytesIO

class ReportGenerator:
    """Generate comprehensive PDF reports for deepfake analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0f3460'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection
        self.styles.add(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#16213e'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2a2a2a'),
            spaceAfter=6,
            alignment=TA_LEFT
        ))
    
    def generate_report(self, result_data, image_path, output_path):
        """
        Generate complete PDF report
        
        Args:
            result_data: Dict with prediction results from backend
            image_path: Path to analyzed image
            output_path: Where to save PDF
        
        Returns:
            Path to generated PDF
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        story = []
        
        # Page 1: Executive Summary
        story.extend(self._create_executive_summary(result_data, image_path))
        story.append(PageBreak())
        
        # Page 2: Detailed Analysis
        story.extend(self._create_detailed_analysis(result_data))
        story.append(PageBreak())
        
        # Page 3: Metadata Analysis
        story.extend(self._create_metadata_section(result_data))
        story.append(PageBreak())
        
        # Page 4: Technical Details
        story.extend(self._create_technical_section(result_data))
        story.append(PageBreak())
        
        # Page 5: Conclusion & Disclaimer
        story.extend(self._create_conclusion(result_data))
        
        # Build PDF with custom page numbers
        doc.build(story, onFirstPage=self._add_page_footer, 
                 onLaterPages=self._add_page_footer)
        
        return output_path
    
    def _create_executive_summary(self, data, image_path):
        """Create executive summary page"""
        elements = []
        
        # Header
        elements.append(Paragraph("PIXELFORENSICS", self.styles['CustomTitle']))
        elements.append(Paragraph("Deepfake Analysis Report", 
                                 self.styles['Heading2']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        report_id = hashlib.md5(f"{data.get('filename', 'unknown')}{datetime.now()}".encode()).hexdigest()[:12].upper()
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        info_data = [
            ['Report ID:', report_id],
            ['Generated:', timestamp],
            ['Analyzed File:', data.get('filename', 'Unknown')],
            ['File Type:', data.get('file_type', 'Image').upper()]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0f3460')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Image preview
        if os.path.exists(image_path):
            try:
                img = Image(image_path, width=4*inch, height=3*inch, kind='proportional')
                elements.append(img)
                elements.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        # Verdict box
        is_fake = data.get('is_deepfake', False)
        confidence = data.get('confidence', 0)
        
        verdict_color = colors.HexColor('#dc3545') if is_fake else colors.HexColor('#28a745')
        verdict_text = "⚠️ AI-GENERATED / FAKE" if is_fake else "✓ AUTHENTIC / REAL"
        
        verdict_data = [[verdict_text]]
        verdict_table = Table(verdict_data, colWidths=[6*inch])
        verdict_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), verdict_color),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, verdict_color),
        ]))
        elements.append(verdict_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Confidence gauge
        confidence_data = [
            ['Confidence Score:', f"{confidence:.1f}%"]
        ]
        conf_table = Table(confidence_data, colWidths=[2.5*inch, 3.5*inch])
        conf_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0f3460')),
            ('TEXTCOLOR', (1, 0), (1, -1), verdict_color),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(conf_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        summary_text = self._generate_summary(data)
        elements.append(Paragraph("<b>Executive Summary:</b>", self.styles['Subsection']))
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        
        return elements
    
    def _create_detailed_analysis(self, data):
        """Create detailed method-by-method analysis"""
        elements = []
        
        elements.append(Paragraph("Detailed Analysis", self.styles['SectionHeader']))
        elements.append(Paragraph("Multi-Method Ensemble Detection", self.styles['Subsection']))
        
        # Get method results
        method_results = data.get('method_results', {})
        ensemble_score = data.get('ensemble_score', 0) * 100
        threshold = data.get('threshold', 50)
        
        # Per-method table
        method_data = [['Detection Method', 'Verdict', 'Confidence', 'Weight']]
        
        method_weights = {
            'Primary detector': '1.0',
            'Secondary detector': '0.9',
            'Frequency Analysis': '0.6',
            'ELA Analysis': '0.6',
            'Noise Analysis': '0.6',
            'Color Analysis': '0.5',
            'Metadata Analysis': '0.8-1.2*'
        }
        
        for method, details in method_results.items():
            is_fake = details.get('is_fake', False)
            conf = details.get('confidence', 0)
            verdict = "🔴 FAKE" if is_fake else "🟢 REAL"
            weight = method_weights.get(method, '1.0')
            
            method_data.append([
                method,
                verdict,
                f"{conf:.1f}%",
                weight
            ])
        
        method_table = Table(method_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1*inch])
        method_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Data
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(method_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Voting summary
        fake_count = sum(1 for m in method_results.values() if m.get('is_fake', False))
        total_methods = len(method_results)
        
        voting_data = [
            ['Methods Voting FAKE:', f"{fake_count} / {total_methods}"],
            ['Weighted Ensemble Score:', f"{ensemble_score:.1f}%"],
            ['Decision Threshold:', f"{threshold:.0f}%"],
        ]
        
        voting_table = Table(voting_data, colWidths=[3*inch, 3*inch])
        voting_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0f3460')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(voting_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Explanation
        elements.append(Paragraph("* Metadata weight increases to 1.2 when no EXIF data is found", 
                                 self.styles['CustomBody']))
        
        return elements
    
    def _create_metadata_section(self, data):
        """Create EXIF metadata analysis section"""
        elements = []
        
        elements.append(Paragraph("EXIF Metadata Analysis", self.styles['SectionHeader']))
        
        metadata_info = data.get('metadata_info', {})
        has_exif = metadata_info.get('has_exif', False)
        
        if has_exif:
            # Camera info found
            elements.append(Paragraph("✓ Camera Metadata Detected", self.styles['Subsection']))
            
            camera_data = []
            
            if metadata_info.get('camera_make'):
                camera_data.append(['Camera Make:', metadata_info['camera_make']])
            if metadata_info.get('camera_model'):
                camera_data.append(['Camera Model:', metadata_info['camera_model']])
            if metadata_info.get('software'):
                camera_data.append(['Software:', metadata_info['software']])
            if metadata_info.get('datetime'):
                camera_data.append(['Date/Time Taken:', metadata_info['datetime']])
            if metadata_info.get('iso'):
                camera_data.append(['ISO:', str(metadata_info['iso'])])
            if metadata_info.get('aperture'):
                camera_data.append(['Aperture:', f"f/{metadata_info['aperture']}"])
            if metadata_info.get('focal_length'):
                camera_data.append(['Focal Length:', f"{metadata_info['focal_length']}mm"])
            if metadata_info.get('gps_info'):
                camera_data.append(['GPS Data:', 'Present'])
            
            camera_data.append(['Total EXIF Tags:', str(metadata_info.get('total_tags', 0))])
            
            if camera_data:
                camera_table = Table(camera_data, colWidths=[2*inch, 4*inch])
                camera_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0f3460')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(camera_table)
            
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                "<b>Interpretation:</b> The presence of authentic camera EXIF data strongly "
                "suggests this image was captured by a physical camera device, which is "
                "typical of genuine photographs.",
                self.styles['CustomBody']
            ))
        else:
            # No EXIF found
            warning_data = [["⚠️ NO EXIF METADATA FOUND"]]
            warning_table = Table(warning_data, colWidths=[6*inch])
            warning_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff3cd')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#856404')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ffc107')),
            ]))
            elements.append(warning_table)
            elements.append(Spacer(1, 0.2*inch))
            
            elements.append(Paragraph(
                "<b>What this means:</b> The absence of EXIF metadata is highly suspicious "
                "and commonly observed in AI-generated images. However, it can also occur in:",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            reasons = [
                "• Screenshots of genuine images",
                "• Images downloaded from websites (metadata often stripped)",
                "• Photos edited in apps that remove EXIF data",
                "• Images shared through messaging apps",
                "• AI-generated or synthetic images (most common)"
            ]
            
            for reason in reasons:
                elements.append(Paragraph(reason, self.styles['CustomBody']))
        
        return elements
    
    def _create_technical_section(self, data):
        """Create technical details section"""
        elements = []
        
        elements.append(Paragraph("Technical Details", self.styles['SectionHeader']))
        
        # Models used
        elements.append(Paragraph("AI Models Deployed", self.styles['Subsection']))
        
        models_data = [
            ['Model Name', 'Type', 'Accuracy', 'Status'],
            ['dima806/ai_vs_real', 'ViT Transformer', '98.2%', '✓ Active'],
            ['Ateeqq/ai-vs-human', 'SigLIP2', '99.2%', '○ Optional']
        ]
        
        models_table = Table(models_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1.4*inch])
        models_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(models_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Analysis methods
        elements.append(Paragraph("Detection Methods Explained", self.styles['Subsection']))
        
        methods = [
            ("Frequency Analysis", "Examines the distribution of frequency components in the image using FFT. "
             "AI-generated images often show unnatural frequency patterns."),
            
            ("Error Level Analysis (ELA)", "Compares compression artifacts between original and recompressed "
             "versions. AI images show unusually uniform compression patterns."),
            
            ("Noise Analysis", "Analyzes sensor noise patterns. Real cameras have characteristic noise "
             "signatures that AI generators cannot perfectly replicate."),
            
            ("Color Analysis", "Examines color distribution, saturation, and histogram smoothness. "
             "AI images often display statistically anomalous color properties."),
            
            ("Metadata Analysis", "Checks for authentic camera EXIF data. Real photos contain detailed "
             "camera settings, timestamps, and device information.")
        ]
        
        for method_name, description in methods:
            elements.append(Paragraph(f"<b>{method_name}:</b> {description}", 
                                     self.styles['CustomBody']))
            elements.append(Spacer(1, 0.08*inch))
        
        return elements
    
    def _create_conclusion(self, data):
        """Create conclusion and disclaimer"""
        elements = []
        
        elements.append(Paragraph("Conclusion", self.styles['SectionHeader']))
        
        is_fake = data.get('is_deepfake', False)
        confidence = data.get('confidence', 0)
        
        conclusion_text = self._generate_conclusion_text(is_fake, confidence)
        elements.append(Paragraph(conclusion_text, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Disclaimer
        elements.append(Paragraph("Important Disclaimer", self.styles['SectionHeader']))
        
        disclaimer_points = [
            "This report is generated by an automated AI detection system and should be used as a preliminary assessment tool only.",
            
            "The results are based on statistical analysis and machine learning models that, while highly accurate, are not infallible.",
            
            "For critical decisions (legal proceedings, forensic investigations, or high-stakes verification), this report should be supplemented with expert human analysis and additional forensic tools.",
            
            "PixelForensics makes no warranties about the absolute accuracy of these results and accepts no liability for decisions made based on this report alone.",
            
            "Accuracy metrics are based on validation testing and may vary with real-world images. The system is regularly updated to detect new AI generation techniques."
        ]

        # Convert to Paragraph bullets
        bullet_list = ListFlowable(
            [ListItem(Paragraph(point, self.styles['CustomBody'])) for point in disclaimer_points],
            bulletType='bullet',
            leftIndent=15
        )

        disclaimer_table = Table([[bullet_list]], colWidths=[6*inch])
        disclaimer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(disclaimer_table)
        
        return elements
    
    def _generate_summary(self, data):
        """Generate plain-English summary"""
        is_fake = data.get('is_deepfake', False)
        confidence = data.get('confidence', 0)
        method_results = data.get('method_results', {})
        
        fake_count = sum(1 for m in method_results.values() if m.get('is_fake', False))
        total = len(method_results)
        
        if is_fake:
            return (f"Our analysis indicates with {confidence:.1f}% confidence that this image is "
                   f"likely AI-generated or manipulated. {fake_count} out of {total} detection methods "
                   f"flagged suspicious characteristics. Key indicators include patterns typical of "
                   f"AI generators and anomalies in the image structure that deviate from authentic "
                   f"photographic properties.")
        else:
            return (f"Our analysis indicates with {confidence:.1f}% confidence that this image appears "
                   f"to be authentic. {total - fake_count} out of {total} detection methods found "
                   f"characteristics consistent with genuine photographs. The image exhibits natural "
                   f"properties expected from real camera sensors and optical systems.")
    
    def _generate_conclusion_text(self, is_fake, confidence):
        """Generate conclusion paragraph"""
        if is_fake:
            if confidence >= 90:
                return ("Based on comprehensive multi-method analysis, we have <b>very high confidence</b> "
                       "that this image is AI-generated or significantly manipulated. Multiple independent "
                       "detection methods concur on this assessment, exhibiting strong statistical indicators "
                       "of synthetic generation.")
            elif confidence >= 75:
                return ("Our analysis provides <b>strong evidence</b> suggesting this image is likely "
                       "AI-generated or manipulated. The majority of detection methods identified "
                       "characteristics inconsistent with authentic photography.")
            else:
                return ("The analysis suggests this image <b>may be</b> AI-generated or manipulated, "
                       "though confidence is moderate. Some detection methods found suspicious patterns, "
                       "but results are not conclusive. Additional verification recommended.")
        else:
            if confidence >= 90:
                return ("Based on our analysis, we have <b>very high confidence</b> that this image is "
                       "authentic and not AI-generated. The image exhibits consistent characteristics of "
                       "genuine photography across multiple independent verification methods.")
            elif confidence >= 75:
                return ("Our analysis provides <b>strong evidence</b> that this image is authentic. "
                       "Most detection methods found characteristics consistent with real photographic "
                       "processes and camera sensors.")
            else:
                return ("The analysis suggests this image is <b>likely authentic</b>, though confidence "
                       "is moderate. Most detection methods found genuine characteristics, but some "
                       "ambiguity remains. Consider the context and source when evaluating authenticity.")
    
    def _add_page_footer(self, canvas, doc):
        """Add footer to each page and set PDF metadata"""
        
        canvas.saveState()
        
        # --- SET PDF METADATA (Fix for anonymous title) ---
        filename = os.path.basename(doc.filename)
        canvas.setTitle(filename)  # This sets the PDF title properly
        canvas.setAuthor("PixelForensics")
        canvas.setSubject("Deepfake Analysis Report")
        canvas.setCreator("PixelForensics AI Engine")
        
        # Page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(7.5*inch, 0.5*inch, text)
        
        # Footer text
        canvas.drawString(0.75*inch, 0.5*inch, "PixelForensics Report")
        canvas.drawCentredString(4.25*inch, 0.5*inch, 
                                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        canvas.restoreState()
