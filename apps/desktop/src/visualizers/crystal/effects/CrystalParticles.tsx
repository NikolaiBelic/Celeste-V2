import { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { AdditiveBlending, BufferAttribute, Color } from "three";
import type { Points } from "three";

interface CrystalParticlesProps {
  accentColor: string;
}

function seededRandom(seed: number): number {
  const value = Math.sin(seed * 91.3458) * 47453.5453;
  return value - Math.floor(value);
}

export function CrystalParticles({ accentColor }: CrystalParticlesProps) {
  const ref = useRef<Points>(null);
  const positions = useMemo(() => {
    const count = 150;
    const data = new Float32Array(count * 3);
    for (let i = 0; i < count; i += 1) {
      const angle = seededRandom(i + 1) * Math.PI * 2;
      const radius = 1.05 + seededRandom(i + 40) * 2.1;
      data[i * 3] = Math.cos(angle) * radius;
      data[i * 3 + 1] = (seededRandom(i + 80) - 0.5) * 3.6;
      data[i * 3 + 2] = (seededRandom(i + 120) - 0.5) * 1.7;
    }
    return data;
  }, []);

  const color = useMemo(() => new Color(accentColor).multiplyScalar(3.4), [accentColor]);

  useFrame((state) => {
    if (!ref.current) return;
    const t = state.clock.elapsedTime;
    ref.current.rotation.z = t * 0.012;
    ref.current.rotation.y = Math.sin(t * 0.11) * 0.05;
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial
        color={color}
        size={0.018}
        sizeAttenuation
        transparent
        opacity={0.78}
        blending={AdditiveBlending}
        depthWrite={false}
        toneMapped={false}
      />
    </points>
  );
}
