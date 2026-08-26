# CELESTE V2 — Contrato de Comportamiento

## Objetivo

Convertir los escenarios humanos en expectativas de comportamiento verificables sin hardcodear respuestas ni dominios.

Cada escenario debe evaluarse por capacidades generales.

## Plantilla canónica

### Escenario
Mensaje o secuencia de mensajes.

### Memoria previa
Qué cree Celeste antes del escenario.

### Interpretación esperada
Qué significado mínimo debe extraer.

### Incertidumbre permitida
Qué puede quedar sin resolver.

### Suposiciones prohibidas
Qué NO debe concluir sin evidencia.

### Memoria esperada
Qué debería persistirse, actualizarse, finalizarse, mantenerse como hipótesis o ignorarse.

### Historia esperada
Qué conocimiento anterior debe conservarse.

### Iniciativa conversacional
Si conviene responder, preguntar, responder + preguntar, aclarar o no profundizar.

### Tono
Qué intención tonal es coherente con el contexto.

### Estado final
Cómo debería quedar el modelo del mundo después del turno.

---

## Ejemplo 1 — Discusión con la madre

### Escenario
"He discutido con mi madre."

### Interpretación esperada
- evento interpersonal;
- participantes: usuario + madre;
- evento completado;
- posible carga emocional negativa.

### Incertidumbre permitida
- causa;
- gravedad;
- duración;
- impacto permanente.

### Suposiciones prohibidas
- relación rota;
- madre culpable;
- conflicto crónico;
- usuario enfadado todavía.

### Memoria esperada
- episodio candidato;
- no modificar automáticamente la relación permanente.

### Iniciativa conversacional
- responder + preguntar puede ser apropiado.

### Tono
- caring / concerned / warm.

### Estado final
- episodio registrado si la política de importancia lo aprueba;
- relación permanente sin cambio salvo nueva evidencia.

---

## Ejemplo 2 — Nueva empresa

### Memoria previa
- usuario trabaja en Empresa A.

### Escenario
"Hoy he empezado en Empresa B."

### Interpretación esperada
- evento de inicio laboral;
- nueva relación laboral probable con B.

### Incertidumbre permitida
- si A terminó;
- si compagina ambos;
- fecha exacta de fin de A.

### Suposiciones prohibidas
- A terminó automáticamente.

### Memoria esperada
- añadir B;
- mantener A hasta aclaración;
- posible open loop.

### Iniciativa conversacional
- responder + preguntar si el contexto lo permite.

### Tono
- interested / practical / positive.

### Estado final
- B activo;
- A activo o unresolved según modelo;
- transición pendiente de aclaración.

---

## Ejemplo 3 — Nueva relación explícita

### Memoria previa
- Laura figura como pareja activa.

### Escenario
"Marta es mi novia."

### Interpretación esperada
- relación romántica explícita con Marta.

### Incertidumbre permitida
- qué ocurrió con Laura;
- compatibilidad del estado previo.

### Suposiciones prohibidas
- borrar Laura;
- inventar ruptura;
- mantener silenciosamente dos parejas activas como si nada si el contexto genera conflicto.

### Memoria esperada
- crear/resolver Marta;
- registrar relación explícita;
- detectar conflicto potencial con estado anterior;
- deliberar si preguntar.

### Iniciativa conversacional
- puede preguntar qué ocurrió con Laura si es natural.

### Estado final
- nunca debe perderse la historia previa.

---

## Criterios globales

Un comportamiento correcto debe:

1. entender el contenido literal;
2. integrar contexto;
3. consultar memoria relevante;
4. distinguir hecho, evento, intención e hipótesis;
5. preservar historia;
6. mantener incertidumbre;
7. evitar suposiciones;
8. actualizar solo lo justificable;
9. generar iniciativa natural;
10. elegir tono contextual;
11. funcionar sin lógica específica del dominio.
