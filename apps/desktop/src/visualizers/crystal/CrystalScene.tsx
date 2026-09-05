import { Canvas } from "@react-three/fiber";
import { ACESFilmicToneMapping } from "three";

import { CrystalAura } from "./CrystalAura";
import { CrystalBody } from "./CrystalBody";
import { CrystalInnerCore } from "./CrystalInnerCore";
import { CrystalPostProcessing } from "./effects/CrystalPostProcessing";
import { CrystalEnvironment } from "./lighting/CrystalEnvironment";
import { CrystalLighting } from "./lighting/CrystalLighting";

interface CrystalSceneProps {
  accentColor: string;
}

export function CrystalScene({ accentColor }: CrystalSceneProps) {
  return (
    <Canvas
      camera={{
        position: [0, 0, 5],
        fov: 38,
      }}
      dpr={[1, 2]}
      gl={{
        antialias: true,
        alpha: true,
        toneMapping: ACESFilmicToneMapping,
        toneMappingExposure: 0.92,
      }}
    >
      <CrystalEnvironment accentColor={accentColor} />
      <CrystalLighting />
      <CrystalAura accentColor={accentColor} />

      <group scale={0.72} position={[0, 0.08, 0]}>
        <CrystalInnerCore accentColor={accentColor} />
        <CrystalBody accentColor={accentColor} />
      </group>

      <CrystalPostProcessing />
    </Canvas>
  );
}
