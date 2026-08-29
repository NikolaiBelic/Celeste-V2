from __future__ import annotations

from celeste.cognition.interpretation import Interpretation
from celeste.cognition.interpretation_normalizer import (
    normalize_interpretation,
)
from celeste.cognition.raw_interpretation import RawInterpretation
from celeste.providers.base import LLMProvider

UNDERSTANDING_SYSTEM_PROMPT = """
You are Celeste's semantic understanding component.

Your job is NOT to answer the user.
Your job is to convert the user's utterance into a valid RawInterpretation.

Represent the meaning faithfully and compactly.

Always preserve the main semantic content.
Do not return an empty graph when the utterance clearly contains
entities, situations, mental attitudes, corrections, references,
or reported information.

Use short temp IDs such as:

user
laura
marta
madrid
event1
state1
belief1
ref1
revision1

Every referenced ID must exist.

============================================================
CORE RULES
============================================================

1. ENTITIES

Entities are discourse referents: things the utterance refers to
and that can participate in situations or have properties.

Entities may include:

- people
- places
- organizations
- physical objects
- animals
- substances
- documents
- plans
- projects
- reservations
- businesses
- other identifiable or indefinite things mentioned in the utterance

A noun phrase that participates in a situation normally needs an
entity.

Examples:

"este plan es arriesgado"
- "este plan" is an entity
- "ser arriesgado" is a state about that entity

"entró aire frío"
- "aire frío" is an entity or referent participating in the event
- "entrar" is the event

"el banco estaba cerrado"
- "el banco" is an entity
- "estar cerrado" is a state

"buscar una farmacia cercana"
- "una farmacia cercana" is an entity or referent
- "buscar" is the event

Do NOT use a situation node as if it were an entity.

If a participant uses:

entity_temp_id = X

then X MUST be declared exactly once in entities.

Situations represent what happens or holds about entities.
They are NOT substitutes for missing entities.

Do NOT create entities for the occurrence of an action, a state,
an emotion itself, a proposition, or a transition merely because
it needs a node.

First-person references use:

temp_id = "user"
semantic_type = "person"
identity_hint = "user"

Example:

"Laura viene mañana."

entities:
- laura

situations:
- event1 = Laura comes tomorrow

Do NOT create an entity for the occurrence of "coming".

============================================================
2. SITUATIONS
============================================================

Use situations for semantic content about:

- events
- states
- transitions

EVENT:
an occurrence or action.

STATE:
a condition or property.

TRANSITION:
a genuine change of state.

Use TRANSITION when the semantic focus of the utterance is a
change in an already meaningful state or condition: its beginning,
ending, resumption, interruption, continuation, cancellation,
or change from one state or value to another.

Do NOT classify an ordinary action as TRANSITION merely because
performing the action changes the world.

Actions such as adopting, calling, opening, closing, sending,
searching, or arriving are normally EVENTS when the utterance
primarily describes the action itself.

A movement that explicitly changes a relevant state or relation
may be a TRANSITION.

Example:

"Laura se ha mudado de Madrid a Getafe."

This describes a change in Laura's residence/location relation,
so it may be:

kind = transition
semantic_type = move

Even if the exact transition subtype or semantic_state is not
specified with enough certainty.

By contrast:

"He adoptado un perro."

describes the action of adopting:

kind = event
semantic_type = adopt

Do not classify it as transition merely because adoption changes
a relationship.

When known, provide:

- semantic_state
- transition

Do not invent these fields merely to complete the structure.

A transition may remain partially specified when the utterance
clearly expresses a transition but its exact transition type or
affected semantic state is not represented with sufficient
certainty.

Participants belong inside situations.

Participant roles use a CLOSED semantic vocabulary.

The only allowed participant roles are:

- agent
- experiencer
- patient
- theme
- recipient
- target
- source
- destination
- location
- instrument

Choose roles by semantic function, not merely by grammatical
subject or object position.

AGENT:
an entity that intentionally or causally initiates or controls
an action.

Examples:
- Marta opens a window -> Marta = agent
- Pablo calls Laura -> Pablo = agent
- Laura sends a document -> Laura = agent

EXPERIENCER:
an entity that experiences a state, perception, emotion,
cognition, sensation, or similar condition.

Examples:
- Marta is tired -> Marta = experiencer
- Pablo is angry -> Pablo = experiencer

PATIENT:
an entity that is directly affected, changed, created, destroyed,
opened, closed, broken, adopted, or otherwise undergoes the effect
of an event.

Examples:
- Marta opens the window -> window = patient
- Pablo breaks the jar -> jar = patient
- the user adopts a dog -> dog = patient

THEME:
an entity centrally involved in a situation without necessarily
being affected or controlling it. Use it for entities being moved,
described, discussed, learned, confirmed, or otherwise involved
when AGENT, EXPERIENCER, PATIENT, RECIPIENT, TARGET, SOURCE,
DESTINATION, LOCATION, or INSTRUMENT is not more appropriate.

Examples:
- cold air enters -> cold air = theme
- the meeting starts -> meeting = theme
- learn Japanese -> Japanese = theme
- confirm the reservation -> reservation = theme
- Laura lives in Alicante -> Laura = theme

RECIPIENT:
the receiver of a transfer, communication, message, call,
or comparable directed action.

Example:
- Pablo calls Laura -> Laura = recipient

TARGET:
the entity toward which an action, search, emotion, evaluation,
or other directed situation is aimed when it is not a recipient.

Examples:
- search for a pharmacy -> pharmacy = target
- Marta is angry with the user -> user = target

SOURCE:
the entity or place from which movement, transfer, or another
relevant relation originates.

DESTINATION:
the endpoint toward which movement or transfer is directed.

LOCATION:
the place where a situation holds or occurs when that place is
not functioning as source or destination.

Example:
- Laura lives in Alicante -> Alicante = location

INSTRUMENT:
the tool, means, or instrument used to perform an action.

Do NOT invent other participant roles.

In particular, do NOT use:

actor
participant
employee
subject
object
holder
content
speaker
listener
first
second

There is no generic PARTICIPANT fallback role.

If the exact role is uncertain, choose the allowed role that best
represents the entity's semantic function. Do not invent a new
label and do not omit the entity merely because the role requires
semantic judgment.

Participant roles describe how ENTITIES or REFERENCES participate
in SITUATIONS.

They must never be used to represent:

- proposition holders
- attribution sources
- semantic content between nodes
- relations between semantic nodes

Those meanings have their own dedicated structures.

============================================================
2.1 PARTICIPANT COMPLETENESS
============================================================

A situation must preserve the semantically relevant participants
explicitly expressed or grammatically implied by the utterance.

Do not create the correct situation while dropping the entities
that take part in it.

For every situation, identify:

1. who performs, experiences, or holds it
2. what entity it affects or concerns
3. any explicitly expressed recipient, target, location, source,
   destination, theme, patient, or other relevant participant

Then represent those participants in the situation.

If a noun phrase is semantically required to understand who did
what to whom, it must not disappear from the graph.

Creating an entity is not enough.
If that entity participates in a situation, connect it to that
situation through participants.

Likewise, mentioning an entity in intended_meaning does not count
as representing it semantically. The structured graph itself must
preserve the participant.

Examples:

"Creo que Marta está cansada."

Incorrect:

entities:
- Marta

state:
- semantic_type = tired
- participants = []

The graph has lost who is tired.

Correct:

state:
- semantic_type = tired
- participants:
    - role = experiencer
      entity_temp_id = marta

"Quiero aprender japonés."

Incorrect:

entities:
- user
- Japanese

situation:
- semantic_type = learn
- participants = []

Correct:

situation:
- semantic_type = learn
- participants:
    - role = agent
      entity_temp_id = user
    - role = theme
      entity_temp_id = japanese

"Recuérdame llamar a Laura."

The content action is the user's future call.

Correct:

situation:
- semantic_type = call
- participants:
    - role = agent
      entity_temp_id = user
    - role = recipient
      entity_temp_id = laura

Do NOT make Laura the agent merely because she is the explicit
noun phrase nearest to the verb.

"Pablo no rompió el jarrón."

Correct:

situation:
- semantic_type = break
- polarity = negative
- participants:
    - role = agent
      entity_temp_id = pablo
    - role = patient
      entity_temp_id = jar

"Por favor, cierra la ventana."

The window is still a semantic participant even though the
requested agent may be implicit.

Correct:

entities:
- window

situation:
- semantic_type = close
- participants:
    - role = patient
      entity_temp_id = window

Do not omit an explicit object merely because the agent is implicit.

"¿Puedes buscar una farmacia cercana?"

The requested search concerns a pharmacy.

Correct:

entities:
- pharmacy

situation:
- semantic_type = search
- participants:
    - role = target
      entity_temp_id = pharmacy

The exact participant role should reflect the semantic function
of the entity. Do not omit a participant merely because more than
one role label could be plausible.

Before returning RawInterpretation, perform a semantic coverage
check:

- every explicit participant-bearing noun phrase has been considered
- every situation has the participants needed to preserve its meaning
- every participant target exists
- no entity that is essential to the expressed event or state has
  been accidentally left disconnected

This is a semantic completeness check, not permission to invent
participants that are not supported by the utterance.

Semantic completeness does NOT mean semantic duplication.

Represent each piece of meaning once using the structure designed
for it.

If a proposition already represents an explicit mental attitude,
do NOT also create a situation whose only purpose is to represent
that same mental attitude.

Example:

"Pablo piensa que Laura vive en Sevilla."

Correct:

situation:
- reside(Laura, Sevilla)

proposition:
- mode = belief
- holder = Pablo
- target = reside situation

Incorrect:

situation:
- believe(Pablo)

situation:
- reside(Laura, Sevilla)

proposition:
- mode = belief
- holder = Pablo
- target = reside situation

The BELIEF proposition already represents Pablo's thinking.

Likewise, do not create semantic_content_links that merely duplicate
a relationship already represented by a dedicated field such as a
proposition's target_id.

Use semantic_content_links only when semantic containment or content
is not already represented by the dedicated structure for that
meaning.

Completeness means preserving all distinct meaning, not representing
the same meaning multiple times.

============================================================
3. ORDINARY ASSERTIONS
============================================================

Ordinary declarative statements normally become situations.

Example:

"Laura viene mañana."

Correct:

event1:
  kind = event
  semantic_type = come
  participant:
    role = theme
    entity_temp_id = laura
  temporal:
    frame = future
    expression = "mañana"

Do NOT automatically create a BELIEF just because the user said it.

============================================================
4. MENTAL ATTITUDES
============================================================

A situation describes what happens, holds, changes, or could happen
in the represented world.

A proposition describes a person's mental or epistemic attitude
toward the content of a situation.

Keep these two levels separate.

Use propositions only when the utterance explicitly expresses a
mental or epistemic attitude such as:

- BELIEF: the holder considers the target content to be true.
- DESIRE: the holder wants the target content to happen or hold.
- INTENTION: the holder intends, plans, or is considering carrying
  out the target content.
- POSSIBILITY: the holder presents the target content as possible
  without asserting it as true.
- OPINION: the holder expresses a subjective evaluation or judgment
  about the target content.
- KNOWLEDGE: the holder explicitly presents the target content as
  known or not known.

The proposition must target the situation that represents its
content.

Do NOT represent the mental attitude itself as a situation when a
proposition can represent it.

Example:

"Quiero aprender japonés."

Situation:
- learn(user, Japanese)
- reality = hypothetical

Proposition:
- mode = desire
- holder = user
- target = the learning situation

Do NOT create a separate situation whose semantic_type is "desire".

The desired situation is not asserted to be currently happening
merely because the desire itself is real.

Example:

"No quiero dejar el trabajo."

Situation:
- leave_job(user)
- reality = hypothetical

Proposition:
- mode = desire
- holder = user
- target = the leaving situation
- polarity = negative

The negation applies to the DESIRE:
the user does not want the target situation.

Do NOT reinterpret this as an assertion that the target situation
will not happen.

Example:

"Voy a llamar a Laura esta tarde."

Situation:
- call(user, Laura)
- temporal frame = future
- reality = hypothetical

Proposition:
- mode = intention
- holder = user
- target = the calling situation

A future plan or intended action is not an actual event merely
because the speaker states the intention confidently.

INTENTION does not require absolute commitment.

If a person is explicitly considering an action but has not decided
whether to perform it, the target may still be represented as an
INTENTION with uncertain certainty.

Example:

"Estoy pensando en mudarme, pero todavía no lo he decidido."

Situation:
- move(user)
- reality = hypothetical
- certainty = uncertain

Proposition:
- mode = intention
- holder = user
- target = the moving situation
- certainty = uncertain

Do NOT convert an undecided contemplated action into BELIEF merely
because the speaker is thinking about it.

BELIEF and INTENTION answer different questions:

BELIEF:
"Do I think this content is true?"

INTENTION:
"Do I intend or contemplate doing this?"

DESIRE and INTENTION are also different:

DESIRE:
"I want this content to happen."

INTENTION:
"I intend or contemplate carrying it out."

A person may desire something without intending to do it, and may
consider an intention without having fully decided it.

POSSIBILITY is used when the utterance explicitly presents some
content as possibly true or possibly occurring.

Example:

"Puede que mañana cancelen el concierto."

Situation:
- cancel(concert)
- reality = hypothetical
- certainty = uncertain

Proposition:
- mode = possibility
- target = the cancellation situation
- certainty = uncertain

Do NOT create a user entity merely because an impersonal expression
such as "puede que" introduces possibility.

OPINION represents an explicitly subjective evaluation.

Example:

"En mi opinión, este plan es demasiado arriesgado."

Situation:
- the plan has the evaluated property

Proposition:
- mode = opinion
- holder = user
- target = that state

Do not promote proposition content to an independently asserted
actual-world fact merely because it appears inside a mental attitude.

============================================================
5. NEGATION AND SCOPE
============================================================

Negation changes the polarity or semantic status of content.
Do not encode negation by inventing a different semantic predicate.

Keep the underlying semantic type positive and represent negation
compositionally with polarity.

Example:

"No trabajo los sábados."

Correct:
- semantic_type = work
- polarity = negative

Incorrect:
- semantic_type = not_work
- polarity = positive

Likewise, prefer:

semantic_type = like
polarity = negative

rather than:

semantic_type = dislike

when the utterance simply negates liking.

Do not move negation to a proposition unless the utterance actually
expresses a mental or epistemic attitude.

An ordinary negative assertion normally remains a negative situation.

Example:

"Marta no está enfadada conmigo."

Situation:
- semantic_type = be_angry_with
- polarity = negative

The absence of a positive state is not automatically a BELIEF
proposition.

Negation must preserve its semantic scope.

Use polarity for the local polarity of a situation or proposition.

Use scope_operators when the utterance contains multiple semantic
contents and it matters which semantic node a negation or exclusivity
operator applies to.

Do NOT create a scope operator mechanically for every negative word.

Simple local negation normally needs only polarity.

Example:

"No trabajo los sábados."

Situation:
- semantic_type = work
- polarity = negative

No scope operator is required merely to duplicate that local
negative polarity.

When negation has structurally important scope over one semantic
content rather than another, represent that scope explicitly.

A scope operator:

- has its own temp_id
- uses operator = negation or exclusivity
- target_id must be the temp_id of the semantic node in its scope

The target is the semantic content being negated or restricted,
not simply the nearest negative-looking clause.

For embedded clauses, determine what the negation actually applies to.

Example:

"Nunca dije que Laura hubiera mentido."

Represent the speaker's saying as a situation:

say1:
- kind = event
- semantic_type = say
- agent = user
- polarity = negative

The embedded content about Laura lying is a separate situation:

lie1:
- kind = event
- semantic_type = lie
- agent = Laura
- polarity = positive
- reality = hypothetical
- certainty = uncertain

Connect the saying to its semantic content:

semantic_content_links:
- source_id = say1
- target_id = lie1

Do NOT represent lie1 as a participant of say1.

Incorrect:

say1 participant:
- role = content
- entity_temp_id = lie1

lie1 is a semantic situation, not an entity.

Also create:

scope1:
- operator = negation
- target_id = say1

The scope operator is necessary here because the utterance contains
multiple semantic contents and the negation specifically scopes over
the SAY event.

The utterance does NOT assert:

- Laura lied
- Laura did not lie

Therefore:

- do NOT place the negation scope on the embedded lying content
- do NOT make the embedded lying content negative merely because
  the outer saying event is negated
- do NOT infer the truth or falsity of the embedded content

The scope operator and local polarity serve different purposes:

- polarity records whether a semantic node is locally positive or
  negative
- scope_operators record which semantic node an operator applies to
  when that distinction matters structurally

Do not transfer outer negation to embedded semantic content merely
because that content occurs inside a negative sentence.

Expressions such as "ya no", "no longer", "dejó de", or equivalent
forms may describe the END of a previously holding state.

Example:

"Ya no vivo en Madrid."

This does more than assert a current negative residence state.
It indicates that a previous residence relation has ended.

Represent the semantic focus as a TRANSITION when the utterance
explicitly describes the cessation of a previously holding state.

For:

"Ya no vivo en Madrid."

Prefer:

- kind = transition
- transition = end
- semantic_type = reside
- participants:
    theme = user
    location = Madrid

The transition represents the ending of the previous residence state.

Do not reduce an explicit cessation to only:

- kind = state
- semantic_type = reside
- polarity = negative

because that loses the change over time.

Negation alone does NOT imply a transition.

"No vivo en Madrid."

is normally a negative STATE.

"Ya no vivo en Madrid."

expresses the END of a previously holding state and may therefore be
a TRANSITION.

"Nunca viví en Madrid."

does not imply that a residence state ended; it denies that such a
state held.

Distinguish carefully between:

- negative state
- negated event
- ending of a previous state
- denial of a claim
- negation scoped over reported or embedded content

Do not infer additional facts outside the scope of the negation.

============================================================
6. AMBIGUOUS REFERENCES
============================================================

Resolve a pronoun when grammar, recency, or discourse focus makes
one candidate clearly more likely. Keep all plausible candidates,
set resolved_entity_temp_id to the most likely one, and lower
confidence when the resolution is not certain.

Leave resolved_entity_temp_id = null only when the candidates are
genuinely balanced or the available context is insufficient.

Create one RawReference.

If there are multiple plausible antecedents:

candidate_entity_temp_ids must contain all plausible candidates.

resolved_entity_temp_id = null

Use reference_temp_id when that ambiguous reference participates in
a situation.

Example:

"Laura habló con Marta y ella se fue."

entities:
- laura
- marta

event1:
  semantic_type = talk_with
  participants:
    - agent -> laura
    - recipient -> marta

ref1:
  text = "ella"
  candidate_entity_temp_ids = ["laura", "marta"]
  resolved_entity_temp_id = marta
  confidence = 0.75

event2:
  semantic_type = leave
  participant:
    role = theme
    reference_temp_id = ref1

Create ONE leave event through the reference. Do not duplicate the
event for every candidate.

If no plausible antecedent can be identified at all,
candidate_entity_temp_ids may be empty.

============================================================
7. REPORTED SPEECH
============================================================

Reported speech is an ATTRIBUTION, not a mental-attitude
PROPOSITION.

Verbs of communication such as decir, contar, afirmar,
comunicar, and informar require an attribution whose source is
the speaker and whose target is the reported semantic content.

Use a proposition only when the utterance explicitly attributes
a mental attitude such as believing, thinking, wanting, or
knowing. Saying something does NOT imply believing it.

Therefore, when the utterance says that Laura "dijo" something:

- put the report in attributions
- use relation = reports
- do not put that report in propositions
- do not assign mode = belief to Laura

Example:

"Laura dijo que Marta vendrá mañana."

entities:
- laura
- marta

event1:
  semantic_type = come
  participant:
    theme -> marta
  temporal:
    frame = future
    expression = "mañana"

attribution1:
  source_entity_temp_id = laura
  relation = reports
  target_id = event1

For this example, propositions MUST be empty and attributions
MUST contain attribution1.

Do NOT turn reported content into the user's or the reported
speaker's BELIEF.

============================================================
8. CORRECTIONS AND REVISIONS
============================================================

Use revisions for same-utterance corrections, retractions,
and reformulations.

For a correction:

target_id = old content being corrected
replacement_id = new corrected content

The revision must have its own temp_id.

Example:

"Me voy a Madrid... perdón, a Getafe."

entities:
- user
- madrid
- getafe

event1:
  semantic_type = move
  participants:
    - theme -> user
    - destination -> madrid

event2:
  semantic_type = move
  participants:
    - theme -> user
    - destination -> getafe

revision1:
  revision = correction
  target_id = event1
  replacement_id = event2

Do NOT reverse target_id and replacement_id.

Do NOT use event1 or event2 as the revision temp_id.

============================================================
9. SEMANTIC RELATIONS
============================================================

Only use semantic relations when the utterance explicitly expresses
one.

Allowed relations are:

cause
reason
consequence
contrast
condition
enables
prevents
temporal_before
temporal_after
corrects
presupposes
contradicts

Do NOT invent relation labels.

Do NOT use semantic relations for ordinary participants.

Semantic relations connect distinct semantic contents when the
utterance explicitly states how those contents relate to each other.

Before using semantic_content_links between two semantic nodes,
ask:

"Does one node actually contain, communicate, express, ask about,
deny, or otherwise take the other node as its semantic content?"

If NO, do not use a semantic_content_link.

If the utterance instead expresses a temporal, causal, conditional,
contrastive, consequential, enabling, preventing, corrective,
presuppositional, or contradictory relationship, use the appropriate
semantic_relation.

Temporal ordering is especially important.

Expressions such as:

- before
- after
- antes de
- después de
- antes de que
- después de que

when they explicitly order two represented situations, normally
require:

temporal_before

or:

temporal_after

Example:

"Pablo llegó antes de que empezara la reunión."

Represent both situations:

arrive1:
- semantic_type = arrive
- theme = Pablo

start1:
- semantic_type = start
- theme = the meeting

Then represent their ordering:

semantic_relations:
- relation = temporal_before
- source_id = arrive1
- target_id = start1

Do NOT use:

semantic_content_links:
- source_id = arrive1
- target_id = start1

The START situation is not the semantic content of ARRIVE.
They are two distinct situations related in time.

Likewise:

"Laura se fue después de que Marta llegara."

requires an explicit temporal relationship between the leaving and
arrival situations.

Do not infer a semantic relation merely because two situations occur
in the same utterance. The relationship must be linguistically
expressed or clearly encoded by the construction.

A semantic_content_link and a semantic_relation answer different
questions:

semantic_content_link:
"What semantic content does this node contain or express?"

semantic_relation:
"How are these distinct semantic contents related?"

Never substitute one for the other.

Do NOT reify a relationship between semantic nodes as an additional
situation merely to connect those nodes.

If two situations are explicitly related by one of the allowed
semantic relations, represent the relationship directly as a
semantic_relation.

Incorrect for:

"Pablo llegó antes de que empezara la reunión."

situations:
- arrive1
- start1
- state1:
    semantic_type = before
    participants:
      first -> arrive1
      second -> start1

This is invalid because ARRIVE and START are semantic situations,
not entities participating in a BEFORE state.

Correct:

situations:
- arrive1
- start1

semantic_relations:
- relation = temporal_before
- source_id = arrive1
- target_id = start1

Do not create semantic types such as:

before
after
because
if
contrast

when their only purpose is to represent a relationship between
already represented semantic nodes.

Use the corresponding semantic_relation instead.

A participant may connect a situation only to an entity or reference.
It must never be used as an indirect way to connect two semantic
situations.

============================================================
9.1 SEMANTIC CONTENT LINKS
============================================================

Participants and semantic content are different kinds of
relationships.

A participant connects a SITUATION to an ENTITY or REFERENCE that
takes part in that situation.

Examples:

- agent -> Laura
- recipient -> Marta
- destination -> Madrid

A participant MUST NEVER point to another situation, proposition,
attribution, or other semantic node.

If X is semantic content rather than an entity participating in an
event, do NOT put X in participants.

Use semantic_content_links to represent that one semantic node
contains, expresses, communicates, asks about, denies, or otherwise
takes another semantic node as its semantic content.

A semantic content link:

- uses source_id = the semantic node that contains or expresses
  the content
- uses target_id = the semantic node that represents that content
- both IDs must refer to existing semantic nodes
- is structural composition, not an ordinary participant relation
- is not a causal, temporal, contrastive, or other semantic_relation

Example:

"Laura dijo que Marta venía."

The saying and the coming are two semantic situations:

say1:
- semantic_type = say
- participant:
    agent -> Laura

come1:
- semantic_type = come
- participant:
    theme -> Marta

Their structural relationship is:

semantic_content_links:
- source_id = say1
- target_id = come1

Incorrect:

say1 participant:
- role = content
- entity_temp_id = come1

because come1 is a situation, NOT an entity.

The same distinction applies generally to content-bearing semantic
situations such as saying, asking, denying, claiming, reporting,
communicating, or similar cases when their semantic content is also
represented as a semantic node.

Use the appropriate structures independently when several relations
hold at once.

For example, a semantic node may:

- have entity participants
- contain another semantic node through semantic_content_links
- be targeted by a scope_operator
- participate in a semantic_relation
- be the target of an attribution

These structures represent different aspects of meaning and must not
be substituted for one another.

============================================================
10. COMMUNICATIVE ACTS
============================================================

Communicative acts represent what the speaker is doing with the
utterance, not merely its grammatical sentence form.

Choose acts from the pragmatic meaning of the utterance.

ASSERT:
the speaker presents content as holding or being the case.

ASK:
the speaker seeks information or an answer.

REQUEST:
the speaker asks the listener or assistant to perform an action.

SPECULATE:
the speaker presents possibilities, hypotheses, alternatives, or
uncertain scenarios without asserting one as true.

CORRECT:
the speaker explicitly replaces or corrects previously expressed
content.

CONFIRM:
the speaker explicitly confirms previously introduced content.

DENY:
the speaker explicitly rejects or denies a claim, attribution, or
previously introduced content.

EXPRESS:

EXPRESS must not be used merely because the utterance contains a
BELIEF, OPINION, DESIRE, INTENTION, or other mental attitude.

Mental attitude and communicative act are separate layers.

Examples:

"Creo que Marta está cansada."
- communicative act = ASSERT
- proposition mode = BELIEF

"En mi opinión, este plan es demasiado arriesgado."
- communicative act = ASSERT
- proposition mode = OPINION

Use EXPRESS only when expressing the reaction or attitude itself is
the primary communicative function and ASSERT, ASK, REQUEST,
SPECULATE, CORRECT, CONFIRM, or DENY does not describe it better.

the utterance primarily expresses a subjective reaction or attitude
when no more specific communicative act applies.

Do not classify an utterance only from its grammatical surface form.

A question-shaped utterance can pragmatically be a REQUEST.

Example:

"¿Puedes buscar una farmacia cercana?"

Literal form:
- question about capability

Intended communicative act:
- request

The speaker is asking the assistant to perform the search, not merely
asking whether searching is possible.

Likewise:

"Dime si Marta confirmó la reserva."

The embedded content concerns whether Marta confirmed the reservation,
but the utterance as a whole is a REQUEST for the listener to provide
that information.

Use ASK when the speaker's primary goal is obtaining an answer to the
question itself.

Example:

"¿Dónde vive Laura?"
- ASK

Use SPECULATE when the speaker explicitly frames content as possible,
uncertain, hypothetical, or as competing alternatives rather than
asserting it as true.

Examples:

"Puede que mañana cancelen el concierto."
- SPECULATE

"Quizá fue Ana o quizá fue Elena."
- SPECULATE

The existence of a POSSIBILITY or HYPOTHESIS proposition does not
replace the communicative act. They represent different layers:

- communicative act = what the speaker is doing
- proposition mode = the attitude toward semantic content
- certainty/reality = epistemic or modal status of that content

Use DENY when the speaker's communicative act is explicitly denying
that something was said, happened, held, or was attributable to them.

Example:

"Nunca dije que Laura hubiera mentido."
- DENY

Be careful with scope:
the speaker denies having said the embedded claim.
This does NOT by itself assert that Laura did not lie.

An utterance may contain more than one communicative act when this is
semantically justified, such as asserting content and then correcting
it.

Do not add extra acts merely because they are compatible with the
utterance.

============================================================
11. DO NOT INVENT FACTS
============================================================

Preserve semantic framing.

"Creo que Marta está enfadada."
must remain a BELIEF about Marta being angry.

"No quiero dejar el trabajo."
must remain a negative DESIRE.

"Laura dice que Marta se fue."
must preserve Laura as the source.

"Quizá mañana llueva."
must preserve uncertainty.

Ambiguity must remain ambiguity.

============================================================
12. OUTPUT
============================================================

Return only a valid RawInterpretation.

Do not answer the user.
Do not explain your reasoning.

Prefer the smallest graph that preserves the complete meaning.

Most importantly:

DO NOT OMIT CLEAR SEMANTIC CONTENT.

If the utterance contains a clear event, state, mental attitude,
reference, attribution, correction, or semantically relevant
participant, represent it.

Before returning the RawInterpretation, verify semantic coverage:

- Have all clearly expressed situations been represented?
- Have the entities participating in those situations been connected?
- Has any explicit object, recipient, target, location, source,
  destination, theme, patient, or experiencer disappeared?
- Does each participant point to a declared entity or reference?
- Does the structured graph preserve the same essential meaning
  described by intended_meaning?

If intended_meaning contains an essential semantic relation that is
missing from the structured graph, the graph is incomplete.

Prefer a compact graph, but never achieve compactness by deleting
meaning.
"""


class Understanding:
    """
    Converts one user utterance into Celeste's strict semantic
    Interpretation.

    The LLM produces the forgiving RawInterpretation.
    Deterministic Python normalization then creates and validates
    the internal semantic graph.
    """

    def __init__(
        self,
        provider: LLMProvider,
    ) -> None:
        self._provider = provider

    async def interpret(
        self,
        text: str,
    ) -> Interpretation:
        if not text.strip():
            raise ValueError(
                "Cannot interpret an empty utterance."
            )

        raw = await self.interpret_raw(text)

        return normalize_interpretation(raw)

    async def interpret_raw(
        self,
        text: str,
    ) -> RawInterpretation:
        if not text.strip():
            raise ValueError(
                "Cannot interpret an empty utterance."
            )

        return await self._provider.generate_structured(
            system_prompt=UNDERSTANDING_SYSTEM_PROMPT,
            user_prompt=text,
            response_model=RawInterpretation,
        )