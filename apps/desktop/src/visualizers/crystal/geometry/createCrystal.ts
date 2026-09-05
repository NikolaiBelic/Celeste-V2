import {
  IcosahedronGeometry,
  Vector3,
} from "three";
import { createCrystalPieceGeometry } from "./createCrystalPieceGeometry";
import type { CrystalPiece } from "./types";

function seededRandom(seed: number): number {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

export function createCrystal(): CrystalPiece[] {
  /*
   * Detail 1 is intentional: the reference is built from broad,
   * irregular-looking plates, not a dense geodesic wireframe.
   */
  const sourceGeometry = new IcosahedronGeometry(1.45, 1).toNonIndexed();
  const positions = sourceGeometry.getAttribute("position");
  const pieces: CrystalPiece[] = [];

  for (let i = 0; i < positions.count; i += 3) {
    const a = new Vector3(positions.getX(i), positions.getY(i), positions.getZ(i));
    const b = new Vector3(positions.getX(i + 1), positions.getY(i + 1), positions.getZ(i + 1));
    const c = new Vector3(positions.getX(i + 2), positions.getY(i + 2), positions.getZ(i + 2));

    const center = new Vector3().add(a).add(b).add(c).divideScalar(3);

    a.sub(center);
    b.sub(center);
    c.sub(center);

    const edgeAB = new Vector3().subVectors(b, a);
    const edgeAC = new Vector3().subVectors(c, a);
    const normal = new Vector3().crossVectors(edgeAB, edgeAC).normalize();

    if (normal.dot(center) < 0) normal.negate();

    const id = i / 3;
    const thickness = 0.045 + seededRandom(id + 900) * 0.055;

    const geometry = createCrystalPieceGeometry({ a, b, c, normal, thickness });
    const explodeDirection = center.clone().normalize();
    const explodeDistance = 0.5 + seededRandom(id + 10) * 1.15;
    const phase = seededRandom(id + 20) * Math.PI * 2;

    pieces.push({
      id,
      geometry,
      homePosition: center,
      homeRotation: new Vector3(0, 0, 0),
      normal,
      explodeDirection,
      explodeDistance,
      phase,
    });
  }

  sourceGeometry.dispose();
  return pieces;
}
