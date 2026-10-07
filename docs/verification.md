# Verificación de archivos y datos

Revisión realizada el 7 de octubre de 2026. Fecha de corte de los datos: 21 de septiembre de 2026.

- Fuentes encontradas: 250 leads, 120 oportunidades y 400 actividades.
- Se recalcularon las 120 filas con `calculate_scores.py` y se compararon todos sus campos con el CSV guardado. Coinciden con tolerancia numérica de 0,000001.
- Las validaciones del servicio de cálculo comprobaron identificadores, relación con leads, fechas, estados, componentes y límites del puntaje.
- Se confirmó la presencia de las tres páginas del informe.
- La copia del .pbix conserva el mismo SHA-256 que el archivo original en español.

## Referencia calculada desde el CSV

Estos valores sirven para contrastar el informe sin filtros. No son resultados leídos de sus medidas DAX.

| Métrica | Valor |
| --- | ---: |
| Oportunidades abiertas | 76 |
| Ganadas | 26 |
| Perdidas | 18 |
| Monto potencial abierto (PEN) | 8,916,000 |
| Ganadas / (ganadas + perdidas) | 59.09% |
| Puntaje promedio de abiertas | 35.52 |
| Abiertas con riesgo LOW | 1 |
| Abiertas con riesgo MEDIUM | 26 |
| Abiertas con riesgo HIGH | 49 |

## Revisión de las tres capturas

Resumen Ejecutivo: 76 oportunidades abiertas, tasa de cierre de 59,1 %, puntaje promedio de 35,5 y 49 oportunidades abiertas de alto riesgo. El pipeline de 8.916.000 PEN aparece redondeado a 8.92M. Coinciden con los valores de referencia del CSV al redondeo mostrado.

Embudo Comercial y Desempeño: 44 oportunidades cerradas, de las cuales 26 son ganadas y 18 perdidas. Los conteos por ejecutivo y las tasas de cierre visibles coinciden con el CSV. El gráfico de contacto pendiente se corrigió para excluir oportunidades cerradas; sus seis empresas visibles y días sin contacto coinciden con las primeras seis filas Open ordenadas por esa métrica.

Priorización de Oportunidades: las tarjetas coinciden con las referencias anteriores. Las primeras filas muestran Servicios Aurora Perú SAC (71,00/LOW), Tecnología Prisma Integral SAC (68,00/MEDIUM), Servicios Solaris del Norte SAC y Tecnología Horizonte Central SAC (ambas 62,50/MEDIUM). La tabla sigue el orden descendente del puntaje y usa verde, amarillo y rojo para LOW, MEDIUM y HIGH.

## Archivo final guardado

- Se incorporó el .pbix guardado tras los cambios y se verificó que su copia coincide por SHA-256 con el original actualizado.
- El gráfico de contacto pendiente contiene las condiciones result = Open y days_since_last_contact > 30.
- El pipeline contiene precisión de dos decimales.
- La página de priorización contiene el filtro result = Open.
- Se incluyeron las tres capturas y se comprobaron los enlaces locales del README.

## Alcance de la verificación

Las comprobaciones de datos se ejecutaron desde Python. La revisión visual utiliza capturas proporcionadas por el usuario; no se automatizó Power BI Desktop ni se inspeccionaron las fórmulas internas del modelo comprimido. Los valores visibles concordantes y los filtros guardados no sustituyen una prueba de actualización del origen en otro equipo. Para esa actualización, consultar powerbi.md.
