import { useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type { Group } from "three";

import { createCrystal } from "./geometry/createCrystal";
import { CrystalPiece } from "./CrystalPiece";

interface CrystalBodyProps {
  accentColor: string;
}

export function CrystalBody({
  accentColor,
}: CrystalBodyProps) {
  const groupRef = useRef<Group>(null);

  const pieces = useMemo(
    () => createCrystal(),
    [],
  );

  useEffect(() => {
    return () => {
      pieces.forEach((piece) => {
        piece.geometry.dispose();
      });
    };
  }, [pieces]);

  useFrame((state) => {
    if (!groupRef.current) {
      return;
    }

    const time = state.clock.elapsedTime;

    /*
     * Movimiento lento y pesado.
     * Celeste debe sentirse suspendida,
     * no como una esfera decorativa girando.
     */
    groupRef.current.rotation.y =
      time * 0.055;

    groupRef.current.rotation.x =
      Math.sin(time * 0.13) * 0.035;

    groupRef.current.rotation.z =
      Math.sin(time * 0.09) * 0.018;
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