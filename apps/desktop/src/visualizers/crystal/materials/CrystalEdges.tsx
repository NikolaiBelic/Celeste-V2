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
  brightness: number;
}

export function CrystalEdges({
  geometry,
  accentColor,
  brightness,
}: CrystalEdgesProps) {
  const edges = useMemo(
    () => new EdgesGeometry(geometry),
    [geometry],
  );

  const hdrColor = useMemo(() => {
    const color = new Color(accentColor);

    /*
     * Three.js permite componentes RGB > 1.
     * Es precisamente lo que necesitamos para que determinadas
     * aristas entren en el rango HDR y produzcan bloom.
     */
    const energy = 1.2 + brightness * 2.8;

    return color.multiplyScalar(energy);
  }, [accentColor, brightness]);

  return (
    <lineSegments geometry={edges}>
      <lineBasicMaterial
        color={hdrColor}
        transparent
        opacity={0.18 + brightness * 0.55}
        toneMapped={false}
      />
    </lineSegments>
  );
}