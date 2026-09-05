import { Bloom, EffectComposer, Vignette } from "@react-three/postprocessing";

export function CrystalPostProcessing() {
  return (
    <EffectComposer multisampling={0}>
      <Bloom
        intensity={1.75}
        luminanceThreshold={1.05}
        luminanceSmoothing={0.16}
        mipmapBlur
      />
      <Vignette
        eskil={false}
        offset={0.2}
        darkness={0.72}
      />
    </EffectComposer>
  );
}
