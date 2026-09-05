import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import {
  AdditiveBlending,
  BackSide,
} from "three";

import type { Group } from "three";

interface CrystalAuraProps {
  accentColor: string;
}

export function CrystalAura({
  accentColor,
}: CrystalAuraProps) {
  const groupRef = useRef<Group>(null);

  useFrame((state) => {
    const group = groupRef.current;

    if (!group) {
      return;
    }

    const time = state.clock.elapsedTime;

    const pulse =
      1 + Math.sin(time * 0.55) * 0.018;

    group.scale.setScalar(pulse);
    group.rotation.y += 0.00035;
  });

  return (
    <group ref={groupRef}>
      <mesh>
        <icosahedronGeometry args={[1.53, 4]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.018}
          blending={AdditiveBlending}
          depthWrite={false}
          side={BackSide}
          toneMapped={false}
        />
      </mesh>

      <mesh>
        <icosahedronGeometry args={[1.66, 4]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.009}
          blending={AdditiveBlending}
          depthWrite={false}
          side={BackSide}
          toneMapped={false}
        />
      </mesh>

      <mesh>
        <icosahedronGeometry args={[1.82, 4]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.0035}
          blending={AdditiveBlending}
          depthWrite={false}
          side={BackSide}
          toneMapped={false}
        />
      </mesh>
    </group>
  );
}