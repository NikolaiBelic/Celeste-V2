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
  const edges = useMemo(() => new EdgesGeometry(geometry), [geometry]);

  const glowColor = useMemo(
    () => new Color(accentColor).multiplyScalar(3.5 + strength * 9),
    [accentColor, strength],
  );

  if (strength <= 0.1) {
    return null;
  }

  return (
    <lineSegments geometry={edges} scale={1.006}>
      <lineBasicMaterial
        color={glowColor}
        transparent
        opacity={0.08 + strength * 0.34}
        blending={AdditiveBlending}
        depthWrite={false}
        toneMapped={false}
      />
    </lineSegments>
  );
}
