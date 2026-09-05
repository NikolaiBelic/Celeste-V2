import type { ColorRepresentation } from "three";

interface CrystalSidesProps {
  accentColor: ColorRepresentation;
  energy: number;
}

export function CrystalSides({
  accentColor,
  energy,
}: CrystalSidesProps) {
  return (
    <meshStandardMaterial
      color="#030304"
      emissive={accentColor}
      emissiveIntensity={0.03 + energy * 0.22}
      roughness={0.3}
      metalness={0.38}
    />
  );
}
