import { AdditiveBlending, DoubleSide } from "three";

interface CrystalStageProps {
  accentColor: string;
}

export function CrystalStage({ accentColor }: CrystalStageProps) {
  return (
    <group position={[0, -1.72, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[2.8, 96]} />
        <meshPhysicalMaterial
          color="#030303"
          roughness={0.2}
          metalness={0.72}
          clearcoat={1}
          clearcoatRoughness={0.12}
          transparent
          opacity={0.72}
        />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.012, 0]}>
        <ringGeometry args={[0.72, 0.735, 128]} />
        <meshBasicMaterial color={accentColor} transparent opacity={0.8} blending={AdditiveBlending} depthWrite={false} toneMapped={false} side={DoubleSide} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.014, 0]}>
        <ringGeometry args={[1.35, 1.365, 128]} />
        <meshBasicMaterial color={accentColor} transparent opacity={0.42} blending={AdditiveBlending} depthWrite={false} toneMapped={false} side={DoubleSide} />
      </mesh>

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.016, 0]}>
        <ringGeometry args={[2.05, 2.065, 128]} />
        <meshBasicMaterial color={accentColor} transparent opacity={0.2} blending={AdditiveBlending} depthWrite={false} toneMapped={false} side={DoubleSide} />
      </mesh>

      <pointLight position={[0, 0.12, 0]} color={accentColor} intensity={4.5} distance={3.4} decay={2} />
    </group>
  );
}
