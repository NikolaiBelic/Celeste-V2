import { Bloom, EffectComposer } from "@react-three/postprocessing";

export function CrystalPostProcessing() {
  return (
    <EffectComposer multisampling={0}>
      <Bloom
        intensity={1.35}
        luminanceThreshold={0.85}
        luminanceSmoothing={0.18}
        mipmapBlur
      />
    </EffectComposer>
  );
}