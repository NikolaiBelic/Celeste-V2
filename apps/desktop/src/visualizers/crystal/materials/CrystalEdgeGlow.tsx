import { useMemo } from "react";
import { AdditiveBlending, Color, EdgesGeometry } from "three";
import type { BufferGeometry } from "three";

interface CrystalEdgeGlowProps {
  geometry: BufferGeometry;
  accentColor: string;
  strength: number;
}

export function CrystalEdgeGlow({ geometry, accentColor, strength }: CrystalEdgeGlowProps) {
  const edges = useMemo(() => new EdgesGeometry(geometry), [geometry]);
  const glowColor = useMemo(
    () => new Color(accentColor).multiplyScalar(6 + strength * 12),
    [accentColor, strength],
  );

  if (strength <= 0.55) return null;

  return (
    <lineSegments geometry={edges} scale={1.008}>
      <lineBasicMaterial
        color={glowColor}
        transparent
        opacity={0.22 + strength * 0.38}
        blending={AdditiveBlending}
        depthWrite={false}
        toneMapped={false}
      />
    </lineSegments>
  );
}
