import { useMemo } from "react";

import type { CrystalPiece as CrystalPieceData } from "./geometry/types";
import { CrystalEdges } from "./materials/CrystalEdges";
import { CrystalSurface } from "./materials/CrystalSurface";

interface CrystalPieceProps {
  piece: CrystalPieceData;
  accentColor: string;
}

function seededVariation(id: number, offset: number): number {
  const value =
    Math.sin((id + offset) * 12.9898) * 43758.5453;

  return value - Math.floor(value);
}

export function CrystalPiece({
  piece,
  accentColor,
}: CrystalPieceProps) {
  const brightness = useMemo(
    () => seededVariation(piece.id, 37),
    [piece.id],
  );

  return (
    <group position={piece.homePosition}>
      <mesh geometry={piece.geometry}>
        <CrystalSurface
          accentColor={accentColor}
          brightness={brightness}
        />
      </mesh>

      <CrystalEdges
        geometry={piece.geometry}
        accentColor={accentColor}
        brightness={brightness}
      />
    </group>
  );
}