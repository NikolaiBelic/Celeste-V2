# CELESTE V2 — Especificación de Deliberación

## Objetivo

La deliberación decide qué significa el mensaje respecto a lo que Celeste ya sabe y qué debería hacer.

Es el corazón de:

`mensaje → interpretación → intención propia → respuesta`

## Entradas

- mensaje actual;
- interpretación;
- contexto conversacional;
- memoria relevante;
- estado actual;
- historia;
- hipótesis;
- open loops;
- herramientas disponibles.

## Preguntas cognitivas

Celeste debe poder considerar:

- ¿Qué está pasando?
- ¿Es importante?
- ¿Ha cambiado algo?
- ¿Es compatible con lo anterior?
- ¿Hay contradicción?
- ¿Es una corrección?
- ¿Es evento o estado persistente?
- ¿Merece memoria?
- ¿Debe existir una entidad?
- ¿Debo mantener incertidumbre?
- ¿Falta información importante?
- ¿Debo preguntar ahora?
- ¿Conviene preguntar más adelante?
- ¿Solo debo responder?
- ¿Debo responder y preguntar?
- ¿Debo ejecutar una acción?

## Salida

La deliberación produce decisiones estructuradas, no una cadena de pensamiento libre.

Puede producir:

- propuestas de memoria;
- cambios de incertidumbre;
- open loops;
- intención conversacional;
- solicitud de acción;
- necesidad de aclaración;
- confianza.

## Curiosidad humana

"He adoptado un perro."

Puede generar:

- relevancia alta;
- entidad persistente probable;
- nombre desconocido;
- intención: reconocer + preguntar el nombre.

"He discutido con mi madre."

Puede generar:

- episodio relevante;
- no alterar relación permanente;
- intención: reconocer + preguntar qué ocurrió.

No existe una regla "argumento → pregunta por qué". La pregunta sale de la relevancia y el hueco informativo.

## No preguntar todo

"Me he comprado unas zapatillas."

Celeste no debe interrogar automáticamente por:

- marca;
- talla;
- precio;
- color;
- tienda.

La utilidad de una pregunta depende de:

- valor conversacional;
- importancia;
- contexto emocional;
- intención del usuario;
- coste de interrupción.

## Contradicciones

Memoria:
- trabaja en A.

Nuevo:
- empieza en B.

Posible deliberación:

- añadir B;
- mantener A;
- marcar compatibilidad desconocida;
- preguntar si es relevante.

No:
- terminar A automáticamente.

## Profundidad

### Ligera

- saludos;
- respuestas triviales;
- consultas sencillas.

### Normal

- conversación ordinaria;
- actualizaciones personales simples;
- preferencias.

### Profunda

- contradicciones;
- transiciones vitales;
- eventos emocionales;
- ambigüedad;
- correcciones;
- múltiples implicaciones.

## Seguridad

La deliberación propone.

El validador comprueba:

- identidad;
- temporalidad;
- evidencia;
- ambigüedad;
- integridad de memoria.

## Evaluación

No se evalúa por texto exacto, sino por comportamiento:

- ¿entendió el cambio?
- ¿evitó asumir?
- ¿mantuvo incertidumbre?
- ¿preguntó solo cuando era útil?
- ¿preservó historia?
- ¿produjo decisiones generales?
