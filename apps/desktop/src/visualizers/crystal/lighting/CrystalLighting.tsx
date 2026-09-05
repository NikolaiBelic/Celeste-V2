export function CrystalLighting() {
  return (
    <>
      <ambientLight intensity={0.035} />

      <directionalLight
        position={[4.5, 5.5, 5]}
        color="#e6edf5"
        intensity={1.55}
      />

      <directionalLight
        position={[-5, 1.5, 3]}
        color="#7f8b9a"
        intensity={0.72}
      />

      <directionalLight
        position={[1.5, -3.5, -4]}
        color="#4c5664"
        intensity={0.38}
      />
    </>
  );
}
