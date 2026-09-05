import type { ColorRepresentation } from "three";

interface CrystalSurfaceProps {
  accentColor: ColorRepresentation;
  brightness: number;
}

export function CrystalSurface({
  accentColor,
  brightness,
}: CrystalSurfaceProps) {
  return (
    <meshPhysicalMaterial
        color="#070605"
        emissive={accentColor}
        emissiveIntensity={0.015 + brightness * 0.07}

        roughness={0.2}
        metalness={0.15}

        transparent
        opacity={0.78}

        transmission={0.16}
        thickness={0.35}
        ior={1.7}

        clearcoat={0.55}
        clearcoatRoughness={0.22}

        flatShading
        />
  );
}