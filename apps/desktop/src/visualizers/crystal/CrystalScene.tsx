import { Canvas } from "@react-three/fiber";
import { ACESFilmicToneMapping } from "three";

import { CrystalAura } from "./CrystalAura";
import { CrystalBody } from "./CrystalBody";
import { CrystalInnerCore } from "./CrystalInnerCore";
import { CrystalParticles } from "./effects/CrystalParticles";
import { CrystalPostProcessing } from "./effects/CrystalPostProcessing";
import { CrystalStage } from "./effects/CrystalStage";
import { CrystalEnvironment } from "./lighting/CrystalEnvironment";
import { CrystalLighting } from "./lighting/CrystalLighting";

interface CrystalSceneProps {
  accentColor: string;
}

export function CrystalScene({ accentColor }: CrystalSceneProps) {
  return (
    <Canvas
      camera={{ position: [0, 0.15, 6.3], fov: 38 }}
      dpr={[1, 2]}
      gl={{
        antialias: true,
        alpha: true,
        toneMapping: ACESFilmicToneMapping,
        toneMappingExposure: 0.78,
      }}
    >
      <CrystalEnvironment accentColor={accentColor} />
      <CrystalLighting />
      <CrystalAura accentColor={accentColor} />
      <CrystalStage accentColor={accentColor} />
      <CrystalParticles accentColor={accentColor} />

      <group scale={0.88} position={[0, 0.25, 0]}>
        <CrystalInnerCore accentColor={accentColor} />
        <CrystalBody accentColor={accentColor} />
      </group>

      <CrystalPostProcessing />
    </Canvas>
  );
}
