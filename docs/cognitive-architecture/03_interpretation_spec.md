# CELESTE V2 — Especificación de Interpretación

## Objetivo

Transformar lenguaje natural en comprensión situacional.

No basta con extraer entidades y claims.

Celeste debe intentar entender:

- qué ocurrió;
- quién hizo qué;
- qué cambió;
- cuándo;
- si es presente, pasado o futuro;
- si es hecho, opinión, intención, posibilidad o corrección;
- qué referencias dependen del contexto;
- qué parte es segura y qué parte es inferencia;
- qué puede tener relevancia emocional o social;
- qué espera el usuario de la conversación.

## Actos de habla

Debe reconocer, entre otros:

- informar;
- preguntar;
- solicitar;
- corregir;
- confirmar;
- negar;
- especular;
- reflexionar;
- bromear;
- saludar.

Un mismo turno puede contener varios.

## Temporalidad

Debe distinguir:

- estado actual;
- pasado;
- futuro;
- tiempo relativo;
- rangos;
- tiempo relativo a otro evento;
- tiempo desconocido.

Ejemplos:

"Vivo en Alicante." → estado actual.

"Viví en Alicante." → histórico.

"Me mudaré a Alicante." → futuro.

"Me mudé hace dos semanas." → evento completado.

## Cambios de estado

"Ya no trabajo allí."

No es solo un hecho negativo.

Puede representar el final de un estado previo.

"Empiezo mañana en otra empresa."

Puede representar un estado futuro.

## Corrección vs cambio real

"Te dije que Laura vivía en Madrid, pero me equivoqué. Vive en Getafe."

→ la memoria anterior era incorrecta.

"Laura se ha mudado de Madrid a Getafe."

→ la memoria anterior pudo ser correcta y el mundo cambió.

## Intención vs acción completada

"Estoy pensando dejar a Laura."
→ consideración.

"Voy a dejar a Laura."
→ intención futura.

"He dejado a Laura."
→ evento completado.

"Pensé en dejar a Laura."
→ pensamiento pasado.

## Referencias

Debe conservar expresiones como:

- ella;
- él;
- eso;
- el otro;
- la de Tiendanimal;
- lo de ayer.

Primero se reconocen como referencias. Después se resuelven usando contexto y memoria.

## Grounding

No debe inventar participantes, entidades ni relaciones para completar estructuras.

La información debe poder anclarse en:

- el mensaje;
- el contexto;
- la memoria recuperada.

## Relevancia emocional y social

"He discutido con mi madre."

Puede entenderse como:

- conflicto interpersonal;
- carga probablemente negativa;
- episodio relevante;
- sin evidencia de ruptura permanente.

## Categorías semánticas

La interpretación debe poder representar:

- hecho;
- relación;
- evento;
- corrección;
- intención;
- preferencia;
- opinión;
- hipótesis;
- incertidumbre;
- solicitud;
- objetivo;
- pregunta pendiente.

## Ejemplos

### He adoptado un perro

- evento completado;
- usuario participante;
- nueva entidad probable;
- alta relevancia futura;
- identidad todavía incompleta;
- pregunta natural posible.

### He discutido con mi madre

- evento de conflicto;
- participantes user + madre;
- probablemente episódico;
- no implica deterioro permanente;
- follow-up potencial.

### Ya no me hablo con mi madre

- cambio de estado relacional;
- persistencia mayor;
- historia previa debe conservarse.

### Hoy he empezado en Microsoft

- inicio de empleo;
- nueva relación laboral probable;
- compatibilidad con empleo anterior desconocida;
- posible necesidad de aclaración.

## Fallos que debemos evitar

- intención convertida en acción completada;
- una discusión convertida en relación mala permanente;
- "estoy viendo a alguien" convertido en pareja formal;
- personas con mismo nombre fusionadas sin evidencia;
- nuevo empleo = fin automático del anterior;
- pérdida de negación;
- pérdida de tiempo verbal;
- participantes inventados;
- correcciones ignoradas;
- historia convertida en estado actual.
