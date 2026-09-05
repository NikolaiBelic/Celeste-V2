import { useMemo } from "react";
import { Color, EdgesGeometry } from "three";
import type { BufferGeometry, ColorRepresentation } from "three";

interface CrystalEdgesProps {
  geometry: BufferGeometry;
  accentColor: ColorRepresentation;
  edgeEnergy: number;
  hotSpot: number;
}

export function CrystalEdges({
  geometry,
  accentColor,
  edgeEnergy,
  hotSpot,
}: CrystalEdgesProps) {
  const edges = useMemo(() => new EdgesGeometry(geometry), [geometry]);

  const hdrColor = useMemo(() => {
    const color = new Color(accentColor);
    return color.multiplyScalar(
      0.55 + edgeEnergy * 2.8 + hotSpot * 7.5,
    );
  }, [accentColor, edgeEnergy, hotSpot]);

  const opacity = Math.min(
    0.025 + edgeEnergy * 0.3 + hotSpot * 0.5,
    0.95,
  );

  return (
    <lineSegments geometry={edges}>
      <lineBasicMaterial
        color={hdrColor}
        transparent
        opacity={opacity}
        depthWrite={false}
        toneMapped={false}
      />
    </lineSegments>
  );
}
