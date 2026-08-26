# CELESTE V2 — Principios Cognitivos

## Misión

Construir un asistente que se aproxime al comportamiento de una mente coherente: que interprete, recuerde, dude, relacione, decida, pregunte, responda, cambie de opinión y mantenga continuidad en el tiempo.

No pretendemos simular literalmente una persona. Pretendemos construir una arquitectura general capaz de producir comportamientos humanos coherentes en conversación.

## Principio rector

> Celeste no debe ser una colección de reglas sobre dominios de la vida. Debe ser un sistema general de operaciones cognitivas.

No queremos lógica central del tipo:

- `if novia`
- `if perro`
- `if trabajo`
- `if madre`
- `if sushi`

Queremos abstracciones generales:

- entidades;
- relaciones;
- estados;
- hechos;
- eventos;
- episodios;
- preferencias;
- intenciones;
- hipótesis;
- contradicciones;
- incertidumbre;
- preguntas abiertas;
- objetivos conversacionales.

## Reparto de responsabilidades

### La IA decide semánticamente

Puede:

- interpretar significado;
- inferir implicaciones;
- detectar ambigüedad;
- proponer cambios de memoria;
- decidir si conviene preguntar;
- formar hipótesis;
- revisar hipótesis;
- decidir la intención del turno.

### El sistema ejecuta con seguridad

Debe:

- validar identidades;
- preservar historia;
- mantener integridad temporal;
- evitar escrituras destructivas ambiguas;
- validar cambios;
- persistir datos;
- recuperar recuerdos relevantes;
- mantener trazabilidad.

El LLM nunca debe tener acceso libre para modificar directamente la base de datos.

## La memoria no es JSON

Los modelos Pydantic y las estructuras JSON son contratos internos entre módulos.

No son la memoria final.

La memoria persistente debe permitir identidad, relaciones, tiempo, historia, hipótesis, eventos, episodios, correcciones, procedencia y confianza.

## El presente no borra el pasado

Ejemplo:

- Laura fue pareja del usuario.
- La relación terminó.
- Más tarde apareció Marta.

No debe existir solo:

`pareja = Marta`

Debe conservarse:

- la relación histórica con Laura;
- su final;
- la relación actual con Marta;
- fechas e incertidumbre cuando proceda.

## La incertidumbre es una capacidad, no un error

Celeste debe poder mantener:

- hecho confirmado;
- creencia probable;
- hipótesis débil;
- ambigüedad;
- contradicción;
- desconocimiento.

Ejemplo:

"Estoy viendo mucho a Marta."

No implica automáticamente:

`Marta = pareja`

Celeste debe poder concluir:

> No tengo evidencia suficiente todavía.

## No asumir incompatibilidades

"He empezado en otra empresa."

no implica automáticamente:

"He dejado mi empresa anterior."

"Tengo otro perro."

no implica que el anterior ya no exista.

Las incompatibilidades deben interpretarse, no codificarse universalmente.

## Preguntar antes que inventar

Si un cambio puede afectar al modelo del mundo pero existe ambigüedad relevante, Celeste debe poder preguntar de forma natural.

Ejemplo:

Memoria:
- trabaja en Empresa A.

Nuevo:
- "Hoy he empezado en Empresa B."

Posible respuesta:
- reconocer el nuevo trabajo;
- preguntar si dejó A o compagina ambos.

## No todo merece memoria a largo plazo

"Se me ha caído el tenedor."

Normalmente no necesita persistencia.

"He adoptado un perro."

Probablemente sí.

"He discutido con mi madre."

Puede ser memoria episódica sin convertirse en un cambio permanente de relación.

## La conversación es una acción

Antes de generar texto, Celeste debe decidir qué quiere hacer:

- responder;
- preguntar;
- responder y preguntar;
- aclarar;
- retomar un asunto;
- ejecutar una acción;
- mantener la respuesta mínima;
- profundizar.

## Separar contenido de personalidad

Primero:

> ¿Qué quiero comunicar?

Después:

> ¿Cómo lo diría Celeste?

La personalidad nunca debe decidir qué es verdad o qué se borra de la memoria.

## Profundidad cognitiva adaptativa

"Hola" puede ir por ruta ligera.

"Creo que me equivoqué dejando a Laura, pero ahora estoy con otra persona."

puede necesitar recuperación de historia, deliberación profunda, incertidumbre y planificación.

## Ciclo cognitivo objetivo

1. Percepción
2. Contexto
3. Recuerdo
4. Interpretación
5. Deliberación
6. Intención propia
7. Respuesta / acción
8. Reflexión / consolidación

## Reglas constitucionales

1. No hardcodear dominios concretos como núcleo.
2. No crear diccionarios infinitos de frases.
3. No convertir inferencias en hechos.
4. No borrar historia para actualizar presente.
5. No asumir incompatibilidad sin evidencia.
6. No guardar todo.
7. No permitir al LLM modificar la BD directamente.
8. No depender de una única salida libre del LLM.
9. No convertir JSON en la memoria.
10. No usar razonamiento máximo para cada mensaje.
11. No rellenar huecos inventando.
12. Preferir incertidumbre o aclaración.
13. Mantener procedencia de cambios relevantes.
14. Hacer las decisiones cognitivas comprobables.
15. Evaluar con escenarios humanos de dominios distintos.
