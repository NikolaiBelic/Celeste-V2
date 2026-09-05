import { AdditiveBlending } from "three";
import type { ColorRepresentation } from "three";

interface CrystalInteriorProps {
  accentColor: ColorRepresentation;
  energy: number;
  hotSpot: number;
}

export function CrystalInterior({
  accentColor,
  energy,
  hotSpot,
}: CrystalInteriorProps) {
  const emissiveIntensity =
    0.25 +
    energy * 0.45 +
    hotSpot * 1.1;

  return (
    <meshStandardMaterial
      color="#120704"
      emissive={accentColor}
      emissiveIntensity={emissiveIntensity}
      roughness={0.38}
      metalness={0.05}
      transparent
      opacity={0.78}
      blending={AdditiveBlending}
      depthWrite={false}
      toneMapped={false}
    />
  );
}