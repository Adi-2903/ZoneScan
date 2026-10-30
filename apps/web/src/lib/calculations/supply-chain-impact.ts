/**
 * ZoneScan — Commodity Price Sensitivity Calculator
 * 
 * Deterministic mathematical model computing gross margin impact and cost deltas
 * from commodity input price shocks.
 * 
 * Period & Denominator Rule:
 * All calculations MUST use the identical reporting period and currency denominator
 * (Annual Revenue from Operations for the corresponding baseline fiscal year).
 */

export interface CommodityImpactInput {
  /** Annual Revenue from Operations for baseline period (₹ Cr) */
  annualRevenueCr: number;
  /** Annual Cost of Goods Sold / Materials Consumed for baseline period (₹ Cr) */
  annualCogsCr: number;
  /** Commodity input share of total COGS (0 to 100 percentage) */
  cogsSharePct: number;
  /** Simulated commodity price shock (-100 to +100 percentage) */
  priceChangePct: number;
}

export interface CommodityImpactResult {
  /** Total baseline expenditure on this raw material (₹ Cr) */
  baselineMaterialCostCr: number;
  /** Additional cost incurred due to price shock (₹ Cr) */
  additionalCostCr: number;
  /** Modelled total COGS after shock (₹ Cr) */
  modelledCogsCr: number;
  /** Baseline Gross Margin percentage (%) */
  baselineGrossMarginPct: number;
  /** Modelled Gross Margin percentage after shock (%) */
  modelledGrossMarginPct: number;
  /** Change in gross margin in percentage points (modelled - baseline) */
  marginDeltaPctPoints: number;
  /** Margin compression in basis points (positive = compression/reduction) */
  marginCompressionBps: number;
}

/**
 * Calculates the deterministic cost and margin impact of a commodity price movement.
 * 
 * Mathematical identities:
 * 1. baselineMaterialCostCr = annualCogsCr * (cogsSharePct / 100)
 * 2. additionalCostCr = baselineMaterialCostCr * (priceChangePct / 100)
 * 3. modelledCogsCr = annualCogsCr + additionalCostCr
 * 4. baselineGrossMarginPct = ((annualRevenueCr - annualCogsCr) / annualRevenueCr) * 100
 * 5. modelledGrossMarginPct = ((annualRevenueCr - modelledCogsCr) / annualRevenueCr) * 100
 * 6. marginDeltaPctPoints = modelledGrossMarginPct - baselineGrossMarginPct
 * 7. marginCompressionBps = (additionalCostCr / annualRevenueCr) * 10,000
 */
export function calculateCommodityImpact(input: CommodityImpactInput): CommodityImpactResult {
  const { annualRevenueCr, annualCogsCr, cogsSharePct, priceChangePct } = input;

  if (annualRevenueCr <= 0) {
    throw new Error("annualRevenueCr must be greater than zero for valid margin calculation.");
  }

  // Material spend in baseline period (₹ Cr)
  const baselineMaterialCostCr = annualCogsCr * (cogsSharePct / 100);

  // Additional cost from price shock (₹ Cr)
  const additionalCostCr = baselineMaterialCostCr * (priceChangePct / 100);

  // Modelled COGS after cost impact (₹ Cr)
  const modelledCogsCr = annualCogsCr + additionalCostCr;

  // Baseline Gross Margin %
  const baselineGrossMarginPct = ((annualRevenueCr - annualCogsCr) / annualRevenueCr) * 100;

  // Modelled Gross Margin %
  const modelledGrossMarginPct = ((annualRevenueCr - modelledCogsCr) / annualRevenueCr) * 100;

  // Margin Delta in percentage points (negative when costs increase)
  const marginDeltaPctPoints = modelledGrossMarginPct - baselineGrossMarginPct;

  // Margin compression in basis points (1 percentage point = 100 bps)
  // Positive bps = compression (margin reduction); negative bps = margin expansion
  const marginCompressionBps = (additionalCostCr / annualRevenueCr) * 10000;

  return {
    baselineMaterialCostCr,
    additionalCostCr,
    modelledCogsCr,
    baselineGrossMarginPct,
    modelledGrossMarginPct,
    marginDeltaPctPoints,
    marginCompressionBps,
  };
}
