import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  DEMO_COMPANIES,
  EVIDENCE_DETAILS_STORE,
} from "./company-intelligence.ts";
import type {
  CompanyProfile,
  EvidenceDetail,
} from "./company-intelligence.ts";

/**
 * Fixture Realism Drift Validator
 * Ensures no synthetic company, filing, evidence citation, or identifier
 * drifts toward looking like real market data without explicit demo markers.
 */
function validateCompanyDemoMarkers(company: CompanyProfile): void {
  assert.equal(
    company.isSynthetic,
    true,
    `Company ${company.symbol} must have isSynthetic=true`
  );
  assert.equal(
    company.origin,
    "synthetic_demo",
    `Company ${company.symbol} must have origin='synthetic_demo'`
  );
  assert.match(
    company.cin,
    /\(Demo\)$/,
    `Company ${company.symbol} CIN "${company.cin}" must end with explicit "(Demo)" marker`
  );
  assert.match(
    company.cin,
    /^SYN-/,
    `Company ${company.symbol} CIN "${company.cin}" must start with "SYN-" prefix`
  );
  assert.match(
    company.isin,
    /\(Demo\)$/,
    `Company ${company.symbol} ISIN "${company.isin}" must end with explicit "(Demo)" marker`
  );
  assert.match(
    company.isin,
    /^SYN-/,
    `Company ${company.symbol} ISIN "${company.isin}" must start with "SYN-" prefix`
  );
  assert.ok(
    company.exchange.includes("Demo") || company.exchange.includes("Synthetic"),
    `Company ${company.symbol} exchange "${company.exchange}" must identify as Demo or Synthetic`
  );

  // Validate all filings carry explicit demo markers
  for (const filing of company.filings) {
    assert.equal(
      filing.isSynthetic,
      true,
      `Filing ${filing.id} in ${company.symbol} must have isSynthetic=true`
    );
    assert.ok(
      filing.title.includes("[Synthetic Demo]") || filing.title.includes("(Demo)"),
      `Filing "${filing.title}" in ${company.symbol} must carry "[Synthetic Demo]" or "(Demo)" in title`
    );
    assert.ok(
      filing.exchange.includes("Demo") || filing.exchange.includes("Synthetic"),
      `Filing exchange "${filing.exchange}" in ${company.symbol} must carry Demo or Synthetic indicator`
    );
  }

  // Validate relationships carry explicit synthetic reference indicators
  for (const rel of company.relationships) {
    assert.equal(
      rel.isSynthetic,
      true,
      `Relationship ${rel.id} in ${company.symbol} must have isSynthetic=true`
    );
    assert.ok(
      rel.sourceReference.includes("[Demo") || rel.sourceReference.includes("(Demo)"),
      `Relationship "${rel.name}" source "${rel.sourceReference}" must contain "[Demo" marker`
    );
  }
}

function validateEvidenceDetailDemoMarkers(id: string, ev: EvidenceDetail): void {
  assert.equal(
    ev.isSynthetic,
    true,
    `Evidence record ${id} must have isSynthetic=true`
  );
  assert.equal(
    ev.origin,
    "synthetic_demo",
    `Evidence record ${id} must have origin='synthetic_demo'`
  );
  assert.ok(
    ev.sourceDocument?.includes("[Synthetic Fixture]") ||
      ev.sourceDocument?.includes("(Demo)") ||
      ev.sourceDocument?.includes("[Demo]"),
    `Evidence record ${id} sourceDocument "${ev.sourceDocument}" must explicitly identify as Synthetic Fixture or Demo`
  );
  if (ev.sourceSection) {
    assert.ok(
      ev.sourceSection.includes("[Demo]") || ev.sourceSection.includes("(Demo)"),
      `Evidence record ${id} sourceSection "${ev.sourceSection}" must carry "[Demo]" marker`
    );
  }
  if (ev.verbatimExcerpt) {
    assert.ok(
      ev.verbatimExcerpt.includes("[Fictional Demo Citation]") ||
        ev.verbatimExcerpt.includes("Demo"),
      `Evidence record ${id} verbatimExcerpt "${ev.verbatimExcerpt}" must state it is a fictional demo citation`
    );
  }
}

describe("Fixture Realism Drift Guard (CI Safety Checks)", () => {
  it("verifies all DEMO_COMPANIES carry required (Demo) markers and SYN- prefixes", () => {
    assert.ok(DEMO_COMPANIES.length >= 2, "Must contain at least 2 demo companies");
    for (const company of DEMO_COMPANIES) {
      validateCompanyDemoMarkers(company);
    }
  });

  it("verifies all EVIDENCE_DETAILS_STORE entries identify as synthetic demo citations", () => {
    const keys = Object.keys(EVIDENCE_DETAILS_STORE);
    assert.ok(keys.length >= 20, "Evidence store must contain expected fixtures");
    for (const [id, ev] of Object.entries(EVIDENCE_DETAILS_STORE)) {
      validateEvidenceDetailDemoMarkers(id, ev);
    }
  });

  describe("Realism Drift Failure Invariant (Regression Tests)", () => {
    it("fails when (Demo) is removed from company CIN", () => {
      const companyCopy: CompanyProfile = {
        ...DEMO_COMPANIES[0],
        cin: "L28910MH2012PLC987654", // Stripped (Demo) and SYN-
      };
      assert.throws(() => validateCompanyDemoMarkers(companyCopy), {
        name: "AssertionError",
      });
    });

    it("fails when (Demo) is removed from company ISIN", () => {
      const companyCopy: CompanyProfile = {
        ...DEMO_COMPANIES[0],
        isin: "INE999X01099", // Stripped (Demo) and SYN-
      };
      assert.throws(() => validateCompanyDemoMarkers(companyCopy), {
        name: "AssertionError",
      });
    });

    it("fails when [Synthetic Demo] is removed from a filing title", () => {
      const companyCopy: CompanyProfile = {
        ...DEMO_COMPANIES[0],
        filings: [
          {
            ...DEMO_COMPANIES[0].filings[0],
            title: "Board Meeting Outcome: Unaudited Financial Results Q2", // Stripped demo tag
          },
        ],
      };
      assert.throws(() => validateCompanyDemoMarkers(companyCopy), {
        name: "AssertionError",
      });
    });

    it("fails when [Synthetic Fixture] is removed from evidence sourceDocument", () => {
      const evCopy: EvidenceDetail = {
        ...EVIDENCE_DETAILS_STORE["ev-zenith-overview"],
        sourceDocument: "Master Corporate Profile, Ministry of Corporate Affairs", // Stripped synthetic indicator
      };
      assert.throws(
        () => validateEvidenceDetailDemoMarkers("ev-zenith-overview", evCopy),
        {
          name: "AssertionError",
        }
      );
    });

    it("fails when isSynthetic is flipped to false on an evidence record", () => {
      const evCopy: EvidenceDetail = {
        ...EVIDENCE_DETAILS_STORE["ev-zenith-revenue"],
        isSynthetic: false,
      };
      assert.throws(
        () => validateEvidenceDetailDemoMarkers("ev-zenith-revenue", evCopy),
        {
          name: "AssertionError",
        }
      );
    });
  });
});
