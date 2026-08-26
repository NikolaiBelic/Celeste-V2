from __future__ import annotations

from celeste.cognition.models import EntityReference
from celeste.memory.entities import ResolutionResult, StoredEntity
from celeste.memory.entity_repository import EntityRepository


class EntityResolver:
    def __init__(
        self,
        repository: EntityRepository,
        *,
        user_entity_id: str,
    ) -> None:
        self._repository = repository
        self._user_entity_id = user_entity_id

    async def resolve(
        self,
        reference: EntityReference,
    ) -> ResolutionResult:
        if reference.known_entity_id:
            entity = await self._repository.get_by_id(
                str(reference.known_entity_id)
            )

            return ResolutionResult(
                entity=entity,
                confidence=1.0 if entity else 0.0,
                strategy="known_id",
            )

        if reference.contextual_role == "user":
            entity = await self._repository.get_by_id(
                self._user_entity_id
            )

            return ResolutionResult(
                entity=entity,
                confidence=1.0 if entity else 0.0,
                strategy="user",
            )

        name_candidates: list[StoredEntity] = []

        lookup_name = reference.name

        if (
            lookup_name is None
            and reference.reference_kind.value == "explicit_entity"
        ):
            lookup_name = reference.surface_text

        if lookup_name:
            name_candidates = await self._repository.find_by_name(
                lookup_name
            )

            if not name_candidates:
                name_candidates = await self._repository.find_by_alias(
                    lookup_name
                )

        if reference.contextual_role:
            role_candidates = await self._repository.find_relation_objects(
                subject_id=self._user_entity_id,
                predicate=reference.contextual_role,
            )

            if name_candidates:
                name_ids = {entity.id for entity in name_candidates}

                role_candidates = [
                    entity
                    for entity in role_candidates
                    if entity.id in name_ids
                ]

            if len(role_candidates) == 1:
                candidate = role_candidates[0]

                if self._matches_qualifiers(
                    candidate,
                    reference.qualifiers,
                ):
                    return ResolutionResult(
                        entity=candidate,
                        confidence=0.99,
                        strategy="name_and_contextual_role",
                    )

            if len(role_candidates) > 1:
                filtered = self._filter_by_qualifiers(
                    role_candidates,
                    reference.qualifiers,
                )

                if len(filtered) == 1:
                    return ResolutionResult(
                        entity=filtered[0],
                        confidence=0.98,
                        strategy="contextual_role_and_qualifiers",
                    )

                return ResolutionResult(
                    confidence=0.0,
                    strategy="contextual_role",
                    ambiguous=True,
                )

        if name_candidates:
            filtered = self._filter_by_qualifiers(
                name_candidates,
                reference.qualifiers,
            )

            if len(filtered) == 1:
                return ResolutionResult(
                    entity=filtered[0],
                    confidence=0.98,
                    strategy=(
                        "name_and_qualifiers"
                        if reference.qualifiers
                        else "canonical_name"
                    ),
                )

            if len(filtered) > 1:
                return ResolutionResult(
                    confidence=0.0,
                    strategy="canonical_name",
                    ambiguous=True,
                )

            if reference.qualifiers:
                return ResolutionResult(
                    confidence=0.0,
                    strategy="qualifier_mismatch",
                )

        return ResolutionResult(
            confidence=0.0,
            strategy="unresolved",
        )

    @staticmethod
    def _matches_qualifiers(
        entity: StoredEntity,
        qualifiers: dict[str, object],
    ) -> bool:
        for key, expected in qualifiers.items():
            actual = entity.attributes.get(key)

            if isinstance(actual, str) and isinstance(expected, str):
                if actual.casefold() != expected.casefold():
                    return False
            elif actual != expected:
                return False

        return True

    @classmethod
    def _filter_by_qualifiers(
        cls,
        entities: list[StoredEntity],
        qualifiers: dict[str, object],
    ) -> list[StoredEntity]:
        if not qualifiers:
            return entities

        return [
            entity
            for entity in entities
            if cls._matches_qualifiers(entity, qualifiers)
        ]