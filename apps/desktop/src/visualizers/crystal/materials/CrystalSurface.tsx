import type { ColorRepresentation } from "three";

interface CrystalSurfaceProps {
  accentColor: ColorRepresentation;
  surfaceEnergy: number;
  hotSpot: number;
}

export function CrystalSurface({
  surfaceEnergy,
  hotSpot,
}: CrystalSurfaceProps) {
  const environmentIntensity =
    1.05 + surfaceEnergy * 0.8 + hotSpot * 0.45;

  const roughness =
    0.075 + (1 - surfaceEnergy) * 0.075;

  return (
    <meshPhysicalMaterial
      color="#050609"
      emissive="#000000"
      emissiveIntensity={0}
      envMapIntensity={environmentIntensity}
      roughness={roughness}
      metalness={0.48}
      clearcoat={1}
      clearcoatRoughness={0.035}
      reflectivity={1}
      transparent={false}
      flatShading
    />
  );
}
