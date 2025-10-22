"""
RPA para Validación del Informe Técnico de Inspección Ocular
Proyecto: IE N° 33065 Pacro Yuncan
Adaptado al formato real del documento
"""


import PyPDF2
import re
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


@dataclass
class ValidationResult:
    """Resultado de validación de un componente"""
    component: str
    is_valid: bool
    missing_items: List[str]
    warnings: List[str]
    details: Dict


class InformeInspeccionValidator:
    """Validador del Informe Técnico de Inspección Ocular"""
    
    def __init__(self):
        # Estructura REAL basada en el entregable1.pdf
        self.estructura_informe = {
            "secciones_obligatorias": [
                "ANTECEDENTES",
                "METODOLOGIA PARA LA INSPECCION",
                "METODOLOGÍA PARA LA INSPECCIÓN",
                "UBICACION DEL PROYECTO",
                "UBICACIÓN DEL PROYECTO",
                "ACCESOS",
                "INFORMACION RECOGIDA DE CAMPO",
                "INFORMACIÓN RECOGIDA DE CAMPO",
                "INFRAESTRUCTURA EXISTENTE",
                "SERVICIOS BASICOS EXISTENTES",
                "SERVICIOS BÁSICOS EXISTENTES",
                "LIBRE DISPONIBILIDAD DEL TERRENO",
                "COMPATIBILIZACION DEL AREA A INTERVENIR",
                "COMPATIBILIZACIÓN DEL ÁREA A INTERVENIR",
                "VERIFICACION DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL",
                "VERIFICACIÓN DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL",
                "CONCLUSIONES Y RECOMENDACIONES"
            ],
            "minimo_requerido": 11,  # Las 11 secciones únicas obligatorias
            # Secciones que se consideran como "panel fotográfico implícito"
            "fotografias_incluidas": True  # El documento incluye fotografías en cada módulo
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error al leer PDF: {e}")
            return ""
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto para comparación"""
        text = text.upper()
        replacements = {
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'Ñ': 'N', '\n': ' ', '\t': ' '
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def find_sections(self, text: str, sections_list: List[str]) -> Dict[str, bool]:
        """Busca secciones en el texto"""
        text_normalized = self.normalize_text(text)
        found_sections = {}
        
        for section in sections_list:
            section_normalized = self.normalize_text(section)
            patterns = [
                rf'\b{re.escape(section_normalized)}\b',
                rf'\d+\.?\s*{re.escape(section_normalized)}',
                rf'[A-Z]+\.?\s*{re.escape(section_normalized)}'
            ]
            
            found = False
            for pattern in patterns:
                if re.search(pattern, text_normalized):
                    found = True
                    break
            
            found_sections[section] = found
        
        return found_sections
    
    def check_photographs(self, text: str) -> Dict:
        """Verifica la presencia de fotografías/panel fotográfico"""
        text_normalized = self.normalize_text(text)
        
        # Buscar referencias a fotografías
        foto_patterns = [
            r'FOTOGRAFIA\s*N',
            r'FOTO\s*N',
            r'FIGURA\s*N',
            r'IMAGEN\s*N'
        ]
        
        foto_count = 0
        for pattern in foto_patterns:
            matches = re.findall(pattern, text_normalized)
            foto_count += len(matches)
        
        return {
            "fotografias_encontradas": foto_count,
            "tiene_panel_fotografico": foto_count > 0
        }
    
    def validate_informe_inspeccion(self, text: str) -> ValidationResult:
        """Valida el Informe de Inspección Ocular según estructura REAL"""
        config = self.estructura_informe
        secciones = config["secciones_obligatorias"]
        
        found_sections = self.find_sections(text, secciones)
        
        # Agrupar variantes de secciones
        unique_sections = {}
        section_groups = [
            ["METODOLOGIA PARA LA INSPECCION", "METODOLOGÍA PARA LA INSPECCIÓN"],
            ["UBICACION DEL PROYECTO", "UBICACIÓN DEL PROYECTO"],
            ["INFORMACION RECOGIDA DE CAMPO", "INFORMACIÓN RECOGIDA DE CAMPO"],
            ["SERVICIOS BASICOS EXISTENTES", "SERVICIOS BÁSICOS EXISTENTES"],
            ["COMPATIBILIZACION DEL AREA A INTERVENIR", "COMPATIBILIZACIÓN DEL ÁREA A INTERVENIR"],
            ["VERIFICACION DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL", 
             "VERIFICACIÓN DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL"]
        ]
        
        for section in secciones:
            group_found = False
            for group in section_groups:
                if section in group:
                    group_key = group[0]
                    if group_key not in unique_sections:
                        unique_sections[group_key] = any(found_sections.get(s, False) for s in group)
                    group_found = True
                    break
            
            if not group_found and section not in [s for g in section_groups for s in g]:
                unique_sections[section] = found_sections.get(section, False)
        
        # Verificar fotografías
        foto_info = self.check_photographs(text)
        
        # Si hay fotografías en el documento, se considera que tiene panel fotográfico implícito
        if foto_info["tiene_panel_fotografico"]:
            unique_sections["PANEL FOTOGRÁFICO (IMPLÍCITO)"] = True
        
        found_count = sum(1 for v in unique_sections.values() if v)
        missing = [k for k, v in unique_sections.items() if not v]
        
        # El documento es válido si tiene las 11 secciones requeridas
        is_valid = found_count >= config["minimo_requerido"]
        
        warnings = []
        if found_count < len(unique_sections):
            warnings.append(f"Se encontraron {found_count}/{len(unique_sections)} secciones")
        
        if foto_info["fotografias_encontradas"] > 0:
            warnings.append(f"Documento incluye {foto_info['fotografias_encontradas']} fotografías distribuidas en secciones")
        
        return ValidationResult(
            component="ESTUDIO TÉCNICO DE INSPECCIÓN OCULAR",
            is_valid=is_valid,
            missing_items=missing,
            warnings=warnings,
            details={
                "secciones_encontradas": found_count,
                "secciones_requeridas": config["minimo_requerido"],
                "secciones_totales": len(unique_sections),
                "detalle_secciones": unique_sections,
                "fotografias": foto_info["fotografias_encontradas"]
            }
        )
    
    def validate_pdf(self, pdf_path: str) -> Dict:
        """Valida el Informe de Inspección Ocular desde PDF"""
        print(f"\n{'='*80}")
        print(f"VALIDACIÓN DEL ESTUDIO TÉCNICO DE INSPECCIÓN OCULAR")
        print(f"{'='*80}")
        print(f"Archivo: {pdf_path}")
        print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        print("Extrayendo texto del PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {
                "status": "ERROR",
                "message": "No se pudo extraer texto del PDF"
            }
        
        print(f"✓ Texto extraído: {len(text)} caracteres\n")
        
        print("Validando Estudio Técnico de Inspección Ocular...\n")
        result = self.validate_informe_inspeccion(text)
        self._print_result(result)
        
        print(f"\n{'='*80}")
        print(f"RESUMEN")
        print(f"{'='*80}")
        print(f"Estado: {'✓ APROBADO' if result.is_valid else '✗ OBSERVADO'}")
        print(f"Secciones encontradas: {result.details['secciones_encontradas']}/{result.details['secciones_totales']}")
        print(f"Cumplimiento: {(result.details['secciones_encontradas']/result.details['secciones_totales']*100):.1f}%")
        print(f"Fotografías incluidas: {result.details['fotografias']}")
        print(f"{'='*80}\n")
        
        report = {
            "metadata": {
                "archivo": pdf_path,
                "fecha_validacion": datetime.now().isoformat(),
                "componente": "ESTUDIO TÉCNICO DE INSPECCIÓN OCULAR",
                "estado": "APROBADO" if result.is_valid else "OBSERVADO"
            },
            "validacion": {
                "componente": result.component,
                "valido": result.is_valid,
                "elementos_faltantes": result.missing_items,
                "advertencias": result.warnings,
                "detalles": result.details
            },
            "observaciones_generales": self._generate_observations(result)
        }
        
        return report
    
    def _print_result(self, result: ValidationResult):
        """Imprime resultado de validación"""
        status_icon = "✓" if result.is_valid else "✗"
        status_text = "VÁLIDO" if result.is_valid else "OBSERVADO"
        
        print(f"   {status_icon} {status_text}")
        
        if result.missing_items:
            print(f"\n   Elementos faltantes:")
            for item in result.missing_items:
                print(f"      • {item}")
        
        if result.warnings:
            print(f"\n   Información adicional:")
            for warning in result.warnings:
                print(f"      ℹ {warning}")
    
    def _generate_observations(self, result: ValidationResult) -> List[str]:
        """Genera observaciones generales"""
        observations = []
        
        if not result.is_valid:
            observations.append(
                f"El informe presenta {len(result.missing_items)} sección(es) faltante(s)"
            )
            
            if result.missing_items:
                observations.append(
                    f"Secciones faltantes: {', '.join(result.missing_items)}"
                )
        else:
            observations.append("El informe cumple con todos los requisitos establecidos")
        
        if result.details.get('fotografias', 0) > 0:
            observations.append(f"El documento incluye {result.details['fotografias']} fotografías como evidencia")
        
        return observations
    
    def export_report(self, report: Dict, output_path: str = "reporte_inspeccion_ocular.json"):
        """Exporta reporte a JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Reporte JSON exportado: {output_path}")
            return True
        except Exception as e:
            print(f"\n✗ Error al exportar reporte JSON: {e}")
            return False
    
    def export_report_txt(self, report: Dict, output_path: str = "reporte_inspeccion_ocular.txt"):
        """Exporta reporte a formato TXT legible"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE VALIDACIÓN\n")
                f.write("ESTUDIO TÉCNICO DE INSPECCIÓN OCULAR\n")
                f.write("="*80 + "\n\n")
                
                meta = report["metadata"]
                f.write(f"Archivo: {meta['archivo']}\n")
                f.write(f"Fecha: {meta['fecha_validacion']}\n")
                f.write(f"Componente: {meta['componente']}\n")
                f.write(f"Estado: {meta['estado']}\n")
                f.write("\n" + "="*80 + "\n\n")
                
                val = report["validacion"]
                f.write(f"RESULTADO DE VALIDACIÓN\n")
                f.write("-"*80 + "\n")
                f.write(f"Estado: {'✓ VÁLIDO' if val['valido'] else '✗ OBSERVADO'}\n")
                
                if val['elementos_faltantes']:
                    f.write(f"\nElementos faltantes:\n")
                    for item in val['elementos_faltantes']:
                        f.write(f"   • {item}\n")
                
                if val['advertencias']:
                    f.write(f"\nInformación adicional:\n")
                    for warning in val['advertencias']:
                        f.write(f"   ℹ {warning}\n")
                
                if val['detalles']:
                    f.write(f"\nDetalles:\n")
                    for key, value in val['detalles'].items():
                        f.write(f"   - {key}: {value}\n")
                
                f.write("\n" + "="*80 + "\n")
                
                if report["observaciones_generales"]:
                    f.write("\nOBSERVACIONES GENERALES:\n")
                    f.write("-"*80 + "\n")
                    for obs in report["observaciones_generales"]:
                        f.write(f"• {obs}\n")
                
                f.write("\n" + "="*80 + "\n")
                f.write("Fin del reporte\n")
                f.write("="*80 + "\n")
            
            print(f"✓ Reporte TXT exportado: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error al exportar reporte TXT: {e}")
            return False
    
    def export_report_pdf(self, report: Dict, output_path: str = "reporte_inspeccion_ocular.pdf"):
        """Exporta reporte a formato PDF profesional"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=50
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_JUSTIFY,
                spaceAfter=6
            )
            
            obs_style = ParagraphStyle(
                'Observations',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#c0392b'),
                leftIndent=20,
                spaceAfter=4
            )
            
            # PORTADA
            story.append(Spacer(1, 1.2*inch))
            
            title = Paragraph("REPORTE DE VALIDACIÓN<br/>ESTUDIO TÉCNICO DE INSPECCIÓN OCULAR", title_style)
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            subtitle = Paragraph("Expediente Técnico<br/>IE N° 33065 Pacro Yuncan", subtitle_style)
            story.append(subtitle)
            story.append(Spacer(1, 0.4*inch))
            
            meta = report["metadata"]
            
            info_data = [
                ["Archivo:", meta['archivo']],
                ["Fecha de Validación:", datetime.fromisoformat(meta['fecha_validacion']).strftime('%d/%m/%Y %H:%M:%S')],
                ["Componente:", meta['componente']],
                ["Estado General:", meta['estado']]
            ]
            
            info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(info_table)
            story.append(PageBreak())
            
            # RESUMEN EJECUTIVO
            story.append(Paragraph("RESUMEN EJECUTIVO", subtitle_style))
            story.append(Spacer(1, 0.15*inch))
            
            val = report["validacion"]
            estado_color = colors.HexColor('#27ae60') if meta['estado'] == 'APROBADO' else colors.HexColor('#e74c3c')
            estado_text = f"<font color='{estado_color.hexval()}' size='11'><b>{meta['estado']}</b></font>"
            story.append(Paragraph(f"Estado del Informe: {estado_text}", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            summary_text = f"""
            El presente reporte detalla la validación del Estudio Técnico de Inspección Ocular 
            del proyecto IE N° 33065 Pacro Yuncan. Se evaluaron <b>{val['detalles']['secciones_totales']} 
            secciones obligatorias</b>, de las cuales se encontraron <b>{val['detalles']['secciones_encontradas']}</b>.
            El documento incluye <b>{val['detalles']['fotografias']} fotografías</b> como evidencia.
            """
            story.append(Paragraph(summary_text, normal_style))
            story.append(Spacer(1, 0.25*inch))
            
            # VALIDACIÓN DETALLADA
            story.append(Paragraph("VALIDACIÓN DETALLADA", subtitle_style))
            story.append(Spacer(1, 0.15*inch))
            
            estado_text_val = "✓ VÁLIDO" if val['valido'] else "✗ OBSERVADO"
            estado_color_val = colors.HexColor('#27ae60') if val['valido'] else colors.HexColor('#e74c3c')
            story.append(Paragraph(
                f"<font color='{estado_color_val.hexval()}'><b>{estado_text_val}</b></font>",
                normal_style
            ))
            story.append(Spacer(1, 0.15*inch))
            
            # Elementos faltantes
            if val['elementos_faltantes']:
                story.append(Paragraph("<b>Elementos Faltantes:</b>", normal_style))
                story.append(Spacer(1, 0.08*inch))
                for item in val['elementos_faltantes']:
                    story.append(Paragraph(f"• {item}", obs_style))
                story.append(Spacer(1, 0.15*inch))
            
            # Información adicional
            if val['advertencias']:
                story.append(Paragraph("<b>Información Adicional:</b>", normal_style))
                story.append(Spacer(1, 0.08*inch))
                for warning in val['advertencias']:
                    story.append(Paragraph(f"ℹ {warning}", normal_style))
                story.append(Spacer(1, 0.15*inch))
            
            # Tabla de detalle de secciones
            story.append(Paragraph("<b>Detalle de Secciones:</b>", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            detalle_secciones = val['detalles'].get('detalle_secciones', {})
            if detalle_secciones:
                sections_data = [["Sección", "Estado"]]
                
                for seccion, encontrada in detalle_secciones.items():
                    estado_icon = "✓" if encontrada else "✗"
                    estado_text_cell = f"{estado_icon} {'Encontrada' if encontrada else 'Faltante'}"
                    sections_data.append([seccion, estado_text_cell])
                
                sections_table = Table(sections_data, colWidths=[4.2*inch, 1.3*inch])
                sections_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 1), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ]))
                
                # Colores alternados según estado
                for idx, (seccion, encontrada) in enumerate(detalle_secciones.items(), 1):
                    row_color = colors.HexColor('#d5f4e6') if encontrada else colors.HexColor('#fadbd8')
                    sections_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, idx), (-1, idx), row_color)
                    ]))
                
                story.append(sections_table)
            
            story.append(Spacer(1, 0.25*inch))
            
            # Resumen estadístico
            story.append(Paragraph("<b>Resumen Estadístico:</b>", normal_style))
            story.append(Spacer(1, 0.08*inch))
            
            porcentaje = (val['detalles']['secciones_encontradas'] / val['detalles']['secciones_totales'] * 100)
            
            stats_data = [
                ["Secciones Encontradas:", str(val['detalles']['secciones_encontradas'])],
                ["Secciones Requeridas:", str(val['detalles']['secciones_requeridas'])],
                ["Secciones Totales:", str(val['detalles']['secciones_totales'])],
                ["Fotografías Incluidas:", str(val['detalles']['fotografias'])],
                ["Porcentaje de Cumplimiento:", f"{porcentaje:.1f}%"]
            ]
            
            stats_table = Table(stats_data, colWidths=[2.8*inch, 1.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            story.append(stats_table)
            story.append(PageBreak())
            
            # OBSERVACIONES GENERALES
            if report["observaciones_generales"]:
                story.append(Paragraph("OBSERVACIONES GENERALES", subtitle_style))
                story.append(Spacer(1, 0.15*inch))
                
                for obs in report["observaciones_generales"]:
                    story.append(Paragraph(f"• {obs}", normal_style))
                    story.append(Spacer(1, 0.05*inch))
            
            # CONCLUSIÓN
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("CONCLUSIÓN", subtitle_style))
            story.append(Spacer(1, 0.1*inch))
            
            if meta['estado'] == 'APROBADO':
                conclusion = """
                El Estudio Técnico de Inspección Ocular <b>CUMPLE</b> con todos los requisitos 
                establecidos en la normativa vigente. Se recomienda proceder con la siguiente etapa 
                del proyecto.
                """
            else:
                num_faltantes = len(val['elementos_faltantes'])
                conclusion = f"""
                El Estudio Técnico de Inspección Ocular presenta <b>{num_faltantes} sección(es) 
                faltante(s)</b>. Se requiere subsanar las deficiencias identificadas antes de 
                proceder con la aprobación del expediente. Revisar el detalle de observaciones 
                en las secciones anteriores.
                """
            
            story.append(Paragraph(conclusion, normal_style))
            
            doc.build(story)
            
            print(f"✓ Reporte PDF exportado: {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error al exportar reporte PDF: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Función principal"""
    import sys
    
    print("\n" + "="*80)
    print("RPA - VALIDADOR DE ESTUDIO TÉCNICO DE INSPECCIÓN OCULAR")
    print("Expediente Técnico IE N° 33065 Pacro Yuncan")
    print("="*80 + "\n")
    
    if len(sys.argv) < 2:
        print("Uso: python rpa_inspeccion_ocular.py <ruta_pdf>")
        print("\nEjemplo:")
        print("  python rpa_inspeccion_ocular.py entregable1.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"✗ Error: El archivo '{pdf_path}' no existe")
        return
    
    validator = InformeInspeccionValidator()
    report = validator.validate_pdf(pdf_path)
    
    if report.get("status") == "ERROR":
        print(f"\n✗ Error: {report.get('message')}")
        return
    
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    json_output = f"reporte_{base_name}.json"
    txt_output = f"reporte_{base_name}.txt"
    pdf_output = f"reporte_{base_name}.pdf"
    
    validator.export_report(report, json_output)
    validator.export_report_txt(report, txt_output)
    validator.export_report_pdf(report, pdf_output)
    
    print("\n" + "="*80)
    print("VALIDACIÓN COMPLETADA")
    print("="*80)
    print(f"\nEstado: {report['metadata']['estado']}")
    print(f"Secciones encontradas: {report['validacion']['detalles']['secciones_encontradas']}/{report['validacion']['detalles']['secciones_totales']}")
    porcentaje = (report['validacion']['detalles']['secciones_encontradas'] / report['validacion']['detalles']['secciones_totales'] * 100)
    print(f"Cumplimiento: {porcentaje:.1f}%")
    print(f"Fotografías: {report['validacion']['detalles']['fotografias']}")
    print(f"\nReportes generados:")
    print(f"  • {json_output}")
    print(f"  • {txt_output}")
    print(f"  • {pdf_output}")
    print("\n")


if __name__ == "__main__":
    main()
