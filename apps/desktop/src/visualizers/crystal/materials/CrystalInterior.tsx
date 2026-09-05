import { AdditiveBlending, Color } from "three";
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
  const hdrColor = new Color(accentColor).multiplyScalar(
    1.8 + energy * 2.2 + hotSpot * 4.8,
  );

  return (
    <meshBasicMaterial
      color={hdrColor}
      transparent
      opacity={0.12 + energy * 0.2 + hotSpot * 0.34}
      blending={AdditiveBlending}
      depthWrite={false}
      toneMapped={false}
    />
  );
}
