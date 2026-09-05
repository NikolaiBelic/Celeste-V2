import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { AdditiveBlending, Color } from "three";
import type { Mesh } from "three";

interface CrystalInnerCoreProps {
  accentColor: string;
}

export function CrystalInnerCore({ accentColor }: CrystalInnerCoreProps) {
  const coreRef = useRef<Mesh>(null);
  const hdrColor = new Color(accentColor).multiplyScalar(4.5);

  useFrame((state) => {
    const core = coreRef.current;
    if (!core) return;

    const time = state.clock.elapsedTime;
    core.scale.setScalar(0.9 + Math.sin(time * 0.82) * 0.035);
    core.rotation.y = -time * 0.09;
    core.rotation.x = Math.sin(time * 0.31) * 0.08;
  });

  return (
    <>
      <mesh ref={coreRef} scale={0.72}>
        <icosahedronGeometry args={[0.88, 1]} />
        <meshBasicMaterial
          color={hdrColor}
          transparent
          opacity={0.085}
          blending={AdditiveBlending}
          depthWrite={false}
          toneMapped={false}
        />
      </mesh>

      <pointLight
        color={accentColor}
        intensity={2.8}
        distance={2.4}
        decay={2}
      />
    </>
  );
}
