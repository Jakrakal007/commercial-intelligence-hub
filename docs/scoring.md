# Puntaje de prioridad comercial

Fecha fija de evaluación: 2026-09-21. Una fila representa una oportunidad.

Para `Open`, se suman seis componentes y se redondea a dos decimales:

| Componente | Regla | Máximo |
| --- | --- | --- |
| Etapa | Evaluación 5; Reunión 10; Propuesta 18; Negociación 25 | 25 |
| Probabilidad registrada | Probabilidad entre 0 y 1 multiplicada por 25 | 25 |
| Contacto reciente | Hasta 7 días: 20; 14: 16; 30: 12; 60: 6; 90: 2; más de 90: 0 | 20 |
| Antigüedad | Hasta 30 días: 10; 60: 8; 90: 6; 120: 3; más de 120: 0 | 10 |
| Monto | Menos de 50 000: 2; 100 000: 4; 180 000: 6; 250 000: 8; desde 250 000: 10 | 10 |
| Cierre esperado | Sin vencimiento: 10; hasta 30 días vencido: 5; más de 30: 0 | 10 |

El riesgo es LOW desde 70 puntos, MEDIUM desde 45 y por debajo de 70, y HIGH por debajo de 45.

Las cerradas reciben una regla especial: `Won` = 100/LOW y `Lost` = 0/HIGH. Sus componentes se guardan en cero como no aplicables. Para priorización y riesgo comercial activo, analizar únicamente `Open`.

El monto representa prioridad económica. La probabilidad es un dato sintético registrado, no una estimación aprendida. El método no entrena modelos ni demuestra resultados comerciales reales.
