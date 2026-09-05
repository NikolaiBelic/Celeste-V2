import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type { Group } from "three";

import { CrystalPiece } from "./CrystalPiece";
import { createCrystal } from "./geometry/createCrystal";

interface CrystalBodyProps {
  accentColor: string;
}

export function CrystalBody({
  accentColor,
}: CrystalBodyProps) {
  const groupRef = useRef<Group>(null);

  const pieces = useMemo(() => createCrystal(), []);

  useFrame((state, delta) => {
    const group = groupRef.current;

    if (!group) {
      return;
    }

    group.rotation.y += delta * 0.08;
    group.rotation.x += delta * 0.018;

    const time = state.clock.elapsedTime;

    const breathing =
      1 + Math.sin(time * 0.75) * 0.018;

    group.scale.setScalar(breathing);
  });

  return (
    <group ref={groupRef}>
      {pieces.map((piece) => (
        <CrystalPiece
          key={piece.id}
          piece={piece}
          accentColor={accentColor}
        />
      ))}
    </group>
  );
}