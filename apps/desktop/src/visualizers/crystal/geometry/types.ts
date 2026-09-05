import type { BufferGeometry, Vector3 } from "three";

export interface CrystalPiece {
  id: number;

  geometry: BufferGeometry;

  homePosition: Vector3;
  homeRotation: Vector3;

  normal: Vector3;

  explodeDirection: Vector3;
  explodeDistance: number;

  phase: number;
}