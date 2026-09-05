import { Vector3 } from "three";

import type { CrystalPiece } from "../geometry/types";

export interface CrystalIdlePose {
  position: Vector3;
  rotation: Vector3;
  kind: "home" | "loose" | "detached";
}

function seededRandom(seed: number): number {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

export function createIdlePose(
  piece: CrystalPiece,
): CrystalIdlePose {
  const poseRoll = seededRandom(piece.id + 401);

  /*
   * 80 %:
   * cristal completamente reconstruido.
   */
  if (poseRoll < 0.8) {
    return {
      position: piece.homePosition.clone(),
      rotation: piece.homeRotation.clone(),
      kind: "home",
    };
  }

  const distanceRandom = seededRandom(piece.id + 503);
  const rotationX = seededRandom(piece.id + 607) - 0.5;
  const rotationY = seededRandom(piece.id + 701) - 0.5;
  const rotationZ = seededRandom(piece.id + 809) - 0.5;

  /*
   * 14 %:
   * pequeñas imperfecciones de la superficie.
   */
  if (poseRoll < 0.94) {
    const distance =
      0.025 + distanceRandom * 0.075;

    return {
      position: piece.homePosition
        .clone()
        .add(
          piece.normal
            .clone()
            .multiplyScalar(distance),
        ),

      rotation: piece.homeRotation
        .clone()
        .add(
          new Vector3(
            rotationX * 0.1,
            rotationY * 0.1,
            rotationZ * 0.1,
          ),
        ),

      kind: "loose",
    };
  }

  /*
   * 6 %:
   * fragmentos exteriores visibles.
   *
   * Siguen siendo piezas REALES del cristal.
   */
  const detachedDistance =
    0.32 + distanceRandom * 0.48;

  return {
    position: piece.homePosition
      .clone()
      .add(
        piece.normal
          .clone()
          .multiplyScalar(detachedDistance),
      ),

    rotation: piece.homeRotation
      .clone()
      .add(
        new Vector3(
          rotationX * 0.65,
          rotationY * 0.65,
          rotationZ * 0.65,
        ),
      ),

    kind: "detached",
  };
}