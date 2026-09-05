export interface CrystalPieceAppearance {
  surfaceEnergy: number;
  edgeEnergy: number;
  hotSpot: number;
}

function seededRandom(seed: number): number {
  const value = Math.sin(seed * 12.9898) * 43758.5453;
  return value - Math.floor(value);
}

export function createPieceAppearance(pieceId: number): CrystalPieceAppearance {
  const surfaceVariation = seededRandom(pieceId + 31);
  const edgeVariation = seededRandom(pieceId + 79);
  const hotSpotRoll = seededRandom(pieceId + 137);
  const hotSpotStrength = seededRandom(pieceId + 211);

  // Broad contrast: most black, a useful minority silver/graphite.
  const surfaceEnergy = Math.pow(surfaceVariation, 1.45);

  // Most edges are dead. Only the upper tail becomes visibly energized.
  const edgeEnergy = edgeVariation > 0.68
    ? Math.pow((edgeVariation - 0.68) / 0.32, 0.8)
    : 0;

  // Very sparse incandescent plates/cracks.
  const hotSpot = hotSpotRoll > 0.91
    ? 0.68 + hotSpotStrength * 0.32
    : 0;

  return { surfaceEnergy, edgeEnergy, hotSpot };
}
