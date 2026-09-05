import { AdditiveBlending } from "three";

interface CrystalAuraProps {
  accentColor: string;
}

export function CrystalAura({ accentColor }: CrystalAuraProps) {
  return (
    <group position={[0, 0.15, -1.9]}>
      <mesh scale={[2.65, 2.65, 1]}>
        <circleGeometry args={[1, 96]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.022}
          blending={AdditiveBlending}
          depthWrite={false}
          toneMapped={false}
        />
      </mesh>
      <mesh scale={[1.85, 1.85, 1]} position={[0.12, 0.08, 0.05]}>
        <circleGeometry args={[1, 96]} />
        <meshBasicMaterial
          color={accentColor}
          transparent
          opacity={0.032}
          blending={AdditiveBlending}
          depthWrite={false}
          toneMapped={false}
        />
      </mesh>
    </group>
  );
}
