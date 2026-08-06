---
title: "002 - Geospatial Information Agents"
author:
  - name: "Carl Boettiger"
    orcid: "0000-0002-1642-628X"
    github: "cboettig"
    affiliations:
      - "University of California, Berkeley"
github_issue_number: 14
---

### Problem statement

**What does Jupyter geospatial look like in an era of coding agents?**

Coding agents are "coming for all of us" -- the landscape **is** changing. How does this impact geospatial practitioners and how can we maximize the benefits and minimize the harms of this change?

Frontier AI organizations are putting forth a vision where the underlying software is diminished/hidden and the interface we use is a chatbot, and we're all locked us in to those interfaces. This is a less open future.


### Who is impacted by this problem?

Everyone everywhere! In our community, geospatial practitioners, software engineers, students, instructors.

* End-user of geospatial / GIS tools: students & researchers. Just want to achieve a goal or complete a task, don't care too much about what tool they use as long as it works. <how that might be disrupted>.
* Developer community: open source & industry developer communities. <motivation>. <disruption>.
* Open geospatial and AI communities: JupyterAI, JupyterGIS, Pangeo are our friends and neighbors that are likely to be impacted by this problem. Want to help people break out of "proprietary prisons". <disruption>.

Jupyter as a platform is likely to be threatened by the emergence of new agentic geospatial platforms (Esri, Fused, Google Colab, ...) and generic agentic tools (Claude Code, ...).

TODO: Needs more fleshing-out. Seek voices of people in each of the above buckets to help define these.


### Proposed solution

We think the following values / practices are needed:

* Small models supported by strong software infrastructure that enables them to compete with frontier models for some (?) tasks
    * Engineering is needed to help these do geospatial well. Skills, tools, ???
* Interfaces that integrate with geospatial tools, e.g. JupyterGIS
* People need to be better able to produce geospatial data, not just consume it. _TODO: Does this belong here or not? Separate initiative?_ (this is what excites @cboettig about Jed's vision for source.coop -- you can be a producer for geospatial data, not just Amazon, Esri, etc.)
*

### Proposed implementation

TODO!!!

* Move [geo-agent](https://github.com/boettiger-lab/geo-agent) into GeoJupyter and build community scaffolding around it? (NOTE: it's not explicitly "jupyter")


### How will this fit in the ecosystem?

* Leverages JupyterAI interfaces and contributors to the development of those interfaces
* Integrates with JupyterGIS
* Containers -- safe places for agents to go wild. How can JupyterHub enable this?
* Safer agents (both financially and with respect to personal data / services)
* Collaboration!


### How do we identify the right time to do this? (Is it now?)

😱 AHHHHHHHHHHHHHHHH!!!


(TODO: Link to horror stories? 🙃)


### Who is doing / will do the work?

Fleshing this initiative out:

- @kpdavi
- @cboettig
- @mfisher87
- Who else wants to help?

Who's implementing stuff?

TODO -- are you inspired by any of these ideas? Comment below!


### Endorsements

- @cboettig


### Other information

#### Related things

* https://boettiger-lab.github.io/jupyter-geoagent

From @Mary-h86:

* https://github.com/makeabilitylab/altgeoviz
* MapStyle recommender: @Mary-h86 's idea where the user gives a prompt / explaining the intent and what they want to show and based on the data model and intent, the model recommends some styles
