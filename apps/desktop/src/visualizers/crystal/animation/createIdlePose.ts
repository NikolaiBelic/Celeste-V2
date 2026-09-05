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

export function createIdlePose(piece: CrystalPiece): CrystalIdlePose {
  const poseRoll = seededRandom(piece.id + 401);

  // Dense central shell: most plates remain exactly reconstructable.
  if (poseRoll < 0.72) {
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

  // A few cracked plates hover just outside the shell.
  if (poseRoll < 0.9) {
    const distance = 0.035 + distanceRandom * 0.11;
    return {
      position: piece.homePosition.clone().add(piece.normal.clone().multiplyScalar(distance)),
      rotation: piece.homeRotation.clone().add(new Vector3(rotationX * 0.16, rotationY * 0.16, rotationZ * 0.16)),
      kind: "loose",
    };
  }

  // Sparse hero shards, clearly separated like the reference.
  const detachedDistance = 0.48 + distanceRandom * 0.72;
  return {
    position: piece.homePosition.clone().add(piece.normal.clone().multiplyScalar(detachedDistance)),
    rotation: piece.homeRotation.clone().add(new Vector3(rotationX * 0.9, rotationY * 0.9, rotationZ * 0.9)),
    kind: "detached",
  };
}
