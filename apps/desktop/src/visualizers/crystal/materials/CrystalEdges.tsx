import { useMemo } from "react";
import {
  Color,
  EdgesGeometry,
} from "three";

import type {
  BufferGeometry,
  ColorRepresentation,
} from "three";

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
  const edges = useMemo(
    () => new EdgesGeometry(geometry),
    [geometry],
  );

  const hdrColor = useMemo(() => {
    const color = new Color(accentColor);

    const energy =
        0.18 +
        edgeEnergy * 1.15 +
        hotSpot * 3.2;

    return color.multiplyScalar(energy);
  }, [accentColor, edgeEnergy, hotSpot]);

    const opacity =
    0.015 +
    edgeEnergy * 0.16 +
    hotSpot * 0.34;

  return (
    <lineSegments geometry={edges}>
      <lineBasicMaterial
        color={hdrColor}
        transparent
        opacity={Math.min(opacity, 0.9)}
        toneMapped={false}
      />
    </lineSegments>
  );
}