"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import cytoscape, { Core, EventObject } from "cytoscape";
import type { CompanyProfile, RelationshipItem } from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";

interface RelationshipMapProps {
  company: CompanyProfile;
  relationships: RelationshipItem[];
  onInspectSource: (evidenceId: string) => void;
}

type NodeFilter = "all" | "supplier" | "customer" | "competitor" | "raw_material";

export function RelationshipMap({
  company,
  relationships,
  onInspectSource,
}: RelationshipMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  const [selectedRel, setSelectedRel] = useState<RelationshipItem | null>(relationships[0] ?? null);
  const [filter, setFilter] = useState<NodeFilter>("all");
  const [viewMode, setViewMode] = useState<"graph" | "table">("graph");

  const filteredRelationships = relationships.filter((rel) => {
    if (filter === "all") return true;
    return rel.type === filter;
  });

  const initCytoscape = useCallback(() => {
    if (!containerRef.current) return;

    // Destroy existing instance if any
    if (cyRef.current) {
      cyRef.current.destroy();
      cyRef.current = null;
    }

    // Prepare Cytoscape elements
    const elements: cytoscape.ElementDefinition[] = [];

    // Central Node
    elements.push({
      data: {
        id: company.id,
        label: company.symbol,
        name: company.legalName,
        type: "central",
        level: 3, // central concentric level
      },
    });

    // Relationship Nodes and Edges
    filteredRelationships.forEach((rel) => {
      const isSupplier = rel.type === "supplier";
      const isCustomer = rel.type === "customer";
      const isCompetitor = rel.type === "competitor";
      const isRawMat = rel.type === "raw_material";

      // Short node label
      const shortLabel = rel.ticker ?? rel.name.replace(/(Ltd|Corp|Systems|Technologies|Industries|Materials)/gi, "").trim();

      elements.push({
        data: {
          id: rel.id,
          label: shortLabel,
          name: rel.name,
          type: rel.type,
          evidence: rel.evidenceStatus,
          concentration: rel.concentrationPct ?? 0,
          relData: rel,
          level: isSupplier || isRawMat ? 2 : isCustomer ? 1 : 2,
        },
      });

      // Edge
      let source = company.id;
      let target = rel.id;
      let edgeLabel = "";

      if (isSupplier || isRawMat) {
        source = rel.id;
        target = company.id;
        edgeLabel = rel.concentrationPct ? `${rel.concentrationPct}% spend` : "supplies";
      } else if (isCustomer) {
        source = company.id;
        target = rel.id;
        edgeLabel = rel.concentrationPct ? `${rel.concentrationPct}% rev` : "buys";
      } else if (isCompetitor) {
        source = company.id;
        target = rel.id;
        edgeLabel = "peer";
      }

      elements.push({
        data: {
          id: `edge-${rel.id}`,
          source,
          target,
          label: edgeLabel,
          evidence: rel.evidenceStatus,
          isCompetitor,
        },
      });
    });

    // Cytoscape Configuration
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      boxSelectionEnabled: false,
      autounselectify: false,
      minZoom: 0.4,
      maxZoom: 2.5,
      style: [
        {
          selector: "node",
          style: {
            "label": "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "font-family": "Inter, ui-sans-serif, system-ui, sans-serif",
            "font-size": "10px",
            "font-weight": "bold",
            "text-wrap": "wrap",
            "text-max-width": "64px",
            "transition-property": "border-width, border-color, background-color, transform",
            "transition-duration": 0.2,
          },
        },
        {
          selector: 'node[type = "central"]',
          style: {
            "shape": "ellipse",
            "background-color": "#122a28",
            "border-width": 3,
            "border-color": "#44ce9a",
            "color": "#e6fff4",
            "width": 78,
            "height": 78,
            "font-size": "12px",
            "font-weight": "bold",
          },
        },
        {
          selector: 'node[type = "supplier"]',
          style: {
            "shape": "round-rectangle",
            "background-color": "#0d2238",
            "border-width": 2,
            "border-color": "#38bdf8",
            "color": "#e0f2fe",
            "width": 64,
            "height": 64,
          },
        },
        {
          selector: 'node[type = "customer"]',
          style: {
            "shape": "ellipse",
            "background-color": "#0a3026",
            "border-width": 2,
            "border-color": "#34d399",
            "color": "#ecfdf5",
            "width": 66,
            "height": 66,
          },
        },
        {
          selector: 'node[type = "competitor"]',
          style: {
            "shape": "diamond",
            "background-color": "#28173d",
            "border-width": 2,
            "border-color": "#c084fc",
            "color": "#f5f3ff",
            "width": 68,
            "height": 68,
          },
        },
        {
          selector: 'node[type = "raw_material"]',
          style: {
            "shape": "round-octagon",
            "background-color": "#36210f",
            "border-width": 2,
            "border-color": "#fb923c",
            "color": "#fff7ed",
            "width": 64,
            "height": 64,
          },
        },
        {
          selector: "node:selected",
          style: {
            "border-color": "#ffffff",
            "border-width": 4,
          },
        },
        {
          selector: "edge",
          style: {
            "curve-style": "bezier",
            "width": 1.8,
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#475569",
            "line-color": "#334155",
            "arrow-scale": 0.8,
            "label": "data(label)",
            "font-size": "9px",
            "color": "#94a3b8",
            "text-rotation": "autorotate",
            "text-margin-y": -7,
            "font-family": "ui-monospace, monospace",
          },
        },
        {
          selector: 'edge[evidence = "disclosed"]',
          style: {
            "line-style": "solid",
          },
        },
        {
          selector: 'edge[evidence = "inferred"]',
          style: {
            "line-style": "dashed",
            "line-dash-pattern": [6, 4],
          },
        },
        {
          selector: 'edge[evidence = "unconfirmed"]',
          style: {
            "line-style": "dotted",
            "line-dash-pattern": [3, 3],
          },
        },
        {
          selector: "edge[?isCompetitor]",
          style: {
            "target-arrow-shape": "none",
            "line-style": "dashed",
          },
        },
      ],
      layout: {
        name: "concentric",
        concentric: (node) => node.data("level") || 1,
        levelWidth: () => 1,
        padding: 50,
        animate: false,
        spacingFactor: 1.3,
      },
    });

    // Handle node selection
    cy.on("tap", "node", (evt: EventObject) => {
      const node = evt.target;
      const data = node.data();
      if (data.type === "central") {
        // Keep or clear
      } else if (data.relData) {
        setSelectedRel(data.relData as RelationshipItem);
      }
    });

    // Handle background click (deselects)
    cy.on("tap", (evt: EventObject) => {
      if (evt.target === cy) {
        // Clicked background
      }
    });

    cyRef.current = cy;

    // Fit view
    cy.ready(() => {
      cy.fit(undefined, 35);
    });
  }, [company, filteredRelationships]);

  useEffect(() => {
    if (viewMode === "graph") {
      initCytoscape();
    }
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [initCytoscape, viewMode]);

  // Zoom / Reset Handlers
  const handleZoomIn = () => {
    if (!cyRef.current) return;
    cyRef.current.zoom({
      level: cyRef.current.zoom() * 1.25,
      renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 },
    });
  };

  const handleZoomOut = () => {
    if (!cyRef.current) return;
    cyRef.current.zoom({
      level: cyRef.current.zoom() * 0.8,
      renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 },
    });
  };

  const handleReset = () => {
    if (!cyRef.current) return;
    cyRef.current.fit(undefined, 35);
  };

  return (
    <div className="relationship-map-container">
      <header className="relationship-map-header">
        <div>
          <h3 className="section-heading">Relationship &amp; Supply Chain Ecosystem</h3>
          <span className="section-subheading">
            Interactive network mapping suppliers, buyers, peers, and commodity dependencies
          </span>
        </div>

        <div className="header-controls">
          <div className="segmented-control" role="group" aria-label="View mode">
            <button
              type="button"
              className={`segment-btn ${viewMode === "graph" ? "active" : ""}`}
              onClick={() => setViewMode("graph")}
            >
              Network Graph
            </button>
            <button
              type="button"
              className={`segment-btn ${viewMode === "table" ? "active" : ""}`}
              onClick={() => setViewMode("table")}
            >
              Adjacency Table
            </button>
          </div>
        </div>
      </header>

      {/* Filter Chips Bar */}
      <div className="graph-filter-bar">
        <span className="filter-label">Filter Entities:</span>
        <div className="filter-chips">
          {(
            [
              ["all", "All Ecosystem"],
              ["supplier", "Suppliers"],
              ["customer", "Customers"],
              ["competitor", "Competitors"],
              ["raw_material", "Commodity Inputs"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              className={`filter-chip ${filter === key ? "active" : ""}`}
              onClick={() => setFilter(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {viewMode === "graph" ? (
        <div className="graph-workspace-layout">
          {/* Graph Viewport */}
          <div className="cytoscape-card">
            <div
              ref={containerRef}
              className="cytoscape-viewport"
              role="region"
              aria-label="Interactive network visualization showing connections between company and suppliers, customers, competitors, and commodities"
            />

            {/* Floating Navigation Controls */}
            <div className="graph-floating-controls" role="toolbar" aria-label="Graph view controls">
              <button
                type="button"
                className="graph-ctrl-btn"
                onClick={handleZoomIn}
                aria-label="Zoom in"
                title="Zoom in"
              >
                +
              </button>
              <button
                type="button"
                className="graph-ctrl-btn"
                onClick={handleZoomOut}
                aria-label="Zoom out"
                title="Zoom out"
              >
                −
              </button>
              <button
                type="button"
                className="graph-ctrl-btn"
                onClick={handleReset}
                aria-label="Reset and center view"
                title="Reset view"
              >
                ⊡
              </button>
            </div>

            {/* Graph Legend */}
            <div className="graph-legend">
              <span className="legend-item">
                <i className="legend-dot dot-supplier" aria-hidden="true" /> Supplier
              </span>
              <span className="legend-item">
                <i className="legend-dot dot-customer" aria-hidden="true" /> Customer
              </span>
              <span className="legend-item">
                <i className="legend-dot dot-competitor" aria-hidden="true" /> Competitor
              </span>
              <span className="legend-item">
                <i className="legend-dot dot-material" aria-hidden="true" /> Raw Material
              </span>
              <span className="legend-item line-legend">
                <span className="line-solid" /> Disclosed
              </span>
              <span className="legend-item line-legend">
                <span className="line-dashed" /> Inferred
              </span>
              <span className="legend-item line-legend">
                <span className="line-dotted" /> Unconfirmed
              </span>
            </div>
          </div>

          {/* Node Inspector Drawer */}
          <div className="node-detail-panel">
            {selectedRel ? (
              <article className="selected-node-article">
                <header className="node-detail-header">
                  <div>
                    <span className="node-type-badge">{selectedRel.type.replace("_", " ").toUpperCase()}</span>
                    <h4 className="node-name">{selectedRel.name}</h4>
                    {selectedRel.ticker && (
                      <span className="node-ticker">Ticker: {selectedRel.ticker}</span>
                    )}
                  </div>
                  <EvidenceBadge
                    status={selectedRel.evidenceStatus}
                    size="sm"
                    interactive
                    onClick={() => onInspectSource(selectedRel.evidenceId)}
                  />
                </header>

                <div className="node-detail-body">
                  <div className="node-role-box">
                    <strong>Commercial Role:</strong>
                    <p>{selectedRel.roleDescription}</p>
                  </div>

                  {selectedRel.concentrationPct !== undefined && selectedRel.concentrationPct !== null && (
                    <div className="node-concentration-box">
                      <span className="concentration-label">
                        {selectedRel.type === "supplier" || selectedRel.type === "raw_material"
                          ? "Share of Direct Spend (COGS):"
                          : "Share of Total Sales (Revenue):"}
                      </span>
                      <strong className="concentration-value">
                        {selectedRel.concentrationPct.toFixed(1)}%
                      </strong>
                    </div>
                  )}

                  <div className="node-rationale-box">
                    <strong>Why this connection matters:</strong>
                    <p>{selectedRel.whyItMatters}</p>
                  </div>

                  <div className="node-source-box">
                    <span className="source-label">Disclosure Reference:</span>
                    <p className="source-citation">{selectedRel.sourceReference}</p>
                  </div>
                </div>

                <footer className="node-detail-footer">
                  <button
                    type="button"
                    className="btn-inspect-evidence"
                    onClick={() => onInspectSource(selectedRel.evidenceId)}
                  >
                    Inspect Level 3 Disclosure ↗
                  </button>
                </footer>
              </article>
            ) : (
              <div className="empty-node-state">
                <p>Click on any node in the network to inspect its relationship details, concentration share, and statutory evidence.</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Accessible Adjacency Table */
        <div className="adjacency-table-card">
          <table className="financial-table">
            <thead>
              <tr>
                <th scope="col">Connected Entity</th>
                <th scope="col">Relationship Type</th>
                <th scope="col">Commercial Role</th>
                <th scope="col" className="col-num">Concentration</th>
                <th scope="col">Evidence</th>
                <th scope="col">Statutory Reference</th>
              </tr>
            </thead>
            <tbody>
              {filteredRelationships.map((rel) => (
                <tr key={rel.id}>
                  <th scope="row">
                    <strong>{rel.name}</strong>
                    {rel.ticker && <span className="text-muted text-xs block">{rel.ticker}</span>}
                  </th>
                  <td>
                    <span className={`inline-block px-2 py-0.5 rounded text-xs uppercase font-semibold ${
                      rel.type === "supplier" ? "text-blue bg-blue-soft" :
                      rel.type === "customer" ? "text-green bg-green-soft" :
                      rel.type === "competitor" ? "text-purple-400 bg-purple-950/40" :
                      "text-amber bg-amber-soft"
                    }`}>
                      {rel.type.replace("_", " ")}
                    </span>
                  </td>
                  <td>
                    <span>{rel.roleDescription}</span>
                    <small className="block text-muted text-xs mt-0.5">{rel.whyItMatters}</small>
                  </td>
                  <td className="cell-num">
                    {rel.concentrationPct ? `${rel.concentrationPct.toFixed(1)}%` : "—"}
                  </td>
                  <td>
                    <EvidenceBadge
                      status={rel.evidenceStatus}
                      size="xs"
                      interactive
                      onClick={() => onInspectSource(rel.evidenceId)}
                    />
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn-inspect-link"
                      onClick={() => onInspectSource(rel.evidenceId)}
                    >
                      {rel.sourceReference} ↗
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
