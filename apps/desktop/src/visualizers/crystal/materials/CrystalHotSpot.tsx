import { useMemo } from "react";
import {
  AdditiveBlending,
  Color,
  Vector3,
} from "three";

import type { BufferGeometry } from "three";

interface CrystalHotSpotProps {
  geometry: BufferGeometry;
  accentColor: string;
  strength: number;
  normal: Vector3;
}

export function CrystalHotSpot({
  geometry,
  accentColor,
  strength,
  normal,
}: CrystalHotSpotProps) {
  const hotColor = useMemo(() => {
    const color = new Color(accentColor);

    return color.multiplyScalar(
      2.2 + strength * 3.2,
    );
  }, [accentColor, strength]);

  const outerOffset = useMemo(
    () => normal.clone().normalize().multiplyScalar(0.008),
    [normal],
  );

  const innerOffset = useMemo(
    () => normal.clone().normalize().multiplyScalar(0.012),
    [normal],
  );

  if (strength <= 0) {
    return null;
  }

  return (
    <>
      <mesh
        geometry={geometry}
        position={outerOffset}
        scale={0.72}
      >
        <meshBasicMaterial
          color={hotColor}
          transparent
          opacity={0.12 + strength * 0.24}
          blending={AdditiveBlending}
          depthWrite={false}
          toneMapped={false}
        />
      </mesh>

      <mesh
        geometry={geometry}
        position={innerOffset}
        scale={0.38}
      >
        <meshBasicMaterial
          color={hotColor}
          transparent
          opacity={0.22 + strength * 0.34}
          blending={AdditiveBlending}
          depthWrite={false}
          toneMapped={false}
        />
      </mesh>
    </>
  );
}