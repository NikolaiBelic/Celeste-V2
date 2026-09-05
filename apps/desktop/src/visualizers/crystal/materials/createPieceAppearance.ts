export interface CrystalPieceAppearance {
  surfaceEnergy: number;
  edgeEnergy: number;
  hotSpot: number;
}

function seededRandom(seed: number): number {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

export function createPieceAppearance(
  pieceId: number,
): CrystalPieceAppearance {
  const surfaceVariation = seededRandom(pieceId + 31);
  const edgeVariation = seededRandom(pieceId + 79);
  const hotSpotRoll = seededRandom(pieceId + 137);
  const hotSpotStrength = seededRandom(pieceId + 211);

  /*
   * La mayoría de las caras permanecen muy oscuras.
   * Algunas reciben algo más de energía.
   */
  const surfaceEnergy =
    Math.pow(surfaceVariation, 2.2);

  /*
   * Las aristas tienen una distribución más contrastada:
   * muchas discretas, algunas claramente energizadas.
   */
  const edgeEnergy =
    Math.pow(edgeVariation, 1.65);

  /*
   * Solo una minoría de piezas son "hot spots".
   */
  const hotSpot =
    hotSpotRoll > 0.86
      ? 0.55 + hotSpotStrength * 0.45
      : 0;

  return {
    surfaceEnergy,
    edgeEnergy,
    hotSpot,
  };
}