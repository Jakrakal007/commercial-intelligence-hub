# Diccionario de datos

Las tablas de `data/` contienen 250 leads, 120 oportunidades y 400 actividades generadas con Python. La salida enriquecida contiene 120 oportunidades enriquecidas y puntuadas. Fechas ISO `YYYY-MM-DD`, texto UTF-8, montos en PEN y probabilidad decimal de 0 a 1. Las claves son únicas en su tabla. El generador actual incluye al menos un contacto por entidad y deriva `last_contact_date` del historial.

## data/leads.csv

| Campo | Tipo | Descripción |
| --- | --- | --- |
| lead_id | Texto | Identificador único del lead |
| company_name | Texto | Nombre ficticio de empresa |
| contact_name | Texto | Nombre ficticio del contacto |
| sector | Texto | Sector comercial |
| city | Texto | Ciudad |
| lead_source | Texto | LinkedIn, Referido, Website, Evento, Email o Prospección directa |
| assigned_executive | Texto | Ejecutivo responsable ficticio |
| created_date | Fecha | Alta del lead |
| last_contact_date | Fecha nullable | Último contacto; vacío si no existe |
| status | Texto | Nuevo, Contactado, Calificado, Descartado o Convertido |

Sectores previstos: Retail, Minería, Construcción, Tecnología, Agroindustria, Servicios, Logística, Manufactura y Turismo.

Ejecutivos ficticios previstos: Andrea Torres, Carlos Mendoza, Lucía Vega y Diego Salazar.

## data/opportunities.csv

| Campo | Tipo | Descripción |
| --- | --- | --- |
| opportunity_id | Texto | Identificador único de oportunidad |
| lead_id | Texto | Referencia al lead de origen |
| company_name | Texto | Empresa del lead relacionado |
| assigned_executive | Texto | Ejecutivo responsable |
| product | Texto | Producto de inversión |
| stage | Texto | Evaluación, Reunión, Propuesta, Negociación o Cerrado |
| potential_amount | Decimal | Monto potencial entre 20000 y 500000 soles |
| probability | Decimal | Probabilidad entre 0 y 1; Won = 1 y Lost = 0 |
| created_date | Fecha | Creación de oportunidad, no anterior al lead |
| expected_close_date | Fecha | Fecha prevista de cierre |
| last_contact_date | Fecha nullable | Último contacto asociado con la oportunidad |
| closed_date | Fecha nullable | Cierre real; vacío para Open |
| result | Texto | Open, Won o Lost |

Productos previstos: Fondo Conservador, Fondo Balanceado, Fondo Crecimiento, Gestión Patrimonial e Inversión Corporativa.

## data/activities.csv

| Campo | Tipo | Descripción |
| --- | --- | --- |
| activity_id | Texto | Identificador único de actividad |
| lead_id | Texto | Lead relacionado |
| opportunity_id | Texto nullable | Oportunidad relacionada; vacío para seguimiento solo de lead |
| executive | Texto | Ejecutivo que realiza la actividad |
| activity_type | Texto | Llamada, Email, Reunión, Seguimiento, Presentación o Propuesta enviada |
| activity_date | Fecha | Fecha de actividad, no anterior a las entidades relacionadas |
| notes | Texto | Nota comercial ficticia |

## output/commercial_dataset.csv

Conserva todas las columnas y valores originales de oportunidades, en el mismo orden, y añade los siguientes. Una fila por oportunidad, sin incorporar filas de actividades.

| Campo adicional | Tipo | Descripción |
| --- | --- | --- |
| sector | Texto | Sector del lead relacionado |
| city | Texto | Ciudad del lead relacionado |
| lead_source | Texto | Fuente del lead relacionado |
| lead_status | Texto | Estado del lead relacionado |
| score_date | Fecha | Fecha de corte explícita del cálculo |
| days_since_last_contact | Entero | Días sin contacto a la fecha de corte; el scoring exige un contacto válido |
| opportunity_age_days | Entero | Días desde creación a la fecha de evaluación |
| days_overdue | Entero | Máximo entre cero y días desde cierre esperado al corte |
| stage_score | Número | Puntos por etapa; máximo 25 |
| probability_score | Número | probability × 25 para Open; máximo 25 |
| recency_score | Número | Puntos por contacto reciente; máximo 20 |
| age_score | Número | Puntos por antigüedad; máximo 10 |
| deal_value_score | Número | Prioridad económica por monto; máximo 10 |
| expected_close_score | Número | Puntos por cumplimiento de fecha estimada; máximo 10 |
| opportunity_score | Decimal | Score determinístico entre 0 y 100 |
| risk_level | Texto | LOW, MEDIUM o HIGH |

El corte es `2026-09-21`. Los seis componentes aplican a Open; en Won/Lost se almacenan como cero (no aplicables), con score final 100/0 y riesgo LOW/HIGH, respectivamente. Para riesgo activo y vencimiento, filtrar Open. Los días en cerradas se calculan igualmente al corte. Consultar las [reglas completas](scoring.md). No se utilizan predicciones ni machine learning.
