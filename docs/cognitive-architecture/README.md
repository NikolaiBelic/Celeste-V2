# CELESTE V2 — Cognitive Architecture v1

Esta carpeta define la arquitectura cognitiva objetivo de Celeste V2.

Flujo rector:

`mensaje → interpretación → contexto → recuerdo → deliberación → intención propia → respuesta/acción → reflexión/memoria`

## Documentos

1. `01_cognitive_principles.md`
2. `02_knowledge_model.md`
3. `03_interpretation_spec.md`
4. `04_memory_spec.md`
5. `05_deliberation_spec.md`
6. `06_conversation_spec.md`
7. `07_scenario_corpus.md`

## Regla de desarrollo

Antes de implementar una nueva conducta cognitiva hay que comprobar si es una capacidad general o un parche de dominio.

Si el núcleo necesita reglas tipo `if novia`, `if perro`, `if trabajo`, hay que revisar la abstracción.

## v1.1 — Curiosidad e iniciativa

La arquitectura incorpora explícitamente:

- curiosidad conversacional;
- iniciativa propia;
- responder + preguntar;
- curiosidad de preocupación;
- curiosidad juguetona/cómplice;
- selección contextual del tono;
- decisión de cuándo NO preguntar;
- open loops motivados por relevancia, no por campos vacíos.

## Documentos añadidos en v1.2

8. `08_behavioral_contract.md` — Contrato general para convertir escenarios humanos en expectativas verificables.
9. `09_cognitive_state_model.md` — Qué mantiene Celeste "en mente" durante un turno.
10. `10_implementation_plan.md` — Orden de construcción del nuevo núcleo cognitivo.
