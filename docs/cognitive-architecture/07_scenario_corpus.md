# CELESTE V2 — Corpus de Escenarios Canónicos

Este documento es un examen para la arquitectura, no una lista de reglas.

Pregunta de evaluación:

> ¿Puede la misma arquitectura general resolver este escenario sin código específico del dominio?

# A. Relaciones

## A1 — Ruptura

Memoria:
- Laura es pareja actual.

Usuario:
"Lo he dejado con Laura."

Debe:
- comprender ruptura completada;
- cerrar relación activa;
- conservar historia;
- registrar evento;
- mantener entidad Laura.

No debe:
- borrar Laura;
- mantenerla como pareja actual;
- eliminar historia.

## A2 — Reconciliación

Memoria:
- relación con Laura terminó.

Usuario:
"Laura y yo hemos vuelto."

Debe:
- registrar reconciliación;
- crear nuevo intervalo activo;
- conservar ruptura previa.

## A3 — Ambigüedad romántica

Usuario:
"Estoy viendo mucho a Marta."

Debe:
- evitar confirmar relación;
- quizá mantener hipótesis;
- conservar incertidumbre.

## A4 — Nueva pareja explícita

Usuario:
"Marta es mi novia."

Debe:
- resolver/crear Marta;
- interpretar relación actual;
- comparar con relaciones activas previas;
- deliberar si existe conflicto.

# B. Trabajo

## B1 — Nuevo trabajo

Memoria:
- trabaja en Empresa A.

Usuario:
"Hoy he empezado en Empresa B."

Debe:
- registrar inicio de B;
- no terminar A automáticamente;
- detectar posible transición;
- preguntar si merece la pena.

## B2 — Transición explícita

Usuario:
"Dejé A el viernes y hoy he empezado en B."

Debe:
- cerrar A;
- abrir B;
- mantener historia;
- interpretar tiempo.

## B3 — Dos empleos

Usuario:
"Voy a compaginar los dos trabajos."

Debe:
- mantener ambos activos;
- cerrar ambigüedad previa.

# C. Familia

## C1 — Discusión

Usuario:
"He discutido con mi madre."

Debe:
- episodio de conflicto;
- no cambiar relación permanente;
- entender relevancia;
- poder preguntar qué ocurrió.

## C2 — Patrón recurrente

Historia:
- varias discusiones similares.

Usuario:
"Siempre discutimos por lo mismo."

Debe:
- posible patrón semántico;
- mantener evidencia;
- confianza gradual.

## C3 — Ruptura relacional

Usuario:
"Ya no me hablo con mi madre."

Debe:
- cambio persistente;
- conservar historia;
- diferenciarlo de una discusión aislada.

# D. Mascotas

## D1 — Adopción

Usuario:
"He adoptado un perro."

Debe:
- registrar adopción;
- posible entidad persistente;
- relación con usuario;
- loop por nombre;
- pregunta natural posible.

## D2 — Nombre contextual

Turno anterior:
- perro recién adoptado.

Usuario:
"Se llama Nala."

Debe:
- resolver referencia al perro;
- actualizar nombre;
- cerrar loop.

## D3 — Muerte

Memoria:
- Nala es mascota actual.

Usuario:
"Ha muerto Nala."

Debe:
- evento de muerte;
- finalizar estado actual;
- mantener Nala históricamente;
- alta relevancia emocional.

# E. Gustos

## E1 — Preferencia

Usuario:
"Me encanta el sushi."

Debe:
- guardar preferencia;
- no necesitar entidad persistente para sushi.

## E2 — Cambio

Memoria:
- le gusta sushi.

Usuario:
"Últimamente no lo soporto."

Debe:
- resolver referencia si contexto claro;
- actualizar preferencia actual;
- conservar historia.

## E3 — Comparación

Usuario:
"Ahora prefiero ramen."

Debe:
- añadir/actualizar preferencia;
- no borrar automáticamente todos los demás gustos.

# F. Planes

## F1 — Consideración

Usuario:
"Estoy pensando mudarme a Madrid."

Debe:
- intención;
- no cambiar residencia actual.

## F2 — Paso avanzado

Usuario:
"Ya he firmado el alquiler en Madrid."

Debe:
- elevar probabilidad de cambio futuro;
- no asumir que ya vive allí si no se dijo.

## F3 — Cancelación

Usuario:
"Al final no me mudo."

Debe:
- cancelar intención;
- no crear mudanza completada.

# G. Correcciones

## G1 — Corrección explícita

Memoria:
- Laura vive en Madrid.

Usuario:
"Te dije Madrid, pero me equivoqué. Vive en Getafe."

