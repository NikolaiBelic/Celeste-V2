# CELESTE V2 — Modelo de Estado Cognitivo

## Objetivo

Definir qué necesita tener "en mente" Celeste durante un turno sin convertir todo en memoria permanente.

## Estado cognitivo de un turno

Conceptualmente, un turno debe poder reunir:

### 1. Percepción actual
- mensaje;
- actos de habla;
- entidades mencionadas;
- referencias;
- eventos;
- hechos;
- intenciones;
- negaciones;
- temporalidad;
- emociones o señales sociales relevantes.

### 2. Contexto conversacional
- turnos recientes;
- pregunta anterior;
- respuesta esperada;
- tema actual;
- subtemas;
- entidades salientes;
- tono reciente;
- tarea activa.

### 3. Memoria recuperada
Solo memoria relevante:
- estado actual;
- historia;
- episodios;
- preferencias;
- hipótesis;
- open loops;
- relaciones.

### 4. Modelo del mundo local
La porción del mundo relevante para este turno:
- entidades;
- relaciones;
- estados;
- intervalos temporales;
- incompatibilidades posibles;
- hechos inciertos.

### 5. Hipótesis activas
Interpretaciones que Celeste considera posibles pero no confirmadas.

### 6. Tensiones / conflictos
- contradicciones;
- ambigüedades;
- cambios posibles;
- identidades dudosas;
- temporalidad incompleta.

### 7. Curiosidades
No son simplemente datos ausentes.

Una curiosidad contiene:
- qué falta;
- por qué interesa;
- utilidad;
- oportunidad de preguntar;
- tono adecuado;
- prioridad.

### 8. Intención del turno
Qué decide hacer Celeste:
- responder;
- preguntar;
- responder + preguntar;
- aclarar;
- actuar;
- retomar;
- no profundizar.

### 9. Propuestas de memoria
Cambios que la IA considera adecuados, aún no ejecutados.

### 10. Resultado validado
Solo después de validación:
- operaciones aprobadas;
- operaciones rechazadas;
- dudas que permanecen.

---

## Principio de localidad

Celeste no debe cargar todo lo que sabe.

Debe construir un "estado cognitivo local" con lo relevante para el turno.

Esto reduce:
- ruido;
- latencia;
- contradicciones accidentales;
- coste de contexto;
- sobreinterpretación.

---

## Estado actual vs memoria

El estado cognitivo es efímero.

La memoria persistente es duradera.

Una hipótesis puede existir durante un turno sin convertirse en memoria.

Una curiosidad puede desaparecer si deja de ser relevante.

Una interpretación puede ser corregida antes de ejecutar cualquier cambio.

---

## Flujo

Mensaje
→ Percepción
→ Contexto
→ Recall
→ Estado cognitivo local
→ Deliberación
→ Intención
→ Validación
→ Respuesta/acción
→ Consolidación selectiva
