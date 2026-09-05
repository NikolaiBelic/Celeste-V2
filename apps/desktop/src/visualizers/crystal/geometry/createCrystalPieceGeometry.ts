import {
  BufferGeometry,
  Float32BufferAttribute,
  Vector3,
} from "three";

interface CreateCrystalPieceGeometryOptions {
  a: Vector3;
  b: Vector3;
  c: Vector3;
  normal: Vector3;
  thickness: number;
}

/*
 * Construye un fragmento triangular con volumen real.
 *
 * La cara exterior conserva exactamente los vértices originales.
 * La cara interior se desplaza hacia dentro siguiendo la normal.
 *
 *      A
 *     / \
 *    B---C       exterior
 *    |\  |
 *    | \ |
 *    B'-C'       interior
 *
 * Esto permite que una pieza separada tenga laterales visibles
 * en lugar de desaparecer cuando la vemos de canto.
 */
export function createCrystalPieceGeometry({
  a,
  b,
  c,
  normal,
  thickness,
}: CreateCrystalPieceGeometryOptions): BufferGeometry {
  const inward = normal
    .clone()
    .normalize()
    .multiplyScalar(-thickness);

  const innerA = a.clone().add(inward);
  const innerB = b.clone().add(inward);
  const innerC = c.clone().add(inward);

  const vertices: number[] = [];

  function triangle(
    v1: Vector3,
    v2: Vector3,
    v3: Vector3,
  ) {
    vertices.push(
      v1.x, v1.y, v1.z,
      v2.x, v2.y, v2.z,
      v3.x, v3.y, v3.z,
    );
  }

  /*
   * Cara exterior.
   */
  triangle(a, b, c);

  /*
   * Cara interior.
   * Orden invertido para que la normal mire hacia dentro.
   */
  triangle(innerC, innerB, innerA);

  /*
   * Lateral AB.
   */
  triangle(a, innerA, innerB);
  triangle(a, innerB, b);

  /*
   * Lateral BC.
   */
  triangle(b, innerB, innerC);
  triangle(b, innerC, c);

  /*
   * Lateral CA.
   */
  triangle(c, innerC, innerA);
  triangle(c, innerA, a);

  const geometry = new BufferGeometry();

  geometry.setAttribute(
    "position",
    new Float32BufferAttribute(vertices, 3),
  );

/*
* Cada triángulo tiene 3 vértices.
*
* 0 - 2   → exterior
* 3 - 5   → interior
* 6 - 23  → laterales
*/
geometry.clearGroups();

geometry.addGroup(0, 3, 0);
geometry.addGroup(3, 3, 1);
geometry.addGroup(6, 18, 2);

  geometry.computeVertexNormals();
  geometry.computeBoundingSphere();

  return geometry;
}