# Celeste V2 — Interpretation

## Purpose

Interpretation converts a user's natural-language utterance into a structured
semantic representation that the rest of Celeste can reason about.

Interpretation does not decide what Celeste should answer, what she should
remember, or what actions she should perform.

Current pipeline:

    User text
        |
        v
    Understanding
        |
        v
    LLMProvider (currently Ollama / Qwen)
        |
        v
    RawInterpretation
        |
        v
    Interpretation Normalizer
        |
        v
    Interpretation

The Raw and strict representations are deliberately separate.


## Production components

### understanding.py

Entry point for language understanding.

Responsibilities:

- Send the utterance to the configured LLM provider.
- Define the semantic instructions given to the LLM.
- Request a RawInterpretation.
- Pass valid raw output to the normalizer.

It must not:

- Write memory.
- Resolve long-term knowledge.
- Decide Celeste's response.
- Perform deliberation.
- Mutate the strict semantic graph manually.

Most of this file is currently the system prompt, not orchestration code.


### raw_interpretation.py

LLM-facing semantic contract.

Responsibilities:

- Define the structured output expected from the LLM.
- Represent entities, references, situations, propositions and semantic links.
- Detect structurally invalid LLM output.
- Apply only safe and deterministic structural repairs where explicitly allowed.

RawInterpretation is allowed to be more defensive than the internal model
because LLM output is an untrusted boundary.

It must not become Celeste's long-term knowledge representation.


### interpretation_normalizer.py

Deterministic boundary between LLM output and Celeste's internal semantics.

Responsibilities:

- Convert RawInterpretation into Interpretation.
- Convert temporary LLM identifiers into strict semantic identifiers.
- Normalize participants and references.
- Build nested semantic structures.
- Reject raw structures that cannot safely become strict semantics.

The normalizer must not invent missing meaning merely to make an
interpretation valid.


### interpretation.py

Strict internal semantic representation.

Responsibilities:

- Represent the meaning Celeste believes was expressed by the utterance.
- Enforce graph integrity.
- Provide stable structural contracts to later cognitive modules.

It includes concepts such as:

- entities and references
- events, states and transitions
- participants
- propositions
- attribution
- semantic relations
- semantic content links
- scope operators
- revisions
- alternatives
- comparisons
- quantification
- uncertainty and temporal information

This layer is independent from any particular LLM provider.


## Laboratory / evaluation

The following components measure Interpretation but are not part of Celeste's
runtime interpretation pipeline:

- tests/scenarios/interpretation_cases.json
- scripts/evaluate_interpretation.py
- celeste/cognition/interpretation_evaluation.py
- tests/unit/test_interpretation_evaluation.py

Benchmark failures must not automatically cause architecture changes.

A benchmark expectation should only be changed when the expectation itself is
semantically wrong.

A production change should only be made when it improves a general
interpretation capability, not merely because it makes one benchmark case pass.


## Current design principles

1. Meaning is represented once whenever possible.
2. Participants connect situations to entities or references.
3. Semantic relations connect semantic nodes through causal, temporal,
   logical or discourse relations.
4. Semantic content links represent semantic containment or communicated
   content.
5. Attribution represents who asserts or reports semantic content.
6. Scope operators represent semantic scope such as negation.
7. LLM output never directly becomes long-term memory.
8. Structural repair must not invent semantic facts.
9. Interpretation describes what the user expressed; later cognitive modules
   decide what Celeste believes, remembers, asks, says or does.


## Known open problems

### Semantic concept identity

`semantic_type` is currently open text.

Semantically related outputs may therefore use different labels, for example:

- angry / be_angry_with
- risky / be_risky
- quit_job / leave_job

This is not currently solved with aliases or benchmark-specific normalization.

A stable conceptual/ontology layer may eventually belong in the World /
Knowledge Model rather than being forced prematurely into Interpretation.


### LLM semantic reliability

The strict representation can express more distinctions than the current local
model consistently produces.

This is expected.

The architecture should not be weakened solely to accommodate the current
model.


### Benchmark

The benchmark is diagnostic, not the definition of correctness.

Its purpose is to expose systematic weaknesses in Interpretation and the LLM
contract while keeping architectural decisions independent from individual
test cases.


## Boundary with future cognition

Interpretation ends after producing the semantic representation of the current
utterance.

Later modules will handle:

- conversational context
- temporal resolution
- world / knowledge modeling
- provenance and evidence
- recall
- hypotheses and uncertainty
- user and self models
- deliberation
- goals and intentions
- curiosity
- memory decisions
- planning
- tools and actions
- response planning
- personality and expression
- reflection and consolidation

Those responsibilities should not be pulled into Interpretation merely because
they can improve an isolated language-understanding example.
