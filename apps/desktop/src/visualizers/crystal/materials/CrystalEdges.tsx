import { useMemo } from "react";
import { Color, EdgesGeometry } from "three";
import type { BufferGeometry, ColorRepresentation } from "three";

interface CrystalEdgesProps {
  geometry: BufferGeometry;
  accentColor: ColorRepresentation;
  edgeEnergy: number;
  hotSpot: number;
}

export function CrystalEdges({ geometry, accentColor, edgeEnergy, hotSpot }: CrystalEdgesProps) {
  const edges = useMemo(() => new EdgesGeometry(geometry), [geometry]);
  const active = Math.max(edgeEnergy, hotSpot);

  const hdrColor = useMemo(() => {
    return new Color(accentColor).multiplyScalar(1.8 + edgeEnergy * 4.8 + hotSpot * 8.5);
  }, [accentColor, edgeEnergy, hotSpot]);

  if (active <= 0.035) return null;

  return (
    <lineSegments geometry={edges}>
      <lineBasicMaterial
        color={hdrColor}
        transparent
        opacity={Math.min(0.08 + edgeEnergy * 0.5 + hotSpot * 0.42, 0.92)}
        depthWrite={false}
        toneMapped={false}
      />
    </lineSegments>
  );
}
