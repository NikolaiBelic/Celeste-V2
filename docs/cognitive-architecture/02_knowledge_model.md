# CELESTE V2 — Modelo de Conocimiento

## Objetivo

Representar de forma general el mundo que Celeste cree conocer sin diseñar una base de datos específica para cada dominio de la vida.

## 1. Entidades

Una entidad es algo con identidad persistente.

Ejemplos:

- personas;
- animales;
- lugares;
- organizaciones;
- proyectos;
- dispositivos;
- vehículos;
- documentos;
- juegos;
- objetos;
- conceptos.

No todo sustantivo merece entidad.

"Me gusta el azul."

puede ser un valor de preferencia.

"Estoy jugando a Red Dead Redemption 2."

puede justificar una entidad persistente porque probablemente reaparecerá.

## 2. Identidad

Una entidad puede tener:

- ID estable;
- nombre canónico;
- alias;
- tipo o hipótesis de tipo;
- atributos;
- procedencia;
- confianza;
- relaciones.

La resolución de identidad debe usar:

- nombres;
- alias;
- contexto;
- calificadores;
- relaciones;
- saliencia reciente;
- memoria;
- ambigüedad.

"Laura", "ella", "mi novia", "la de Tiendanimal" pueden ser la misma persona o no.

## 3. Hechos y relaciones

Representan proposiciones relativamente estables.

Ejemplos:

- user lives_in Alicante;
- Laura works_at Tiendanimal;
- user prefers ramen;
- user owns device X.

Cada hecho debería poder guardar:

- sujeto;
- predicado;
- objeto o valor;
- confianza;
- fuente;
- momento de registro;
- vigencia temporal;
- estado.

Estados posibles:

- active;
- superseded;
- retracted;
- uncertain;
- disputed.

## 4. Estado actual e historia

El estado actual responde:

> ¿Qué cree Celeste que es verdad ahora?

La historia responde:

> ¿Qué fue verdad antes?

No son lo mismo.

Una relación puede tener varios intervalos temporales sin borrar ninguno.

## 5. Eventos

Representan cosas que ocurrieron:

- adopción;
- discusión;
- compra;
- ruptura;
- reconciliación;
- inicio de trabajo;
- final de trabajo;
- viaje;
- accidente;
- logro;
- mudanza;
- muerte.

Un evento puede causar un cambio de estado, pero evento y estado son conceptos distintos.

## 6. Episodios

Un episodio es una experiencia recordada.

Puede incluir:

- participantes;
- momento;
- lugar;
- tema;
- importancia;
- relevancia emocional;
- entidades relacionadas;
- fuente conversacional;
- prioridad de retención.

## 7. Creencias e hipótesis

Celeste debe representar interpretaciones no confirmadas.

Ejemplos:

- Marta podría ser interés romántico.
- El usuario quizá quiere cambiar de trabajo.
- Un tema puede estar causando conflictos recurrentes.

Una hipótesis debería tener:

- enunciado;
- confianza;
- evidencia a favor;
- evidencia en contra;
- momento de creación;
- última actualización;
- estado.

Estados:

- open;
- strengthened;
- weakened;
- confirmed;
- rejected;
- unresolved.

## 8. Intenciones y objetivos

"Estoy pensando mudarme."
"Quiero buscar otro trabajo."
"Quizá adopte otro perro."

No son hechos completados.

Deben representarse como intención, plan o posibilidad futura.

## 9. Preferencias

Pueden cambiar con el tiempo.

Ejemplo:

"Me encanta el sushi."

más tarde:

"Últimamente no lo soporto."

Ambas cosas pueden ser verdaderas en momentos distintos.

## 10. Open loops

Son preguntas o huecos relevantes pendientes.

Ejemplos:

- perro nuevo sin nombre;
- nuevo trabajo pero estado del anterior desconocido;
- decisión futura pendiente;
- conflicto mencionado sin desenlace.

Permiten curiosidad y continuidad natural.

## 11. Contradicciones

Una contradicción no debe borrarse inmediatamente.

Puede significar:

- cambio real;
- corrección;
- identidad equivocada;
- información antigua;
- incompatibilidad posible;
- ambigüedad.

## 12. Procedencia

Las memorias importantes deben distinguir si provienen de:

- afirmación explícita del usuario;
- inferencia;
- herramienta;
- fuente externa;
- corrección;
- patrón consolidado.

## 13. Confianza

Conceptualmente:

- 0.95–1.00: muy confirmada;
- 0.60–0.95: probable;
- 0.30–0.60: posible;
- 0.10–0.30: débil;
- 0.00–0.10: muy incierta.

Los umbrales serán configurables.

## 14. Significancia de entidad

Antes de crear una entidad persistente, Celeste debería valorar:

- probabilidad de recurrencia;
- identidad propia;
- relevancia para el usuario;
- relaciones persistentes;
- utilidad futura;
- nivel de grounding.

## 15. Consolidación

Episodios repetidos pueden formar conocimiento semántico.

Ejemplo:

varias discusiones con la madre por X

→ posible patrón:
X es un motivo recurrente de conflicto.

La inferencia debe mantener evidencia, confianza y reversibilidad.

## 16. Olvido

La memoria humana no conserva todo con igual prioridad.

Posibles mecanismos:

- caída de relevancia;
- resumen;
- archivo;
- consolidación;
- eliminación selectiva de episodios triviales.

La historia importante no debe desaparecer silenciosamente.
