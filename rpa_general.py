"""
RPA para Validación del Primer Entregable - Expediente Técnico
Proyecto: IE N° 33065 Pacro Yuncan
"""


import PyPDF2
import re
import os
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
from reportlab.lib.pagesizes import letter, A4
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


class EntregableValidator:
    """Validador principal del Entregable 1"""
    
    def __init__(self):
        self.estructura_entregable1 = {
            "INFORME_INSPECCION_OCULAR": {
                "secciones_obligatorias": [
                    "ANTECEDENTES",
                    "METODOLOGÍA EMPLEADA PARA LA INSPECCIÓN",
                    "METODOLOGIA EMPLEADA PARA LA INSPECCION",  # Variante sin tilde
                    "UBICACIÓN Y ACCESOS",
                    "UBICACION Y ACCESOS",
                    "INFORMACIÓN RECOGIDA DE CAMPO",
                    "INFORMACION RECOGIDA DE CAMPO",
                    "INFRAESTRUCTURA EXISTENTE",
                    "SERVICIOS BÁSICOS EXISTENTES",
                    "SERVICIOS BASICOS EXISTENTES",
                    "LIBRE DISPONIBILIDAD DE TERRENO",
                    "COMPATIBILIZACIÓN DEL ÁREA A INTERVENIR",
                    "COMPATIBILIZACION DEL AREA A INTERVENIR",
                    "VERIFICACIÓN DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL",
                    "VERIFICACION DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL",
                    "PANEL FOTOGRÁFICO",
                    "PANEL FOTOGRAFICO",
                    "CONCLUSIONES Y RECOMENDACIONES"
                ],
                "minimo_requerido": 11  # Al menos 11 secciones únicas
            },
            
            "ESTUDIO_TOPOGRAFICO": {
                "memoria_descriptiva": {
                    "secciones": [
                        "ANTECEDENTES",
                        "OBJETIVOS Y ALCANCES",
                        "PROCEDIMIENTO TOPOGRÁFICO",
                        "PROCEDIMIENTO TOPOGRAFICO",
                        "DESCRIPCIÓN DE LOS LINDEROS",
                        "DESCRIPCION DE LOS LINDEROS",
                        "DESCRIPCIÓN DE LAS CONSTRUCCIONES EXISTENTES",
                        "DESCRIPCION DE LAS CONSTRUCCIONES EXISTENTES",
                        "DESCRIPCIÓN DE LOS SERVICIOS BÁSICOS",
                        "DESCRIPCION DE LOS SERVICIOS BASICOS",
                        "CUADRO DE DATOS TÉCNICOS",
                        "CUADRO DE DATOS TECNICOS"
                    ],
                    "minimo_requerido": 7
                },
                "anexos_obligatorios": [
                    "PARTIDA REGISTRAL",
                    "CERTIFICADO DE CALIBRACIÓN",
                    "CERTIFICADO DE CALIBRACION",
                    "LIBRETA DE CAMPO",
                    "PANEL FOTOGRÁFICO",
                    "PANEL FOTOGRAFICO",
                    "FICHA DE DESCRIPCIÓN DE BMS",
                    "FICHA DE DESCRIPCION DE BMS"
                ],
                "planos_obligatorios": [
                    "PLANO DE UBICACIÓN Y LOCALIZACIÓN",
                    "PLANO DE UBICACION Y LOCALIZACION",
                    "PLANO PERIMÉTRICO",
                    "PLANO PERIMETRICO",
                    "PLANO TOPOGRÁFICO",
                    "PLANO TOPOGRAFICO",
                    "PLANO TOPOGRÁFICO - SECCIONES",
                    "PLANO TOPOGRAFICO - SECCIONES"
                ],
                "validaciones_especificas": {
                    "minimo_fotografias": 20,
                    "certificado_calibracion_meses": 6,
                    "escalas_validas": ["1/100", "1:100", "1/200", "1:200", "1/500", "1:500"]
                }
            },
            
            "ESTUDIO_DEMOLICION": {
                "memoria_descriptiva": [
                    "ANTECEDENTES Y DESCRIPCIÓN",
                    "ANTECEDENTES Y DESCRIPCION",
                    "ALCANCE DE LA DEMOLICIÓN",
                    "ALCANCE DE LA DEMOLICION",
                    "PROCEDIMIENTOS DE DEMOLICIÓN",
                    "PROCEDIMIENTOS DE DEMOLICION"
                ],
                "informe_tecnico": [
                    "ESTADO DE CONSERVACIÓN",
                    "ESTADO DE CONSERVACION",
                    "SUSTENTO TÉCNICO DE DEMOLICIÓN",
                    "SUSTENTO TECNICO DE DEMOLICION",
                    "VERIFICACIÓN ESTRUCTURAL",
                    "VERIFICACION ESTRUCTURAL"
                ],
                "planos": [
                    "PLANO GENERAL DE INFRAESTRUCTURA EXISTENTE"
                ]
            },
            
            "ESTUDIO_MECANICA_SUELOS": {
                "secciones_principales": [
                    "NOMBRE DEL PROYECTO",
                    "ANTECEDENTES",
                    "UBICACIÓN",
                    "UBICACION",
                    "OBJETIVOS Y ALCANCES",
                    "METODOLOGÍA",
                    "METODOLOGIA",
                    "RESUMEN DE LAS CONDICIONES DE CIMENTACIÓN",
                    "RESUMEN DE LAS CONDICIONES DE CIMENTACION",
                    "INFORMACIÓN PREVIA",
                    "INFORMACION PREVIA",
                    "EXPLORACIÓN DE CAMPO",
                    "EXPLORACION DE CAMPO",
                    "ENSAYOS DE LABORATORIO",
                    "PERFIL DEL SUELO",
                    "NIVEL DE LA NAPA FREÁTICA",
                    "NIVEL DE LA NAPA FREATICA",
                    "ANÁLISIS DE LA CIMENTACIÓN",
                    "ANALISIS DE LA CIMENTACION",
                    "EFECTO DEL SISMO",
                    "PARÁMETROS PARA EL DISEÑO",
                    "PARAMETROS PARA EL DISEÑO",
                    "AGRESIÓN AL SUELO",
                    "AGRESION AL SUELO",
                    "CONCLUSIONES Y RECOMENDACIONES"
                ],
                "minimo_puntos_investigacion": 3
            },
            
            "ESTUDIO_CANTERAS_AGUA": {
                "secciones": [
                    "CANTERAS",
                    "FUENTES DE AGUA",
                    "DISEÑO DE MEZCLA",
                    "DISEÑO DE MEZCLAS"
                ]
            },
            
            "ESTUDIO_DEMANDA": {
                "secciones": [
                    "ANTECEDENTES",
                    "MARCO NORMATIVO",
                    "HORIZONTE DE EVALUACIÓN",
                    "HORIZONTE DE EVALUACION",
                    "ÁREA DE INFLUENCIA",
                    "AREA DE INFLUENCIA",
                    "ANÁLISIS DE LA DEMANDA",
                    "ANALISIS DE LA DEMANDA",
                    "POBLACIÓN DE REFERENCIA",
                    "POBLACION DE REFERENCIA",
                    "POBLACIÓN DEMANDANTE POTENCIAL",
                    "POBLACION DEMANDANTE POTENCIAL",
                    "POBLACIÓN DEMANDANTE EFECTIVA",
                    "POBLACION DEMANDANTE EFECTIVA",
                    "ANÁLISIS DE LA OFERTA",
                    "ANALISIS DE LA OFERTA",
                    "DETERMINACIÓN DE LA BRECHA",
                    "DETERMINACION DE LA BRECHA",
                    "CONCLUSIONES Y RECOMENDACIONES"
                ],
                "minimo_requerido": 10
            },
            
            "ANTEPROYECTO_ARQUITECTURA": {
                "memoria_descriptiva": [
                    "INTRODUCCIÓN",
                    "INTRODUCCION",
                    "GENERALIDADES",
                    "JUSTIFICACIÓN DEL PROYECTO",
                    "JUSTIFICACION DEL PROYECTO",
                    "NOMBRE DEL PROYECTO",
                    "UBICACIÓN GEOGRÁFICA",
                    "UBICACION GEOGRAFICA",
                    "LOCALIZACIÓN EDUCATIVA",
                    "LOCALIZACION EDUCATIVA",
                    "CAPACIDAD EDUCATIVA",
                    "METAS - INFRAESTRUCTURA",
                    "IDENTIFICACIÓN DE MÓDULOS",
                    "IDENTIFICACION DE MODULOS",
                    "TIPO DE INTERVENCIÓN",
                    "TIPO DE INTERVENCION",
                    "UBICACION ESPECÍFICA",
                    "UBICACION ESPECIFICA",
                    "LOCALIZACIÓN Y ENTORNO URBANO",
                    "LOCALIZACION Y ENTORNO URBANO",
                    "TERRENO",
                    "INFRAESTRUCTURA EXISTENTE",
                    "CRITERIOS DE DISEÑO",
                    "DESCRIPCIÓN DEL PROYECTO",
                    "DESCRIPCION DEL PROYECTO",
                    "ZONIFICACIÓN",
                    "ZONIFICACION",
                    "NORMATIVIDAD",
                    "CRITERIOS GENERALES DE DISEÑO",
                    "PROGRAMACIÓN ARQUITECTONICA",
                    "PROGRAMACION ARQUITECTONICA"
                ],
                "memoria_calculo": [
                    "ANTECEDENTES",
                    "OBJETIVOS",
                    "NORMATIVIDAD",
                    "CRITERIOS Y REQUISITOS DE SEGURIDAD",
                    "MEDIOS DE EVACUACIÓN",
                    "MEDIOS DE EVACUACION",
                    "ZONAS SEGURAS",
                    "UBICACIÓN DE LUCES DE EMERGENCIA",
                    "UBICACION DE LUCES DE EMERGENCIA",
                    "SEÑALIZACIÓN",
                    "SEÑALIZACION",
                    "CONCLUSIONES Y RECOMENDACIONES"
                ],
                "planos_obligatorios": [
                    "PLANO DE LOCALIZACIÓN Y UBICACIÓN",
                    "PLANO DE LOCALIZACION Y UBICACION",
                    "PLANO GENERAL DE EJES Y TERRAZAS",
                    "PLANO DE DISTRIBUCIÓN GENERAL",
                    "PLANO DE DISTRIBUCION GENERAL",
                    "PLANO DE CORTE GENERAL",
                    "PLANO DE ELEVACIÓN GENERAL",
                    "PLANO DE ELEVACION GENERAL"
                ]
            }
        }
        
        self.validation_results = []
    
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
        # Convertir a mayúsculas
        text = text.upper()
        # Eliminar tildes y caracteres especiales
        replacements = {
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'Ñ': 'N', '\n': ' ', '\t': ' '
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Eliminar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def find_sections(self, text: str, sections_list: List[str]) -> Dict[str, bool]:
        """Busca secciones en el texto"""
        text_normalized = self.normalize_text(text)
        found_sections = {}
        
        for section in sections_list:
            section_normalized = self.normalize_text(section)
            # Buscar la sección como título (puede tener números, puntos, etc.)
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
    
    def validate_informe_inspeccion(self, text: str) -> ValidationResult:
        """Valida el Informe de Inspección Ocular"""
        config = self.estructura_entregable1["INFORME_INSPECCION_OCULAR"]
        secciones = config["secciones_obligatorias"]
        
        found_sections = self.find_sections(text, secciones)
        
        # Agrupar variantes y contar únicas
        unique_sections = {}
        section_groups = [
            ["METODOLOGÍA EMPLEADA PARA LA INSPECCIÓN", "METODOLOGIA EMPLEADA PARA LA INSPECCION"],
            ["UBICACIÓN Y ACCESOS", "UBICACION Y ACCESOS"],
            ["INFORMACIÓN RECOGIDA DE CAMPO", "INFORMACION RECOGIDA DE CAMPO"],
            ["SERVICIOS BÁSICOS EXISTENTES", "SERVICIOS BASICOS EXISTENTES"],
            ["COMPATIBILIZACIÓN DEL ÁREA A INTERVENIR", "COMPATIBILIZACION DEL AREA A INTERVENIR"],
            ["VERIFICACIÓN DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL", 
             "VERIFICACION DE DATOS CONSIGNADOS EN LA PARTIDA REGISTRAL"],
            ["PANEL FOTOGRÁFICO", "PANEL FOTOGRAFICO"]
        ]
        
        for section in secciones:
            # Buscar si pertenece a algún grupo
            group_found = False
            for group in section_groups:
                if section in group:
                    group_key = group[0]  # Usar primera variante como clave
                    if group_key not in unique_sections:
                        unique_sections[group_key] = any(found_sections.get(s, False) for s in group)
                    group_found = True
                    break
            
            if not group_found and section not in [s for g in section_groups for s in g]:
                unique_sections[section] = found_sections.get(section, False)
        
        found_count = sum(1 for v in unique_sections.values() if v)
        missing = [k for k, v in unique_sections.items() if not v]
        
        is_valid = found_count >= config["minimo_requerido"]
        
        warnings = []
        if found_count < len(unique_sections):
            warnings.append(f"Se encontraron {found_count}/{len(unique_sections)} secciones")
        
        return ValidationResult(
            component="INFORME TÉCNICO DE INSPECCIÓN OCULAR",
            is_valid=is_valid,
            missing_items=missing,
            warnings=warnings,
            details={
                "secciones_encontradas": found_count,
                "secciones_requeridas": config["minimo_requerido"],
                "secciones_totales": len(unique_sections),
                "detalle_secciones": unique_sections
            }
        )
    
    def validate_estudio_topografico(self, text: str) -> ValidationResult:
        """Valida el Estudio Topográfico"""
        config = self.estructura_entregable1["ESTUDIO_TOPOGRAFICO"]
        
        # Validar memoria descriptiva
        memoria_sections = config["memoria_descriptiva"]["secciones"]
        found_memoria = self.find_sections(text, memoria_sections)
        
        # Validar anexos
        anexos = config["anexos_obligatorios"]
        found_anexos = self.find_sections(text, anexos)
        
        # Validar planos
        planos = config["planos_obligatorios"]
        found_planos = self.find_sections(text, planos)
        
        # Validaciones específicas
        text_normalized = self.normalize_text(text)
        
        # Buscar número de fotografías
        foto_patterns = [
            r'(\d+)\s*FOTOGRAFIAS',
            r'(\d+)\s*FOTOS',
            r'MINIMO\s*(\d+)\s*FOTOGRAFIAS'
        ]
        num_fotos = 0
        for pattern in foto_patterns:
            match = re.search(pattern, text_normalized)
            if match:
                num_fotos = max(num_fotos, int(match.group(1)))
        
        # Buscar certificado de calibración y fecha
        cert_calibracion_found = any(found_anexos.get(a, False) for a in anexos if 'CALIBR' in a)
        cert_date_valid = False
        
        if cert_calibracion_found:
            # Buscar fechas en formato DD/MM/YYYY o similar
            date_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
            dates_found = re.findall(date_pattern, text)
            
            if dates_found:
                today = datetime.now()
                six_months_ago = today - timedelta(days=180)
                
                for date_match in dates_found:
                    try:
                        day, month, year = map(int, date_match)
                        cert_date = datetime(year, month, day)
                        if cert_date >= six_months_ago:
                            cert_date_valid = True
                            break
                    except:
                        continue
        
        # Buscar escalas
        escalas_validas = config["validaciones_especificas"]["escalas_validas"]
        escalas_encontradas = []
        for escala in escalas_validas:
            escala_normalized = self.normalize_text(escala)
            if escala_normalized in text_normalized:
                escalas_encontradas.append(escala)
        
        # Consolidar resultados
        missing_items = []
        warnings = []
        
        # Agrupar secciones de memoria
        memoria_found_count = sum(1 for v in found_memoria.values() if v)
        if memoria_found_count < config["memoria_descriptiva"]["minimo_requerido"]:
            missing_items.append(f"Memoria Descriptiva incompleta ({memoria_found_count}/7 secciones)")
        
        # Anexos
        anexos_found_count = sum(1 for v in found_anexos.values() if v)
        if anexos_found_count < len(set(config["anexos_obligatorios"])) // 2:  # Considerar variantes
            missing_items.append("Anexos incompletos")
        
        # Planos
        planos_found_count = sum(1 for v in found_planos.values() if v)
        if planos_found_count < len(set(config["planos_obligatorios"])) // 2:
            missing_items.append("Planos incompletos")
        
        # Fotografías
        if num_fotos < config["validaciones_especificas"]["minimo_fotografias"]:
            warnings.append(f"Se requieren mínimo 20 fotografías (encontradas: {num_fotos})")
        
        # Certificado de calibración
        if not cert_calibracion_found:
            missing_items.append("Certificado de Calibración no encontrado")
        elif not cert_date_valid:
            warnings.append("Verificar antigüedad del Certificado de Calibración (máx 6 meses)")
        
        # Escalas
        if not escalas_encontradas:
            warnings.append("No se encontraron escalas válidas en planos")
        
        is_valid = (
            memoria_found_count >= config["memoria_descriptiva"]["minimo_requerido"] and
            anexos_found_count >= 3 and
            planos_found_count >= 2 and
            cert_calibracion_found
        )
        
        return ValidationResult(
            component="ESTUDIO TOPOGRÁFICO",
            is_valid=is_valid,
            missing_items=missing_items,
            warnings=warnings,
            details={
                "memoria_descriptiva": {
                    "encontradas": memoria_found_count,
                    "requeridas": config["memoria_descriptiva"]["minimo_requerido"]
                },
                "anexos": {
                    "encontrados": anexos_found_count,
                    "total": len(set(config["anexos_obligatorios"])) // 2
                },
                "planos": {
                    "encontrados": planos_found_count,
                    "total": len(set(config["planos_obligatorios"])) // 2
                },
                "fotografias": num_fotos,
                "escalas_encontradas": escalas_encontradas,
                "cert_calibracion": cert_calibracion_found,
                "cert_fecha_valida": cert_date_valid
            }
        )
    
    def validate_estudio_demolicion(self, text: str) -> ValidationResult:
        """Valida el Estudio de Demolición"""
        config = self.estructura_entregable1["ESTUDIO_DEMOLICION"]
        
        memoria = config["memoria_descriptiva"]
        found_memoria = self.find_sections(text, memoria)
        
        informe = config["informe_tecnico"]
        found_informe = self.find_sections(text, informe)
        
        planos = config["planos"]
        found_planos = self.find_sections(text, planos)
        
        # Contar secciones únicas
        memoria_count = sum(1 for k, v in found_memoria.items() if v and ("DESCRIPCION" in k or "ALCANCE" in k or "PROCEDIMIENTOS" in k))
        informe_count = sum(1 for k, v in found_informe.items() if v and ("ESTADO" in k or "SUSTENTO" in k or "VERIFICACION" in k))
        planos_count = sum(1 for v in found_planos.values() if v)
        
        missing_items = []
        if memoria_count < 2:
            missing_items.append("Memoria Descriptiva incompleta")
        if informe_count < 2:
            missing_items.append("Informe Técnico incompleto")
        if planos_count < 1:
            missing_items.append("Plano General faltante")
        
        is_valid = memoria_count >= 2 and informe_count >= 2 and planos_count >= 1
        
        return ValidationResult(
            component="ESTUDIO DE DEMOLICIÓN",
            is_valid=is_valid,
            missing_items=missing_items,
            warnings=[],
            details={
                "memoria_descriptiva": memoria_count,
                "informe_tecnico": informe_count,
                "planos": planos_count
            }
        )
    
    def validate_mecanica_suelos(self, text: str) -> ValidationResult:
        """Valida el Estudio de Mecánica de Suelos"""
        config = self.estructura_entregable1["ESTUDIO_MECANICA_SUELOS"]
        
        secciones = config["secciones_principales"]
        found_sections = self.find_sections(text, secciones)
        
        # Contar secciones únicas encontradas
        unique_keys = set()
        for key, found in found_sections.items():
            if found:
                # Normalizar clave eliminando tildes y variantes
                normalized_key = self.normalize_text(key)
                unique_keys.add(normalized_key)
        
        sections_found = len(unique_keys)
        
        # Buscar número de puntos de investigación (calicatas)
        text_normalized = self.normalize_text(text)
        puntos_patterns = [
            r'(\d+)\s*PUNTOS?\s*DE\s*INVESTIGACION',
            r'(\d+)\s*CALICATAS?',
            r'(\d+)\s*EXPLORACIONES?'
        ]
        
        num_puntos = 0
        for pattern in puntos_patterns:
            matches = re.findall(pattern, text_normalized)
            if matches:
                num_puntos = max(num_puntos, max(int(m) for m in matches))
        
        missing_items = []
        warnings = []
        
        if sections_found < 10:
            missing_items.append(f"Secciones principales incompletas ({sections_found}/15)")
        
        if num_puntos < config["minimo_puntos_investigacion"]:
            warnings.append(f"Se requieren mínimo 3 puntos de investigación (encontrados: {num_puntos})")
        
        # Verificar anexos específicos
        anexos_requeridos = ["REGISTRO DE EXCAVACIONES", "ENSAYOS DE LABORATORIO"]
        found_anexos = self.find_sections(text, anexos_requeridos)
        anexos_count = sum(1 for v in found_anexos.values() if v)
        
        if anexos_count < 2:
            missing_items.append("Anexos incompletos (Registro Excavaciones y/o Ensayos)")
        
        is_valid = sections_found >= 10 and num_puntos >= 3 and anexos_count >= 2
        
        return ValidationResult(
            component="ESTUDIO DE MECÁNICA DE SUELOS",
            is_valid=is_valid,
            missing_items=missing_items,
            warnings=warnings,
            details={
                "secciones_encontradas": sections_found,
                "puntos_investigacion": num_puntos,
                "anexos": anexos_count
            }
        )
    
    def validate_canteras_agua(self, text: str) -> ValidationResult:
        """Valida el Estudio de Canteras y Fuentes de Agua"""
        config = self.estructura_entregable1["ESTUDIO_CANTERAS_AGUA"]
        
        secciones = config["secciones"]
        found_sections = self.find_sections(text, secciones)
        
        found_count = sum(1 for v in found_sections.values() if v)
        missing = [k for k, v in found_sections.items() if not v]
        
        is_valid = found_count >= 2  # Al menos Canteras y Fuentes de Agua
        
        warnings = []
        if not found_sections.get("DISEÑO DE MEZCLA", False) and not found_sections.get("DISEÑO DE MEZCLAS", False):
            warnings.append("Diseño de Mezcla no encontrado")
        
        return ValidationResult(
            component="ESTUDIO DE CANTERAS Y FUENTES DE AGUA",
            is_valid=is_valid,
            missing_items=missing,
            warnings=warnings,
            details={"secciones_encontradas": found_count}
        )
    
    def validate_estudio_demanda(self, text: str) -> ValidationResult:
        """Valida el Estudio de Demanda"""
        config = self.estructura_entregable1["ESTUDIO_DEMANDA"]
        
        secciones = config["secciones"]
        found_sections = self.find_sections(text, secciones)
        
        # Contar secciones únicas
        unique_found = set()
        section_groups = [
            ["HORIZONTE DE EVALUACIÓN", "HORIZONTE DE EVALUACION"],
            ["ÁREA DE INFLUENCIA", "AREA DE INFLUENCIA"],
            ["ANÁLISIS DE LA DEMANDA", "ANALISIS DE LA DEMANDA"],
            ["POBLACIÓN DE REFERENCIA", "POBLACION DE REFERENCIA"],
            ["POBLACIÓN DEMANDANTE POTENCIAL", "POBLACION DEMANDANTE POTENCIAL"],
            ["POBLACIÓN DEMANDANTE EFECTIVA", "POBLACION DEMANDANTE EFECTIVA"],
            ["ANÁLISIS DE LA OFERTA", "ANALISIS DE LA OFERTA"],
            ["DETERMINACIÓN DE LA BRECHA", "DETERMINACION DE LA BRECHA"]
        ]
        
        for section in secciones:
            group_found = False
            for group in section_groups:
                if section in group:
                    if any(found_sections.get(s, False) for s in group):
                        unique_found.add(group[0])
                    group_found = True
                    break
            
            if not group_found and found_sections.get(section, False):
                unique_found.add(section)
        
        found_count = len(unique_found)
        missing = [k for k in section_groups if k[0] not in unique_found]
        
        # Buscar referencia a ESCALE
        text_normalized = self.normalize_text(text)
        escale_found = "ESCALE" in text_normalized
        
        warnings = []
        if not escale_found:
            warnings.append("No se encontró referencia a datos de ESCALE")
        
        is_valid = found_count >= config["minimo_requerido"]
        
        return ValidationResult(
            component="ESTUDIO DE DEMANDA",
            is_valid=is_valid,
            missing_items=[f"Secciones faltantes: {len(missing)}"] if missing else [],
            warnings=warnings,
            details={
                "secciones_encontradas": found_count,
                "secciones_requeridas": config["minimo_requerido"],
                "referencia_escale": escale_found
            }
        )
    
    def validate_anteproyecto_arquitectura(self, text: str) -> ValidationResult:
        """Valida el Anteproyecto de Arquitectura"""
        config = self.estructura_entregable1["ANTEPROYECTO_ARQUITECTURA"]
        
        # Validar Memoria Descriptiva
        memoria_desc = config["memoria_descriptiva"]
        found_memoria = self.find_sections(text, memoria_desc)
        
        # Validar Memoria de Cálculo
        memoria_calc = config["memoria_calculo"]
        found_calculo = self.find_sections(text, memoria_calc)
        
        # Validar Planos
        planos = config["planos_obligatorios"]
        found_planos = self.find_sections(text, planos)
        
        # Contar secciones únicas
        memoria_desc_count = len(set(k for k, v in found_memoria.items() if v))
        memoria_calc_count = len(set(k for k, v in found_calculo.items() if v))
        planos_count = len(set(k for k, v in found_planos.items() if v))
        
        missing_items = []
        warnings = []
        
        if memoria_desc_count < 15:
            missing_items.append(f"Memoria Descriptiva incompleta ({memoria_desc_count}/26 secciones)")
        
        if memoria_calc_count < 5:
            missing_items.append(f"Memoria de Cálculo incompleta ({memoria_calc_count}/10 secciones)")
        
        if planos_count < 3:
            missing_items.append(f"Planos incompletos ({planos_count}/6 mínimos)")
        
        # Buscar normatividad específica
        text_normalized = self.normalize_text(text)
        normas_requeridas = ["A.010", "A.040", "A.120", "A.130"]
        normas_encontradas = [n for n in normas_requeridas if n in text_normalized]
        
        if len(normas_encontradas) < 3:
            warnings.append(f"Verificar referencias normativas (RNE): {', '.join(normas_requeridas)}")
        
        is_valid = memoria_desc_count >= 15 and memoria_calc_count >= 5 and planos_count >= 3
        
        return ValidationResult(
            component="ANTEPROYECTO DE ARQUITECTURA",
            is_valid=is_valid,
            missing_items=missing_items,
            warnings=warnings,
            details={
                "memoria_descriptiva": {
                    "encontradas": memoria_desc_count,
                    "total": len(set(memoria_desc))
                },
                "memoria_calculo": {
                    "encontradas": memoria_calc_count,
                    "total": len(set(memoria_calc))
                },
                "planos": {
                    "encontrados": planos_count,
                    "total": len(set(planos))
                },
                "normas_encontradas": normas_encontradas
            }
        )
    
    def validate_entregable1(self, pdf_path: str) -> Dict:
        """Valida el Entregable 1 completo"""
        print(f"\n{'='*80}")
        print(f"VALIDACIÓN DEL PRIMER ENTREGABLE")
        print(f"{'='*80}")
        print(f"Archivo: {pdf_path}")
        print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Extraer texto del PDF
        print("Extrayendo texto del PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {
                "status": "ERROR",
                "message": "No se pudo extraer texto del PDF"
            }
        
        print(f"✓ Texto extraído: {len(text)} caracteres\n")
        
        # Ejecutar validaciones
        validations = []
        
        print("Validando componentes...\n")
        
        # 1. Informe de Inspección Ocular
        print("1. Informe Técnico de Inspección Ocular...")
        result1 = self.validate_informe_inspeccion(text)
        validations.append(result1)
        self._print_result(result1)
        
        # 2. Estudio Topográfico
        print("\n2. Estudio Topográfico...")
        result2 = self.validate_estudio_topografico(text)
        validations.append(result2)
        self._print_result(result2)
        
        # 3. Estudio de Demolición
        print("\n3. Estudio de Demolición...")
        result3 = self.validate_estudio_demolicion(text)
        validations.append(result3)
        self._print_result(result3)
        
        # 4. Estudio de Mecánica de Suelos
        print("\n4. Estudio de Mecánica de Suelos...")
        result4 = self.validate_mecanica_suelos(text)
        validations.append(result4)
        self._print_result(result4)
        
        # 5. Estudio de Canteras y Fuentes de Agua
        print("\n5. Estudio de Canteras y Fuentes de Agua...")
        result5 = self.validate_canteras_agua(text)
        validations.append(result5)
        self._print_result(result5)
        
        # 6. Estudio de Demanda
        print("\n6. Estudio de Demanda...")
        result6 = self.validate_estudio_demanda(text)
        validations.append(result6)
        self._print_result(result6)
        
        # 7. Anteproyecto de Arquitectura
        print("\n7. Anteproyecto de Arquitectura...")
        result7 = self.validate_anteproyecto_arquitectura(text)
        validations.append(result7)
        self._print_result(result7)
        
        # Resumen general
        total_valid = sum(1 for v in validations if v.is_valid)
        total_components = len(validations)
        
        print(f"\n{'='*80}")
        print(f"RESUMEN GENERAL")
        print(f"{'='*80}")
        print(f"Componentes válidos: {total_valid}/{total_components}")
        print(f"Estado general: {'✓ APROBADO' if total_valid == total_components else '✗ OBSERVADO'}")
        print(f"{'='*80}\n")
        
        # Generar reporte detallado
        report = {
            "metadata": {
                "archivo": pdf_path,
                "fecha_validacion": datetime.now().isoformat(),
                "total_componentes": total_components,
                "componentes_validos": total_valid,
                "estado": "APROBADO" if total_valid == total_components else "OBSERVADO"
            },
            "validaciones": [
                {
                    "componente": v.component,
                    "valido": v.is_valid,
                    "elementos_faltantes": v.missing_items,
                    "advertencias": v.warnings,
                    "detalles": v.details
                }
                for v in validations
            ],
            "observaciones_generales": self._generate_general_observations(validations)
        }
        
        return report
    
    def _print_result(self, result: ValidationResult):
        """Imprime resultado de validación"""
        status_icon = "✓" if result.is_valid else "✗"
        status_text = "VÁLIDO" if result.is_valid else "OBSERVADO"
        
        print(f"   {status_icon} {status_text}")
        
        if result.missing_items:
            print(f"   Elementos faltantes:")
            for item in result.missing_items:
                print(f"      • {item}")
        
        if result.warnings:
            print(f"   Advertencias:")
            for warning in result.warnings:
                print(f"      ⚠ {warning}")
    
    def _generate_general_observations(self, validations: List[ValidationResult]) -> List[str]:
        """Genera observaciones generales"""
        observations = []
        
        invalid_components = [v for v in validations if not v.is_valid]
        
        if invalid_components:
            observations.append(
                f"Se encontraron {len(invalid_components)} componente(s) con observaciones"
            )
            
            for comp in invalid_components:
                if comp.missing_items:
                    observations.append(
                        f"{comp.component}: {', '.join(comp.missing_items)}"
                    )
        
        # Advertencias generales
        all_warnings = [w for v in validations for w in v.warnings]
        if all_warnings:
            observations.append(f"Total de advertencias: {len(all_warnings)}")
        
        return observations
    
    def export_report(self, report: Dict, output_path: str = "reporte_validacion_entregable1.json"):
        """Exporta reporte a JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Reporte exportado: {output_path}")
            return True
        except Exception as e:
            print(f"\n✗ Error al exportar reporte: {e}")
            return False
    
    def export_report_txt(self, report: Dict, output_path: str = "reporte_validacion_entregable1.txt"):
        """Exporta reporte a formato TXT legible"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE VALIDACIÓN - PRIMER ENTREGABLE\n")
                f.write("="*80 + "\n\n")
                
                # Metadata
                meta = report["metadata"]
                f.write(f"Archivo: {meta['archivo']}\n")
                f.write(f"Fecha: {meta['fecha_validacion']}\n")
                f.write(f"Estado: {meta['estado']}\n")
                f.write(f"Componentes válidos: {meta['componentes_validos']}/{meta['total_componentes']}\n")
                f.write("\n" + "="*80 + "\n\n")
                
                # Validaciones detalladas
                for idx, val in enumerate(report["validaciones"], 1):
                    f.write(f"{idx}. {val['componente']}\n")
                    f.write(f"   Estado: {'✓ VÁLIDO' if val['valido'] else '✗ OBSERVADO'}\n")
                    
                    if val['elementos_faltantes']:
                        f.write(f"\n   Elementos faltantes:\n")
                        for item in val['elementos_faltantes']:
                            f.write(f"      • {item}\n")
                    
                    if val['advertencias']:
                        f.write(f"\n   Advertencias:\n")
                        for warning in val['advertencias']:
                            f.write(f"      ⚠ {warning}\n")
                    
                    if val['detalles']:
                        f.write(f"\n   Detalles:\n")
                        for key, value in val['detalles'].items():
                            f.write(f"      - {key}: {value}\n")
                    
                    f.write("\n" + "-"*80 + "\n\n")
                
                # Observaciones generales
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
    
    def export_report_pdf(self, report: Dict, output_path: str = "reporte_validacion_entregable1.pdf"):
        """Exporta reporte a formato PDF profesional"""
        try:
            # Crear documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=50
            )
            
            # Contenedor para elementos del PDF
            story = []
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            # Estilo para subtítulos
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            # Estilo para texto normal
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#333333'),
                alignment=TA_JUSTIFY,
                spaceAfter=6
            )
            
            # Estilo para observaciones
            obs_style = ParagraphStyle(
                'Observations',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#c0392b'),
                leftIndent=20,
                spaceAfter=4
            )
            
            # ====================
            # PORTADA
            # ====================
            story.append(Spacer(1, 1.5*inch))
            
            title = Paragraph("REPORTE DE VALIDACIÓN<br/>PRIMER ENTREGABLE", title_style)
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            subtitle = Paragraph("Expediente Técnico<br/>IE N° 33065 Pacro Yuncan", subtitle_style)
            story.append(subtitle)
            story.append(Spacer(1, 0.5*inch))
            
            # Información del documento
            meta = report["metadata"]
            
            # Tabla de información general
            info_data = [
                ["Archivo:", meta['archivo']],
                ["Fecha de Validación:", datetime.fromisoformat(meta['fecha_validacion']).strftime('%d/%m/%Y %H:%M:%S')],
                ["Estado General:", meta['estado']],
                ["Componentes Válidos:", f"{meta['componentes_validos']} de {meta['total_componentes']}"]
            ]
            
            info_table = Table(info_data, colWidths=[2.5*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(info_table)
            story.append(PageBreak())
            
            # ====================
            # RESUMEN EJECUTIVO
            # ====================
            story.append(Paragraph("RESUMEN EJECUTIVO", subtitle_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Estado general
            estado_color = colors.HexColor('#27ae60') if meta['estado'] == 'APROBADO' else colors.HexColor('#e74c3c')
            estado_text = f"<font color='{estado_color.hexval()}' size='12'><b>{meta['estado']}</b></font>"
            story.append(Paragraph(f"Estado del Entregable: {estado_text}", normal_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Resumen de validaciones
            summary_text = f"""
            El presente reporte detalla la validación del Primer Entregable del Expediente Técnico 
            del proyecto IE N° 33065 Pacro Yuncan. Se evaluaron <b>{meta['total_componentes']} componentes</b> 
            principales, de los cuales <b>{meta['componentes_validos']} resultaron válidos</b>.
            """
            story.append(Paragraph(summary_text, normal_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Tabla de resumen de componentes
            summary_data = [["N°", "Componente", "Estado"]]
            
            for idx, val in enumerate(report["validaciones"], 1):
                estado_icon = "✓" if val['valido'] else "✗"
                
                summary_data.append([
                    str(idx),
                    val['componente'],
                    f"{estado_icon} {'VÁLIDO' if val['valido'] else 'OBSERVADO'}"
                ])
            
            summary_table = Table(summary_data, colWidths=[0.5*inch, 4.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            
            # Aplicar colores a filas según estado
            for idx, val in enumerate(report["validaciones"], 1):
                row_color = colors.HexColor('#d5f4e6') if val['valido'] else colors.HexColor('#fadbd8')
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, idx), (-1, idx), row_color)
                ]))
            
            story.append(summary_table)
            story.append(PageBreak())
            
            # ====================
            # VALIDACIONES DETALLADAS
            # ====================
            story.append(Paragraph("VALIDACIONES DETALLADAS", subtitle_style))
            story.append(Spacer(1, 0.2*inch))
            
            for idx, val in enumerate(report["validaciones"], 1):
                # Título del componente
                comp_title = f"{idx}. {val['componente']}"
                story.append(Paragraph(comp_title, subtitle_style))
                
                # Estado
                estado_text = "✓ VÁLIDO" if val['valido'] else "✗ OBSERVADO"
                estado_color = colors.HexColor('#27ae60') if val['valido'] else colors.HexColor('#e74c3c')
                story.append(Paragraph(
                    f"<font color='{estado_color.hexval()}'><b>{estado_text}</b></font>",
                    normal_style
                ))
                story.append(Spacer(1, 0.1*inch))
                
                # Elementos faltantes
                if val['elementos_faltantes']:
                    story.append(Paragraph("<b>Elementos Faltantes:</b>", normal_style))
                    for item in val['elementos_faltantes']:
                        story.append(Paragraph(f"• {item}", obs_style))
                    story.append(Spacer(1, 0.1*inch))
                
                # Advertencias
                if val['advertencias']:
                    story.append(Paragraph("<b>Advertencias:</b>", normal_style))
                    for warning in val['advertencias']:
                        story.append(Paragraph(f"⚠ {warning}", obs_style))
                    story.append(Spacer(1, 0.1*inch))
                
                # Detalles
                if val['detalles']:
                    story.append(Paragraph("<b>Detalles:</b>", normal_style))
                    
                    details_data = []
                    for key, value in val['detalles'].items():
                        # Formatear valor
                        if isinstance(value, dict):
                            value_str = ", ".join([f"{k}: {v}" for k, v in value.items()])
                        elif isinstance(value, list):
                            value_str = ", ".join(str(v) for v in value)
                        elif isinstance(value, bool):
                            value_str = "Sí" if value else "No"
                        else:
                            value_str = str(value)
                        
                        details_data.append([key.replace('_', ' ').title(), value_str])
                    
                    if details_data:
                        details_table = Table(details_data, colWidths=[2.5*inch, 3.5*inch])
                        details_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('TOPPADDING', (0, 0), (-1, -1), 4),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ]))
                        story.append(details_table)
                
                story.append(Spacer(1, 0.2*inch))
                
                # Separador entre componentes
                if idx < len(report["validaciones"]):
                    story.append(Paragraph("<hr/>", normal_style))
                    story.append(Spacer(1, 0.1*inch))
            
            story.append(PageBreak())
            
            # ====================
            # OBSERVACIONES GENERALES
            # ====================
            if report["observaciones_generales"]:
                story.append(Paragraph("OBSERVACIONES GENERALES", subtitle_style))
                story.append(Spacer(1, 0.2*inch))
                
                for obs in report["observaciones_generales"]:
                    story.append(Paragraph(f"• {obs}", obs_style))
                    story.append(Spacer(1, 0.05*inch))
            
            # ====================
            # CONCLUSIÓN
            # ====================
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("CONCLUSIÓN", subtitle_style))
            story.append(Spacer(1, 0.1*inch))
            
            if meta['estado'] == 'APROBADO':
                conclusion = """
                El Primer Entregable del Expediente Técnico <b>CUMPLE</b> con todos los requisitos 
                establecidos en la normativa vigente. Se recomienda proceder con la siguiente etapa 
                del proyecto.
                """
            else:
                componentes_observados = meta['total_componentes'] - meta['componentes_validos']
                conclusion = f"""
                El Primer Entregable presenta <b>{componentes_observados} componente(s) con observaciones</b>. 
                Se requiere subsanar las deficiencias identificadas antes de proceder con la aprobación 
                del expediente. Revisar el detalle de observaciones en las secciones anteriores.
                """
            
            story.append(Paragraph(conclusion, normal_style))
            
            # Construir PDF
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
    print("RPA - VALIDADOR DE ENTREGABLE 1")
    print("Expediente Técnico IE N° 33065 Pacro Yuncan")
    print("="*80 + "\n")
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python rpa_validador.py <ruta_pdf>")
        print("\nEjemplo:")
        print("  python rpa_validador.py entregable1.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    # Verificar que el archivo existe
    if not os.path.exists(pdf_path):
        print(f"✗ Error: El archivo '{pdf_path}' no existe")
        return
    
    # Crear validador
    validator = EntregableValidator()
    
    # Ejecutar validación
    report = validator.validate_entregable1(pdf_path)
    
    if report.get("status") == "ERROR":
        print(f"\n✗ Error: {report.get('message')}")
        return
    
    # Exportar reportes
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
    print(f"Componentes válidos: {report['metadata']['componentes_validos']}/{report['metadata']['total_componentes']}")
    print(f"\nReportes generados:")
    print(f"  • {json_output}")
    print(f"  • {txt_output}")
    print(f"  • {pdf_output}")
    print("\n")



if __name__ == "__main__":
    main()
