import {
  BufferGeometry,
  Float32BufferAttribute,
  IcosahedronGeometry,
  Vector3,
} from "three";

import type { CrystalPiece } from "./types";

function seededRandom(seed: number): number {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

export function createCrystal(): CrystalPiece[] {
  const sourceGeometry = new IcosahedronGeometry(1.45, 2).toNonIndexed();
  const positions = sourceGeometry.getAttribute("position");

  const pieces: CrystalPiece[] = [];

  for (let i = 0; i < positions.count; i += 3) {
    const a = new Vector3(
      positions.getX(i),
      positions.getY(i),
      positions.getZ(i),
    );

    const b = new Vector3(
      positions.getX(i + 1),
      positions.getY(i + 1),
      positions.getZ(i + 1),
    );

    const c = new Vector3(
      positions.getX(i + 2),
      positions.getY(i + 2),
      positions.getZ(i + 2),
    );

    const center = new Vector3()
      .add(a)
      .add(b)
      .add(c)
      .divideScalar(3);

    /*
     * Convertimos los vértices a coordenadas locales.
     *
     * De esta forma cada pieza tiene su propio origen en el centro
     * del triángulo y posteriormente podemos moverla/rotarla
     * independientemente.
     */
    a.sub(center);
    b.sub(center);
    c.sub(center);

    const geometry = new BufferGeometry();

    geometry.setAttribute(
      "position",
      new Float32BufferAttribute(
        [
          a.x, a.y, a.z,
          b.x, b.y, b.z,
          c.x, c.y, c.z,
        ],
        3,
      ),
    );

    geometry.computeVertexNormals();

    const id = i / 3;

    const explodeDirection = center.clone().normalize();

    const explodeDistance =
      0.5 + seededRandom(id + 10) * 1.15;

    const phase =
      seededRandom(id + 20) * Math.PI * 2;

    pieces.push({
      id,
      geometry,

      homePosition: center,

      homeRotation: new Vector3(0, 0, 0),

      explodeDirection,
      explodeDistance,

      phase,
    });
  }

  sourceGeometry.dispose();

  return pieces;
}