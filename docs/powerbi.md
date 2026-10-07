# Apertura y revisión del informe

Abrir `powerbi/Commercial_Intelligence_Hub_Espanol.pbix` en Power BI Desktop. La revisión de archivos encontró las tablas `commercial_dataset` y `DimStage` en el diagrama, y 22 visuales distribuidos en tres páginas. Las definiciones de medidas y relaciones deben confirmarse desde Power BI.

Si se necesita actualizar el origen, localizar la consulta `commercial_dataset` en Power Query y cambiar el archivo de origen al CSV `output/commercial_dataset.csv` de la copia local. Conservar los pasos posteriores y asignar tipos de datos explícitos: identificadores y categorías como texto, fechas ISO como fechas y montos/probabilidades/puntajes como números. No se verificó la consulta interna del modelo comprimido durante la revisión de archivos.

Para revisar o actualizar una copia:

1. Abrir las tres páginas y comprobar que todos los visuales cargan.
2. Revisar las medidas DAX reales y sus filtros. Comparar sus resultados sin filtros con los valores de referencia del CSV documentados en `verification.md`.
3. Confirmar que riesgo activo y pipeline excluyen `Won` y `Lost`.
4. Revisar que la tasa de cierre tenga una definición explícita. La referencia del CSV usa ganadas / (ganadas + perdidas).
5. Revisar las interacciones entre gráficos y el orden de las etapas de `DimStage`.
6. Revisar los gráficos por empresa que agregan días de antigüedad o de contacto. Sumar días deja de representar la antigüedad de una oportunidad si hay varias oportunidades para una misma empresa.
7. Capturar una vista completa y legible de cada página. Usar `resumen-ejecutivo.png`, `embudo-comercial.png` y `priorizacion-oportunidades.png` en una carpeta `screenshots/`.

Se revisaron las tres capturas proporcionadas por el usuario y se contrastaron los valores visibles con el CSV. También se comprobaron los filtros corregidos en el archivo guardado. La actualización del origen en otro equipo y las fórmulas DAX internas no se verificaron de forma automatizada.
