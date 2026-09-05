import { useMemo } from "react";

import type { CrystalPiece as CrystalPieceData } from "./geometry/types";
import { createPieceAppearance } from "./materials/createPieceAppearance";
import { CrystalEdges } from "./materials/CrystalEdges";
import { CrystalSurface } from "./materials/CrystalSurface";
import { CrystalEdgeGlow } from "./materials/CrystalEdgeGlow";
import { CrystalInterior } from "./materials/CrystalInterior";
import { CrystalSides } from "./materials/CrystalSides";
import { createIdlePose } from "./animation/createIdlePose";

interface CrystalPieceProps {
  piece: CrystalPieceData;
  accentColor: string;
}

export function CrystalPiece({
  piece,
  accentColor,
}: CrystalPieceProps) {
  const appearance = useMemo(
    () => createPieceAppearance(piece.id),
    [piece.id],
  );

  const idlePose = useMemo(
    () => createIdlePose(piece),
    [piece],
  );

  return (
    <group
      position={idlePose.position}
      rotation={[
        idlePose.rotation.x,
        idlePose.rotation.y,
        idlePose.rotation.z,
      ]}
    >
      <mesh geometry={piece.geometry}>
        <CrystalSurface
          accentColor={accentColor}
          surfaceEnergy={appearance.surfaceEnergy}
          hotSpot={appearance.hotSpot}
        />

        <CrystalInterior
          accentColor={accentColor}
          energy={appearance.surfaceEnergy}
          hotSpot={appearance.hotSpot}
        />

        <CrystalSides
          accentColor={accentColor}
          energy={appearance.edgeEnergy}
        />
      </mesh>

      <CrystalEdges
        geometry={piece.geometry}
        accentColor={accentColor}
        edgeEnergy={appearance.edgeEnergy}
        hotSpot={appearance.hotSpot}
      />

      <CrystalEdgeGlow
        geometry={piece.geometry}
        accentColor={accentColor}
        strength={appearance.hotSpot}
      />
    </group>
  );
}