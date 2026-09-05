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
      color="#080504"
      emissive={accentColor}
      emissiveIntensity={0.015 + energy * 0.045}
      roughness={0.46}
      metalness={0.16}
    />
  );
}