# CELESTE V2 — Plan de Implementación Cognitiva

## Regla

No avanzar por features de dominio.

Avanzar por capacidades cognitivas generales.

## Etapa 1 — Congelar baseline

- conservar los tests actuales;
- no eliminar componentes funcionales;
- etiquetar el estado actual como baseline pre-cognitive-loop.

## Etapa 2 — Convertir corpus en pruebas de comportamiento

Crear tests de escenarios que validen:
- interpretación;
- no-asunción;
- temporalidad;
- memoria;
- incertidumbre;
- iniciativa conversacional.

No exigir texto exacto.

## Etapa 3 — Interpretation v2

Mejorar la representación semántica para soportar:
- estados;
- transiciones;
- eventos;
- intenciones;
- hipótesis;
- correcciones;
- negación;
- temporalidad;
- relevancia social/emocional;
- referencias.

## Etapa 4 — Retrieval

Construir MemoryRetriever:
- por entidades;
- relaciones;
- tema;
- similitud semántica;
- historia;
- open loops;
- importancia.

## Etapa 5 — Local World Model

Construir para cada turno una vista temporal y coherente de:
- entidades relevantes;
- relaciones;
- hechos;
- historia;
- hipótesis;
- contradicciones.

## Etapa 6 — Deliberation Engine

La IA recibe:
- interpretación;
- estado local;
- memoria relevante;
- contexto.

Produce:
- interpretación contextual enriquecida;
- incertidumbres;
- curiosidades;
- intención conversacional;
- propuestas de memoria.

## Etapa 7 — Memory Decision Validation

Validar:
- identidad;
- temporalidad;
- ambigüedad;
- historia;
- procedencia;
- confianza;
- operaciones destructivas.

## Etapa 8 — Memory Executor

Ejecutar operaciones aprobadas:
- crear;
- relacionar;
- finalizar;
- superseder;
- retractar;
- registrar episodio;
- hipótesis;
- loops.

## Etapa 9 — Conversation Planner

Decidir:
- responder;
- preguntar;
- responder + preguntar;
- aclarar;
- actuar;
- retomar tema;
- tono abstracto;
- profundidad.

## Etapa 10 — Response Generator

Generar lenguaje a partir de la intención.

Separar:
- contenido;
- personalidad;
- tono;
- estilo.

## Etapa 11 — Reflection / Consolidation

Después del turno:
- consolidar patrones;
- ajustar confianza;
- cerrar loops;
- reducir relevancia;
- resumir episodios;
- mantener historia.

## Etapa 12 — Cognitive Router

Elegir profundidad:
- light;
- standard;
- deep.

No usar deliberación completa para todo.

## Etapa 13 — Persistencia real

Solo cuando el modelo cognitivo sea estable:
- PostgreSQL;
- índices;
- búsqueda semántica;
- temporalidad;
- auditoría;
- migraciones.

## Etapa 14 — Evaluación continua

Mantener:
- unit tests;
- integration tests;
- scenario tests;
- regression corpus;
- tests con modelo real;
- métricas de suposición incorrecta;
- métricas de memoria conflictiva;
- métricas de preguntas innecesarias.

## Orden inmediato recomendado

1. Crear framework de scenario tests.
2. Formalizar 15–20 escenarios iniciales.
3. Ejecutarlos contra Understanding actual.
4. Medir fallos reales.
5. Rediseñar Interpretation v2 a partir de esos fallos.
6. No construir todavía el Deliberation Engine final.
