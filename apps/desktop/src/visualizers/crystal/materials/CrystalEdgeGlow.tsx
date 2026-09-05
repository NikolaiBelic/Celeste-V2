import { useMemo } from "react";
import {
  AdditiveBlending,
  Color,
  EdgesGeometry,
} from "three";

import type { BufferGeometry } from "three";

interface CrystalEdgeGlowProps {
  geometry: BufferGeometry;
  accentColor: string;
  strength: number;
}

export function CrystalEdgeGlow({
  geometry,
  accentColor,
  strength,
}: CrystalEdgeGlowProps) {
  const edges = useMemo(
    () => new EdgesGeometry(geometry),
    [geometry],
  );

  const glowColor = useMemo(() => {
    return new Color(accentColor).multiplyScalar(
      1.8 + strength * 3.8,
    );
  }, [accentColor, strength]);

  if (strength <= 0.15) {
    return null;
  }

  return (
    <lineSegments
      geometry={edges}
      scale={1.004}
    >
      <lineBasicMaterial
        color={glowColor}
        transparent
        opacity={0.06 + strength * 0.24}
        blending={AdditiveBlending}
        depthWrite={false}
        toneMapped={false}
      />
    </lineSegments>
  );
}