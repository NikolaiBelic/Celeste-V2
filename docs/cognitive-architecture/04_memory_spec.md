# CELESTE V2 — Especificación de Memoria

## Objetivo

La memoria debe proporcionar continuidad cognitiva, no solo almacenamiento.

## Tipos de memoria

### Working Memory

Contiene:

- turnos recientes;
- tema actual;
- entidades recientes;
- referencias activas;
- estado temporal de la conversación.

### Memoria semántica

Conocimiento relativamente estable:

- personas conocidas;
- relaciones;
- preferencias;
- hechos persistentes;
- patrones.

### Memoria episódica

Experiencias:

- discusiones;
- viajes;
- compras;
- logros;
- adopciones;
- rupturas;
- conversaciones importantes.

### Historia temporal

Permite saber cómo cambiaron los estados.

### Hipótesis

Almacena interpretaciones no confirmadas.

### Open loops

Mantiene asuntos pendientes y preguntas relevantes.

## Filosofía de escritura

La IA propone operaciones.

El sistema las valida y ejecuta.

Operaciones posibles:

- crear entidad;
- actualizar entidad;
- añadir hecho;
- superseder hecho;
- retractar hecho;
- añadir relación;
- cerrar relación;
- añadir evento;
- añadir episodio;
- añadir hipótesis;
- actualizar hipótesis;
- resolver hipótesis;
- abrir loop;
- cerrar loop;
- fusionar entidades;
- separar entidades mal fusionadas;
- no guardar.

## Relación e historia

Caso:

Laura era pareja actual.

"Lo he dejado con Laura."

Debe:

- finalizar vigencia actual;
- registrar ruptura;
- conservar Laura;
- conservar historia.

No debe:

- borrar Laura;
- mantenerla como pareja activa;
- eliminar el pasado.

## Cambio de trabajo

Memoria:
- trabaja en A.

Nuevo:
- "Hoy he empezado en B."

Debe poder:

- añadir B;
- detectar posible transición;
- mantener A como incierto;
- preguntar si importa.

Si luego dice:
"Sí, dejé A el viernes."

Debe:

- cerrar A;
- mantener historia;
- registrar fecha;
- cerrar loop.

## Episodio de conflicto

"He discutido con mi madre."

Debe poder:

- guardar episodio;
- no alterar automáticamente relación permanente;
- asignar relevancia;
- permitir follow-up.

## Reconciliación

La memoria debe distinguir:

- cambio del mundo;
- corrección;
- duplicado;
- información antigua;
- ambigüedad;
- hechos compatibles;
- conflicto real.

## Importancia

Una memoria candidata puede valorar:

- relevancia inmediata;
- futura;
- emocional;
- identitaria;
- probabilidad de recurrencia;
- necesidad de persistencia.

## Retrieval

La memoria recuperada debe ser selectiva.

Criterios:

- entidades mencionadas;
- alias;
- similitud semántica;
- tema;
- historia reciente;
- estado actual;
- episodios relacionados;
- open loops;
- importancia.

No se debe enviar toda la memoria al LLM.

## Consolidación

Episodios repetidos pueden convertirse en patrones.

Debe conservarse:

- evidencia;
- confianza;
- reversibilidad.

## Olvido

Los episodios triviales pueden:

- perder prioridad;
- resumirse;
- archivarse;
- eliminarse según política.

Los hechos históricos importantes no se tratan igual que los detalles triviales.

## Preguntas que la memoria madura debe poder responder

- ¿Qué es verdad ahora?
- ¿Qué era verdad antes?
- ¿Cuándo cambió?
- ¿Por qué cree Celeste esto?
- ¿Es hecho o inferencia?
- ¿Qué lo contradice?
- ¿Qué queda pendiente?
- ¿Qué episodios soportan un patrón?
