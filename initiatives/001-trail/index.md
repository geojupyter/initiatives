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

Geospatial analysis does not happen in one place. The [2026 CARTO State of Spatial Analytics report](https://go.carto.com/report-state-of-spatial-analytics-2026-carto), based on responses from more than 200 professionals, finds that fewer than 20% of practitioners work within a single platform, the majority use between 3 and 8 tools, likely higher. The field is split between powerful but complex tools and user-friendly but simplistic platforms, creating a gap where sophisticated, large-scale analysis requires deep technical expertise. The spatial stack is powerful but fragile, its value depends on whether tools can share data and stay coherent as data moves between them.

What the report describes as fragmentation has a structural cause: there is no persistent project layer that survives the move between tools. Each environment starts fresh. When a practitioner moves from data discovery to analysis to reporting, the decisions made at each step are not carried forward. They exist precariously in human memory, in undocumented notebooks, or not at all. Even careful, well-intentioned work is structurally difficult to reproduce, audit, or hand off.

### Who is impacted by this problem?

- Researchers who need to document provenance for publication, replication, or data management plans, and currently reconstruct it after the fact.
- Practitioners in public agencies, planning, and consulting who move between tools within the same project and need that context to stay coherent across deliverables.
- Students and educators whose multi-tool workflows need to be legible and reviewable at the end of a project.

### Proposed solution

GeoJupyter Trail is a shared project record: a structured, human-readable file stored at `.geojupyter/trail.json`, that GeoJupyter-compatible tools can read and write as the user works.

The user defines a project once.

Trail accumulates the rest: what the project is trying to answer, what its spatial and temporal scope is, what data sources were brought in, and what happened to them as they moved through the workflow.

It version-controls naturally alongside the project, can be archived or submitted with a paper, and is human readable.

Trail does not coordinate tools or manage pipelines.

Trail does not interoperate with tools outside the Jupyter ecosystem, like QGIS.

The project record captures:

- **Context:** title, research questions, keywords, topics, spatial extent (bounding box, CRS), time frame.
- **Resources:** for each dataset: name, source, version, access date, license, citation, format, and how it entered the workflow.
- **Events:** a sequential log of tool actions, each with a timestamp, tool name, action type, linked resource, and relevant parameters.

Example:

> A practitioner opens a boundary file from a federal data portal through JupyterDataConnect. JupyterDataConnect records the source, checksum, version, license, and access date in the Trailfile. They load it as a layer in JupyterGIS, apply a spatial filter, and reproject. JupyterGIS records the CRS, bounding box, and filter expression in the Trailfile. When they later build a report in Jupyter Book, those records surface automatically as a data availability statement and citation list, without re-entry.

To make it easier, we can have Trail's schema as a domain-specific profile of [RO-Crate](https://www.researchobject.org/ro-crate/), a well-known standard for packaging research data with metadata, and its event log is aligned with [PROV-O](https://www.w3.org/TR/prov-o/), the W3C vocabulary for provenance. Because Trail uses RO-Crate, the project record works anywhere RO-Crate does: Zenodo, data management plans, any tool that already reads it.

### Proposed implementation

Trail is a software package, possibly with a CLI.

`Trail.init()` creates a Trailfile at the expected location, and prompts the user for required information (similar to `myst init`).

`Trail.load()` reads an existing Trailfile and makes it available to any participating tool in the session.

Tools automatically discover a Trailfile by directory traversal in the same manner as Git.

Tools do not ask the user to register things. Registration is triggered by tool actions. When a user brings a dataset into the project through JupyterDataConnect (a companion initiative that connects FAIR-compatible data discovery platforms to notebooks), Trail writes the resource entry automatically. When the user opens that resource in JupyterGIS, Trail logs the transition: which layer contains the data, what parameters, what CRS. The Trailfile grows as the work happens, not as an afterthought.

The user-facing API:

```python
trail = Trail.init("my_project") # once, to start a project
# or, to resume:
# trail = Trail.load("./my_project")

trail.export_citations() # show all data citations for writeups, Jupyter Book
trail.export_methods_summary() # summarize methods (e.g. parse Notebook JSON to extract exact analysis steps,
 # like "data cleaning", optionally using an LLM to summarize/categorize)
 # for writeups, Jupyter Book
trail.visualize() # Show a graph representation of how the user navigated through their toolkit
```

The API that tools write against:

```python
trail.add_resource(
    name,
    source_url,
    version,
    license,
    citation,
    format,
    entry_point
)

trail.log_event(
    tool,
    action,
    resource_id,
    parameters
)
```

These two methods are called by tools, not users (not sure -- should users be able to write their own records if they need it?). The record builds as you work. If users had to call `add_resource()` manually every time, it would become documentation overhead and people would stop doing it.

Tool switching is implicit in the data structure -- when a record by the "JupyterGIS" tool follows a record by the "JupyterDataConnect" tool, we know they switched tools.

### How will this fit in the ecosystem?

Trail is infrastructure. It does not compete with any existing GeoJupyter tool. It gives them a shared surface to write to. Each tool remains self-contained. Trail integration is opt-in and incremental: a tool that writes to Trail becomes more useful without breaking anything for tools that do not yet participate.

The main value of GeoJupyter Trail is in integrations with tools (GUI or non-GUI) in the Jupyter ecosystem. Teaching these tools to speak Trail language is critical to enabling users to successfully use this tool.

Because Trail is a GeoJupyter-specific [profile](https://www.researchobject.org/ro-crate/profiles) of RO-Crate, it inherits interoperability with the broader open science stack without requiring that stack to know anything about GeoJupyter. A Trailfile can travel with a dataset to Zenodo, appear in a data management plan, or be processed by any RO-Crate-aware tool, as plain JSON that any researcher can inspect directly.

### Is the timing right?

JupyterGIS is gradually taking shape. This is the moment to introduce a shared project layer, before each tool independently builds its own state management in ways that make a shared layer structurally harder to add later.

There is also external pressure. Research funders and journals increasingly require workflow documentation, data availability statements, and reproducible methods. Trail makes it possible to satisfy those requirements as a natural byproduct of doing the work, rather than a separate documentation task that happens incompletely, at submission time.

The cost of establishing Trail now is low.

### Open questions

**Q1.** Should Trail define a minimal required schema, like: title, extent, at least one resource, that all tools must write before marking a project as Trail-compatible? Or should conformance be entirely opt-in with no required fields?

**Q2.** How should Trail handle datasets that are too large to download locally and are accessed entirely in the cloud? Is recording the access URL and parameters sufficient for reproducibility, or does Trail need to snapshot query results? Or record a checksum (which requires downloading the entire data file)?

**Q3.** RO-Crate profiles require community agreement on what fields are mandatory and what vocabularies are used. Is there appetite within GeoJupyter to maintain a formal Trail profile, or should Trail remain a looser convention with RO-Crate as inspiration rather than a strict parent?

**Q4.** Should Trail include a JupyterLab extension that shows the project record as a live sidebar letting users visually inspect, annotate, and navigate workflow history without leaving the notebook environment? (I personally would like to have this feature but can be something that we can investigate more with potential users)

**Q5.** One thing I am not yet clear about is the the right contract between Trail and a participating tool. Trail records tool events, but tools vary in how they expose their internal state, say a Python callback, a file-based protocol, a JupyterLab signal.

**Q6.** How should Trail operate -- as a service that tools communicate with, or fully integrated within tools?

### Who is doing / will do the work?

_No response_

### Endorsements

* @mfisher87
* @sampottinger

### References

- CARTO. (2026). *State of Spatial Analytics 2026*. https://carto.com/resources/reports/spatial-data-science
- Sefton, P., Soiland-Reyes, S., et al. (2024). *RO-Crate 1.2: A lightweight approach to packaging research data with metadata*. https://www.researchobject.org/ro-crate/specification/1.2/
- Lebo, T., Sahoo, S., McGuinness, D., et al. (2013). *PROV-O: The PROV Ontology*. W3C Recommendation. https://www.w3.org/TR/prov-o/
- Wilkinson, M. D., et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. https://doi.org/10.1038/sdata.2016.18
