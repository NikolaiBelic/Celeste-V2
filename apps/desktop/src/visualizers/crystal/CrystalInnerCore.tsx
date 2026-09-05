import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type { Mesh } from "three";

interface CrystalInnerCoreProps {
  accentColor: string;
}

export function CrystalInnerCore({
  accentColor,
}: CrystalInnerCoreProps) {
  const coreRef = useRef<Mesh>(null);

  useFrame((state) => {
    const core = coreRef.current;

    if (!core) {
      return;
    }

    const time = state.clock.elapsedTime;

    const pulse =
      0.92 + Math.sin(time * 0.9) * 0.045;

    core.scale.setScalar(pulse);
  });

  return (
    <>
      <mesh ref={coreRef} scale={0.72}>
        <icosahedronGeometry args={[0.92, 1]} />

        <meshBasicMaterial
            color={accentColor}
            transparent
            opacity={0.16}
            depthWrite={false}
        />
        </mesh>

      <pointLight
        color={accentColor}
        intensity={16}
        distance={4.5}
        decay={2}
      />
    </>
  );
}