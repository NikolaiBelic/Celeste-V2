import { Color } from "three";
import type { ColorRepresentation } from "three";

interface CrystalSurfaceProps {
  accentColor: ColorRepresentation;
  surfaceEnergy: number;
  hotSpot: number;
}

export function CrystalSurface({ surfaceEnergy, hotSpot }: CrystalSurfaceProps) {
  /*
   * Most plates are smoked obsidian. A minority become silver/graphite
   * reflectors; orange never comes from the exterior face itself.
   */
  const silver = Math.max(0, (surfaceEnergy - 0.66) / 0.34);
  const base = new Color("#050609");
  const silverColor = new Color("#6f7884");
  const faceColor = base.clone().lerp(silverColor, silver * 0.72);

  return (
    <meshPhysicalMaterial
      color={faceColor}
      emissive="#000000"
      emissiveIntensity={0}
      envMapIntensity={0.72 + silver * 1.65 + hotSpot * 0.12}
      roughness={0.19 - silver * 0.1}
      metalness={0.18 + silver * 0.28}
      clearcoat={0.95}
      clearcoatRoughness={0.06}
      reflectivity={0.92}
      transparent={false}
      flatShading
    />
  );
}
