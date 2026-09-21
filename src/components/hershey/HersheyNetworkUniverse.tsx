"use client";

import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { AlertCircle, Box, ChevronRight, CircleDot, Network, Orbit, Sparkles } from "lucide-react";
import { GraphEdge, GraphNode, loadEnrichedArtifacts } from "@/lib/hershey/enrichedArtifacts";

type PositionedNode = GraphNode & { x: number; y: number; color: string };

const colors = ["#70d8ff", "#72e3bb", "#e8be68", "#bba2ff", "#fa8f82", "#76a9ff", "#b1e27e", "#f3a8d3"];

function shortStatus(value?: string) {
  return value?.replaceAll("_", " ") || "modeled context";
}

function positionNodes(nodes: GraphNode[]): PositionedNode[] {
  return nodes.slice(0, 16).map((node, index) => {
    const theta = (index / Math.max(nodes.length, 1)) * Math.PI * 2 - Math.PI / 2;
    const radiusX = 38 + (index % 3) * 5;
    const radiusY = 32 + (index % 4) * 4;
    return { ...node, x: 50 + Math.cos(theta) * radiusX, y: 49 + Math.sin(theta) * radiusY, color: colors[index % colors.length] };
  });
}

export default function HersheyNetworkUniverse({ compact = false }: { compact?: boolean }) {
  const [nodes, setNodes] = useState<PositionedNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [selectedEdgeId, setSelectedEdgeId] = useState<string>("");
  const [error, setError] = useState("");

  useEffect(() => {
    loadEnrichedArtifacts().then((data) => {
      const positioned = positionNodes(data.graph.nodes || []);
      setNodes(positioned);
      setEdges(data.graph.edges || []);
      setSelectedId(positioned[0]?.id || "");
    }).catch((reason: unknown) => setError(reason instanceof Error ? reason.message : "The graph artifacts could not be loaded."));
  }, []);

  const lookup = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [nodes]);
  const selectedNode = lookup.get(selectedId) || nodes[0];
  const selectedEdge = edges.find((edge) => edge.id === selectedEdgeId);

  if (error) return <div className="universe-state universe-state--error"><AlertCircle size={20} /><span>{error}</span></div>;
  if (!nodes.length) return <div className="universe-state"><Sparkles size={20} className="universe-loading-icon" /><span>Loading the audited supply-chain network…</span></div>;

  return (
    <section className={`hershey-universe ${compact ? "hershey-universe--compact" : ""}`} aria-label="Interactive Hershey supply-chain network">
      <div className="universe-header"><div><span className="universe-kicker">Live graph payload</span><h3>Trace the connected system</h3></div><div className="universe-status"><CircleDot size={15} />{nodes.length} nodes · {edges.length} edges</div></div>
      <div className="universe-body">
        <div className="universe-stage" role="region" aria-label="Supply-chain node and edge map">
          <div className="universe-stars" aria-hidden="true" />
          <div className="universe-core" aria-hidden="true"><Box size={24} /><span>1.55 oz<br />bar</span></div>
          <svg className="universe-edges" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Graph relationships">
            {edges.slice(0, 28).map((edge, index) => {
              const from = lookup.get(edge.source);
              const to = lookup.get(edge.target);
              if (!from || !to) return null;
              const midX = (from.x + to.x) / 2;
              const midY = (from.y + to.y) / 2;
              const active = edge.id === selectedEdgeId;
              return <g key={edge.id || index} className={active ? "is-active" : ""} onClick={() => setSelectedEdgeId(edge.id || "")} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelectedEdgeId(edge.id || ""); } }} role="button" tabIndex={0} aria-label={`Inspect ${edge.materialFlow || edge.flowType || "relationship"}`}><path d={`M ${from.x} ${from.y} Q ${midX} ${midY - 8} ${to.x} ${to.y}`} /><circle cx={midX} cy={midY - 4} r="1.55" /></g>;
            })}
          </svg>
          {nodes.map((node) => <button key={node.id} type="button" onClick={() => { setSelectedId(node.id || ""); setSelectedEdgeId(""); }} className={`universe-node ${node.id === selectedId ? "is-selected" : ""}`} style={{ left: `${node.x}%`, top: `${node.y}%`, "--node-color": node.color } as CSSProperties}><span className="universe-node-orb"><Orbit size={17} /></span><span>{node.label}</span></button>)}
        </div>
        <aside className="universe-inspector" aria-live="polite">
          {selectedEdge ? <><span className="universe-kicker">Selected connection</span><h4>{selectedEdge.materialFlow || selectedEdge.flowType || "Modeled relationship"}</h4><p>{selectedEdge.tooltipText || "This connection is sourced from the graph payload."}</p><dl><div><dt>State</dt><dd>{shortStatus(selectedEdge.relationshipStatus)}</dd></div><div><dt>Confidence</dt><dd>{selectedEdge.confidenceLevel || "not provided"}</dd></div></dl><button type="button" className="universe-clear" onClick={() => setSelectedEdgeId("")}>Return to node <ChevronRight size={15} /></button></> : selectedNode ? <><span className="universe-kicker">Selected node</span><h4>{selectedNode.label}</h4><p>{selectedNode.hoverSummary || selectedNode.description}</p><dl><div><dt>Relationship</dt><dd>{shortStatus(selectedNode.relationshipStatus)}</dd></div><div><dt>Confidence</dt><dd>{selectedNode.confidenceLevel || "not provided"}</dd></div><div><dt>Approved evidence</dt><dd>{selectedNode.enrichedApprovedEvidenceCount ?? 0} items</dd></div></dl><div className="universe-packets"><Network size={15} /><span>{selectedNode.enrichedEvidencePackets?.join(" · ") || "No packets listed"}</span></div></> : null}
        </aside>
      </div>
      <p className="universe-boundary">Node and edge state comes from the enriched public graph payload. Connections remain modeled unless the selected detail marks them as exact evidence.</p>
    </section>
  );
}
