import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { calculateCommodityImpact } from "./supply-chain-impact.ts";

describe("Commodity Sensitivity & Margin Impact Calculations", () => {
  it("computes accurate baseline and +10% shock for Zenith Precision (Steel)", () => {
    const result = calculateCommodityImpact({
      annualRevenueCr: 1825.40,
      annualCogsCr: 1020.20,
      cogsSharePct: 38.0,
      priceChangePct: 10,
    });

    // Material baseline spend
    assert.ok(Math.abs(result.baselineMaterialCostCr - 387.676) < 0.001);

    // +10% cost increase: ₹38.7676 Cr
    assert.ok(Math.abs(result.additionalCostCr - 38.7676) < 0.001);
    assert.ok(Math.abs(result.modelledCogsCr - 1058.9676) < 0.001);

    // Baseline gross margin: 44.11115%
    assert.ok(Math.abs(result.baselineGrossMarginPct - 44.11115) < 0.001);

    // Modelled gross margin: 41.98736%
    assert.ok(Math.abs(result.modelledGrossMarginPct - 41.98736) < 0.001);

    // Margin compression: 212.38 bps
    assert.ok(Math.abs(result.marginCompressionBps - 212.379) < 0.01);
    assert.ok(Math.abs(result.marginDeltaPctPoints - (-2.12379)) < 0.001);

    // Period & Denominator Identity Check:
    // Modelled Margin must exactly equal Baseline Margin minus (Compression BPS / 100)
    const expectedFromBps = result.baselineGrossMarginPct - (result.marginCompressionBps / 100);
    assert.ok(Math.abs(result.modelledGrossMarginPct - expectedFromBps) < 0.00001);
  });

  it("computes softening commodity price (-15% deflation) for Zenith", () => {
    const result = calculateCommodityImpact({
      annualRevenueCr: 1825.40,
      annualCogsCr: 1020.20,
      cogsSharePct: 38.0,
      priceChangePct: -15,
    });

    // Cost reduction: -₹58.1514 Cr
    assert.ok(Math.abs(result.additionalCostCr - (-58.1514)) < 0.001);
    assert.ok(Math.abs(result.modelledCogsCr - 962.0486) < 0.001);

    // Gross margin expands from 44.11% to 47.30%
    assert.ok(result.modelledGrossMarginPct > result.baselineGrossMarginPct);
    assert.ok(Math.abs(result.modelledGrossMarginPct - 47.2968) < 0.001);

    // Negative compression = expansion
    assert.ok(result.marginCompressionBps < 0);
    assert.ok(Math.abs(result.marginCompressionBps - (-318.568)) < 0.01);
  });

  it("computes accurate baseline and +10% shock for Apex Ferrous (Scrap)", () => {
    const result = calculateCommodityImpact({
      annualRevenueCr: 1280.00,
      annualCogsCr: 812.80,
      cogsSharePct: 52.0,
      priceChangePct: 10,
    });

    // Material baseline spend: 812.80 * 0.52 = 422.656 Cr
    assert.ok(Math.abs(result.baselineMaterialCostCr - 422.656) < 0.001);

    // +10% shock: +₹42.2656 Cr
    assert.ok(Math.abs(result.additionalCostCr - 42.2656) < 0.001);

    // Baseline gross margin: 36.50%
    assert.ok(Math.abs(result.baselineGrossMarginPct - 36.50) < 0.001);

    // Modelled gross margin: ((1280 - 855.0656) / 1280) * 100 = 33.198%
    assert.ok(Math.abs(result.modelledGrossMarginPct - 33.198) < 0.001);

    // Margin compression: (42.2656 / 1280) * 10000 = 330.2 bps
    assert.ok(Math.abs(result.marginCompressionBps - 330.2) < 0.01);
  });

  it("handles zero price change (0% shock) with exact identity", () => {
    const result = calculateCommodityImpact({
      annualRevenueCr: 1825.40,
      annualCogsCr: 1020.20,
      cogsSharePct: 38.0,
      priceChangePct: 0,
    });

    assert.equal(result.additionalCostCr, 0);
    assert.equal(result.marginCompressionBps, 0);
    assert.equal(result.marginDeltaPctPoints, 0);
    assert.equal(result.modelledGrossMarginPct, result.baselineGrossMarginPct);
  });

  it("rejects non-positive annual revenue", () => {
    assert.throws(
      () =>
        calculateCommodityImpact({
          annualRevenueCr: 0,
          annualCogsCr: 500,
          cogsSharePct: 30,
          priceChangePct: 10,
        }),
      /annualRevenueCr must be greater than zero/
    );
  });
});
