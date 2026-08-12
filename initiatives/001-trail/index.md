---
title: "001 - GeoJupyter Trail"
author:
  - name: "Maryam Hosseini"
    orcid: "0000-0002-4088-810X"
    github: "Mary-h86"
    affiliations:
      - "University of California, Berkeley"
github_issue_number: 34
---

### Problem statement

Geospatial analysis does not happen in one place. The [2026 CARTO State of Spatial Analytics report](https://go.carto.com/report-state-of-spatial-analytics-2026-carto), based on responses from more than 200 professionals, finds that fewer than 20% of practitioners work within a single platform; the majority use between 3 and 8 tools. The field is split between powerful but complex tools and user-friendly but simplistic platforms, creating a gap where sophisticated, large-scale analysis requires deep technical expertise. The spatial stack is powerful but fragile: its value depends on whether tools can share data and stay coherent as data moves between them.

What the report describes as fragmentation has a structural cause: there is no persistent project layer that survives the move between tools. Each environment starts fresh. When a practitioner moves from data discovery to analysis to reporting, the decisions made at each step are not carried forward. They exist precariously in human memory, in undocumented notebooks, or not at all. Even careful, well-intentioned work is structurally difficult to reproduce, audit, or hand off.

### Who is impacted by this problem?

- Researchers who need to document provenance for publication, replication, or data management plans, and currently reconstruct it after the fact.
- Practitioners in public agencies, planning, and consulting who move between tools within the same project and need that context to stay coherent across deliverables.
- Students and educators whose multi-tool workflows need to be legible and reviewable at the end of a project.

### Proposed solution

GeoJupyter Trail is a project-scoped provenance record for workflows that move between notebooks and Jupyter-native geospatial tools. Running `trail init` creates a small `.geojupyter/` record and assigns the project a stable internal ID, independent of its directory or display name. Datasets are registered as project resources and receive stable resource UIDs. Trail then records provenance-relevant state transitions and interactions around those resources as work moves between tools.

The record is an append-only, human-readable event log. It can be version-controlled with the project, archived or submitted with a paper, and inspected without specialized software. Exports such as a citation list or data availability statement can then be assembled from the record rather than reconstructed from memory.

Trail does not coordinate tools or manage pipelines. Its purpose is narrower: preserve project and resource identity, durable state transitions, and provenance-relevant GUI interactions whose sequence and context are not otherwise preserved across tools.

The project record captures:

* **Context:** project title, research questions, spatial and temporal scope, and other project-level metadata.
* **Resources:** each registered dataset's stable UID, source, version, access date, license, citation, format, path, and lineage where known.
* **Events:** provenance-relevant state transitions and GUI interactions, with timestamps, tool context, linked resources where applicable, and small structured parameters.

For now, resource registration is explicit: a user registers a dataset once when it enters the project. This establishes the set of resources Trail is responsible for following. A Git-like distinction between tracked, untracked, and ignored files can keep this manageable as a project evolves: registered resources are tracked, newly created outputs can be surfaced as candidates for registration, and scratch paths can be excluded through `.trailignore`. A future data-acquisition tool such as JupyterDataConnect could perform registration automatically without changing Trail's identity model.

### Example

A practitioner initializes a Trail project, which assigns it a stable project ID, and registers an administrative-boundary dataset, which receives a stable resource UID. They read, filter, and transform it in a notebook. Those explicit computational steps already remain in the notebook, so Trail does not duplicate them.

If a cell overwrites a registered dataset, Trail reconciles that resource after execution and records the durable state change. The IPython execution event determines when Trail checks; Trail does not parse the cell to infer what happened.

The practitioner then opens the resource in JupyterGIS. Pan and zoom, feature inspection, layer changes, and other provenance-relevant GUI interactions can be observed through JupyterGIS's existing model-level signals and added to the same project record without modifying JupyterGIS itself. Trail observes the structured application state exposed by JupyterGIS rather than parsing raw Yjs transactions. Low-level pointer movement and other interaction telemetry are ignored.

Where a JupyterGIS source can be matched unambiguously to a registered Trail resource, the interaction can be linked to that resource UID. Where identity cannot be established, Trail records the interaction without inventing a dependency.

The resulting record connects durable resource states with the implicit interactions that would otherwise be difficult to recover when a workflow crosses tools.

Trail's internal format remains deliberately small, but the record can later be exported to a GeoJupyter-specific [RO-Crate](https://www.researchobject.org/ro-crate/) profile and aligned with [PROV-O](https://www.w3.org/TR/prov-o/) for interoperability with the broader research-data ecosystem.

### How Trail records without continuously watching

Trail follows a Git-like model: persistent identity and durable state are the foundation; continuous monitoring is not.

**Projects and resources establish identity.** `trail init` assigns a stable project ID. Each dataset registered with Trail receives a project-scoped resource UID. This resource registry gives Trail a bounded set of things to follow rather than requiring it to scan arbitrary project contents or infer which files matter.

**Notebook writes are detected through event-triggered reconciliation.** Trail installs as an IPython extension and uses existing lifecycle and execution hooks such as `post_run_cell` as reconciliation triggers. After a user-run cell, Trail compares the filesystem state of registered resources with their last recorded state. If a registered file was overwritten, replaced, or deleted, Trail records the new durable state.

The execution hook tells Trail **when to check**; it is not itself evidence that the cell caused the change. Trail does not parse the cell, duplicate explicit reads or transformations, or inspect notebook metadata to infer what the code meant.

**Explicit notebook operations are not duplicated.** Reading a dataset, filtering it, or applying a transformation in Python is already represented in notebook source and history. Trail is concerned with the parts of the workflow that are not otherwise preserved: durable resource transitions and implicit interactions across graphical tools.

**GUI interactions are observed through existing application signals.** JupyterGIS maintains interactive state through a Yjs-backed shared model and exposes model-level signals for changes to map options, layers, sources, selections, inspection state, and other application state. A Trail JupyterLab observer can subscribe to those signals from outside JupyterGIS. JupyterGIS does not need to import Trail or add Trail-specific calls.

Trail listens at this structured model layer rather than parsing Yjs itself. Yjs provides the underlying synchronized state; the JupyterGIS model provides the application-level event surface Trail needs.

**GUI activity is summarized as provenance, not telemetry.** Trail does not record every pointer movement, wheel event, or intermediate viewport update. Repeated pan and zoom changes can instead be coalesced into a settled map-view event. The goal is to preserve meaningful exploratory context, not a behavioral trace of every gesture.

**The record is append-only.** Every recorded state transition or interaction adds a new event with a unique identifier. Multiple notebooks or processes can therefore contribute without rewriting shared history.

**Lifecycle and consumption boundaries provide a correctness backstop.** Reconciliation can run when a session begins, after user-run cells, when a session ends, and before Trail presents or exports the record. A change made while no Trail process was active can therefore be discovered at the next reconciliation point.

A filesystem watcher may still be useful as an optional real-time layer, for example to update a live sidebar immediately. Correctness does not depend on one.

### Proposed implementation

Trail is a small Python package with a Jupyter integration and a planned CLI.

```python
from trail import TrailStore

trail = TrailStore.init("my_project")

resource_id = trail.add_resource(
    name="boundaries",
    source_url="https://portal.example/boundaries.tif",
    path="my_project/data/boundaries.tif",
    license="CC-BY-4.0",
)
```

The IPython extension can be loaded for notebook sessions or enabled globally through IPython configuration. Before registering any hooks, it checks whether the current working context belongs to a Trail project. Outside a Trail project it remains dormant.

The JupyterLab side follows the same principle. When a supported graphical application such as JupyterGIS is active within a Trail project, a Trail-side observer can attach to existing application signals and send small, allow-listed provenance events to the project record. The observed application does not need to take a dependency on Trail.

This separates the mechanisms cleanly:

* project and resource UIDs establish identity;
* IPython events provide reconciliation points for durable notebook writes;
* application-level signals expose implicit GUI activity;
* the Trail record connects those observations across the project.

### How will this fit in the ecosystem?

Trail is infrastructure rather than another analysis environment. It integrates through Jupyter's existing extension, execution, and application event surfaces instead of requiring every geospatial tool to implement a Trail-specific API.

This keeps adoption non-invasive. Notebook support comes from IPython execution and lifecycle hooks. GUI support can use structured model or command signals already exposed by Jupyter-native applications. Where an application does not expose enough semantic state, Trail can record only what can be established reliably rather than inferring an operation from internal data structures.

The resulting record remains plain, portable project data. Export to RO-Crate and PROV-O can provide interoperability outside GeoJupyter without forcing those standards into Trail's day-to-day representation.

### Is the timing right?

JupyterGIS and other GeoJupyter components are establishing their interaction and state-management models now. This is a useful moment to define a shared project-level provenance layer while those event surfaces remain visible and extensible, rather than asking each tool to invent an independent history mechanism later.

There is also external pressure for reproducible methods, data availability statements, and documented provenance. Trail makes that documentation a byproduct of working across Jupyter tools rather than a separate reconstruction exercise at submission time.

### Open questions

**Q1.** Which GUI state transitions are provenance-relevant enough to record by default? Map exploration, feature inspection, layer changes, and exports are plausible candidates; pointer movement and other interaction telemetry are not.

**Q2.** Are JupyterGIS's existing model-level signals sufficiently stable as an external event surface for Trail to depend on, or should GeoJupyter define a small, stable semantic event interface for provenance consumers?

**Q3.** How should Trail handle newly created outputs without a resource UID? A Git-like tracked/untracked/ignored model could surface new outputs as registration candidates without silently treating scratch files and caches as provenance. What remains open is whether outputs that can be linked unambiguously to a registered resource should acquire identity automatically or remain one explicit registration step away.

**Q4.** How should Trail associate graphical activity with registered resources? When a JupyterGIS source can be resolved to a path or identity already present in the Trail resource registry, the relationship can be recorded directly. When no unambiguous match exists, should the event remain project-level rather than infer lineage?

**Q5.** How should Trail handle resources that are accessed remotely and never materialized as local files? What identity and state evidence is sufficient for reproducibility without downloading the full dataset?

**Q6.** Should Trail include a JupyterLab sidebar for inspecting, annotating, and navigating the project record? A live interface may justify an optional real-time layer even though correctness does not require one.

**Q7.** How should the browser-side observer and project record behave in multi-user or remote-kernel deployments, where the Jupyter frontend, server, kernel, and project filesystem may not share the same process or host?

### Who is doing / will do the work?

*No response*

### Endorsements

* @mfisher87
* @sampottinger

### References

* CARTO. (2026). *State of Spatial Analytics 2026*. https://go.carto.com/report-state-of-spatial-analytics-2026-carto
* Sefton, P., Soiland-Reyes, S., et al. (2024). *RO-Crate 1.2: A lightweight approach to packaging research data with metadata*. https://www.researchobject.org/ro-crate/specification/1.2/
* Lebo, T., Sahoo, S., McGuinness, D., et al. (2013). *PROV-O: The PROV Ontology*. W3C Recommendation. https://www.w3.org/TR/prov-o/
* Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. https://doi.org/10.1038/sdata.2016.18