Debe:
- retractar/corregir memoria;
- no tratarlo como mudanza.

## G2 — Cambio real

Memoria:
- Laura vive en Madrid.

Usuario:
"Laura se ha mudado a Getafe."

Debe:
- conservar Madrid históricamente;
- actualizar estado actual;
- registrar mudanza.

# H. Identidad

## H1 — Dos Lauras

Memoria:
- Laura A trabaja en Tiendanimal.
- Laura B es otra persona.

Usuario:
"Laura, la de Tiendanimal, me escribió."

Debe:
- resolver Laura A.

## H2 — Pronombre contextual

Turno previo:
- Laura es la persona relevante.

Usuario:
"Luego ella me llamó."

Debe:
- resolver ella → Laura.

## H3 — Ambigüedad

Turno previo:
- Laura y Marta igualmente relevantes.

Usuario:
"Luego ella me llamó."

Debe:
- no adivinar;
- mantener ambigüedad;
- quizá preguntar.

# I. Episodios e importancia

## I1 — Trivial

Usuario:
"Se me ha caído el tenedor."

Debe:
- entender;
- normalmente no persistir.

## I2 — Compra significativa

Usuario:
"Me he comprado mi primer coche."

Debe:
- evento importante;
- posible entidad vehículo;
- relación de propiedad.

## I3 — Logro

Usuario:
"Por fin he aprobado la oposición."

Debe:
- episodio importante;
- posible objetivo completado;
- respuesta celebratoria.

# J. Hipótesis

## J1 — Especulación

Usuario:
"Creo que Marta está enfadada conmigo."

Debe:
- creencia atribuida al usuario;
- no convertirla en hecho sobre Marta.

## J2 — Evidencia contraria

Después:
"Marta me ha dicho que no está enfadada."

Debe:
- debilitar/rechazar hipótesis previa;
- preservar que existió.

# K. Open loops

## K1 — Trabajo anterior pendiente

Memoria:
- empezó B;
- estado de A desconocido.

Más tarde:
- conversación vuelve al trabajo.

Debe:
- poder recuperar loop;
- follow-up natural posible.

## K2 — Cierre de loop

Celeste:
"¿Al final dejaste A?"

Usuario:
"Sí, el viernes."

Debe:
- interpretar respuesta con contexto;
- cerrar A;
- cerrar loop;
- conservar historia.

# L. Conversación

## L1 — Saludo

Usuario:
"Hola."

Debe:
- ruta ligera;
- respuesta simple.

## L2 — Responder y preguntar

Usuario:
"He discutido con mi madre."

Debe:
- reconocer;
- poder preguntar.

## L3 — No interrogar

Usuario:
"Me he comprado unas zapatillas."

Debe:
- responder naturalmente;
- no intentar completar marca, talla, precio, color, etc.

# M. Stress tests multidominio

## M1

Usuario:
"Dejé el trabajo la semana pasada, he vuelto con Laura y estamos pensando adoptar otro perro."

Debe:
- separar múltiples eventos;
- entender tiempo;
- cerrar trabajo;
- reactivar relación;
- representar adopción como intención;
- no crear mascota como ya adoptada.

## M2

Memoria:
- Nala es mascota;
- trabaja en A;
- Laura es pareja.

Usuario:
"Nala está enferma, hoy he empezado en B y Laura y yo estamos fatal."

Debe:
- separar tres temas;
- priorizar respuesta;
- no asumir ruptura;
- detectar ambigüedad laboral;
- episodio de salud de mascota;
- mantener coherencia.

# N. Dimensiones de evaluación

Cada escenario se puntuará por:

1. comprensión semántica;
2. resolución de identidad;
3. temporalidad;
4. incertidumbre;
5. estado actual;
6. conservación histórica;
7. relevancia de memoria;
8. calidad de preguntas;
9. ausencia de suposiciones;
10. naturalidad;
11. independencia de dominio;
12. resistencia a contradicciones.

# O. Expansión futura

El corpus crecerá hacia 50–100+ escenarios:

- relaciones;
- familia;
- trabajo;
- estudios;
- conversaciones sobre salud;
- viajes;
- posesiones;
- mascotas;
- hobbies;
- videojuegos;
- finanzas;
- proyectos;
- planes;
- correcciones;
- bromas;
- sarcasmo;
- hipótesis;
- emociones;
- múltiples temas;
- retrieval;
- cambios de opinión;
- referencias indirectas;
- evidencia contradictoria.

El corpus sirve para examinar el cerebro de Celeste, no para decirle cómo responder caso por caso.
