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
  /*
   * Intensidad con la que cada fragmento responde
   * al Environment global de la escena.
   *
   * Ya no necesitamos pasar un envMap manualmente:
   * meshPhysicalMaterial utiliza scene.environment.
   */
  const environmentIntensity =
    0.75 +
    surfaceEnergy * 0.45 +
    hotSpot * 0.55;

  /*
   * Variación ligera entre fragmentos.
   *
   * Algunas facetas serán más pulidas y otras
   * dispersarán ligeramente más el reflejo.
   */
  const roughness =
    0.16 +
    surfaceEnergy * 0.08;

  return (
    <meshPhysicalMaterial
      /*
       * Obsidiana casi negra.
       *
       * No usamos negro matemático para conservar
       * información en las zonas poco iluminadas.
       */
      color="#111317"

      /*
       * La superficie exterior NO genera naranja.
       * La energía pertenece al interior,
       * las juntas y determinados reflejos.
       */
      emissive="#000000"
      emissiveIntensity={0}

      /*
       * Environment global proporcionado por
       * <Environment> + <Lightformer>.
       */
      envMapIntensity={environmentIntensity}

      /*
       * Superficie sólida y reflectante.
       *
       * Ya no utilizamos transmission:
       * queremos obsidiana/cristal negro,
       * no vidrio transparente.
       */
      roughness={roughness}
      metalness={0.28}

      /*
       * Capa especular exterior.
       */
      clearcoat={0.9}
      clearcoatRoughness={0.1}

      transparent={false}

      /*
       * Conservamos la lectura facetada.
       */
      flatShading
    />
  );
}