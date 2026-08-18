---
title: "003 - Better geospatial primitives for Python"
author:
  - name: "Jessica Scheick"
    orcid: "0000-0002-3421-4459"
    github: "JessicaS11"
    affiliations:
      - "University of New Hampshire"
github_issue_number: 18
---

### Problem statement

Geospatial Python library authors and users struggle with defining and using interfaces for communicating geospatial regions that are conventional, unambiguous, and safe from human error.

As a result

* library development is more frustrating and more burdensome (developing new conventions)
* library use is more frustrating because...
    * users have to create non-interoperable data structures
    * users (even experienced ones) often pass incorrect data because they don't have enough information about the library's expectations


<details>
<summary>Extra explanations</summary>

Unconventional:

* Individual APIs (e.g. NASA CMR, NASA Harmony, ...?) often require subtle differences in how this spatial information is submitted; as a result, many libraries include their own set of utilities for reformatting and manipulating basic spatial information
* \>=3 competing standards for representing these primitives: Shapely, Fiona, GeoPandas

Ambiguous:

* ROIs often represented as a bounding box submitted as a `list`/`tuple` of floats in a conventional order, often `(x_min, y_min, x_max, y_max)`
* Handling of ROIs that cross the antimeridian is inconsistent at best, and there is no easy way for users to make this property explicit.
* Many tools and APIs do not provide good options for working in polar regions/with polar projections, instead requiring the use of georectangular bounding boxes.
  Users may not have a good mental model for the implications of reprojecting those bounding boxes and don't have the tools to unambiguously represent the region they intend to.

Error-prone:

* Representing an ROI that crosses the antimeridian, because there's no explicit interface for this, often yields unexpected results
* It is easy to make mistakes in manually arranging values where order is important (e.g. `(x_min, y_min, x_max, y_max)` for a bounding box

</details>


### Who is impacted by this problem?

Any persona running geospatial analyses, but especially those who might be working across educational tools (e.g. in Jupyter Notebooks) up through scaling workflows (PIs/researchers) and thus need flexibility for inputting geospatial objects across multiple APIs would be impacted.
Multiple researchers who work with satellite data in polar regions have expressed interest and support for exploring this idea.


### Proposed solution

* Explore creation of a lightweight (keeping in mind installation challenges associated with gdal, GMT, etc.), generalized tool that can leverage existing geospatial tools (such as Fiona, Shapely, odc-geo, antimeridian) to create, validate, and track a single "geospatial" object (i.e. ROI, or "coverage") and output that object in multiple formats.
  Formats may be specified by the user or backend developer, much as `datetime` creates a valid, timezone aware object and can be used to provide components of dates and/or times.
* Enrich the interface of another existing library (Shapely, Fiona, ??) to meet the same needs.
* Do nothing -- this problem has existed for a long time and perhaps doesn't need to be solved.


### Proposed implementation

Our current thinking is that this would likely require the creation of a new package, given the specialized nature of most existing libraries and desire to broaden support for polar regions.

A broad conceptual framework for how this could be implemented is inspired by the [icepyx.Spatial module](https://github.com/icesat2py/icepyx/blob/development/icepyx/core/spatial.py), which was developed specifically for querying ICESat-2 data in NASA's CMR API but has the general pipeline for (1) interpreting and validating the user's input, (2) storing that input in a consistent way for the rest of the software to leverage, and (3) providing options to format the information for input to specific external APIs.


### How will this fit in the ecosystem?

This proposal fits into the ecosystem as a high level solution to address common pain points and sources of error.
Ultimately, developers can deprecate, contributing upstream as appropriate, their own one-off utilities that were designed to address these challenges on a per-package basis.


#### Current gaps

* Shapely: Has geometry types.
  They represent geometry only -- CRS-naive (analogy: naive datetimes).
  A SRID (but not full CRS definition) can be attached, but there's no checking, conversion, or units attached to it.
  Calling any sort of operation on the geometry in shapely is going to default to the geometry units.
  Changing the SRID does not change the geometry.
* Fiona: Has geometry types.
  They are richer than shapely geometries, but still CRS-naive.
  Fiona's collection types are CRS-aware, but the primitives are not.
* Geopandas: CRS-aware, but it's a collection object, not a primitive.
  It would be unreasonable to ask a user to pass in a GeoDataFrame to represent a single bbox, for example.
* Spherely: Useful for polar coordinate use cases.
  Early development, single author-owner.
  Limited as an implementation of s2geometry.
  TODO: More
* ?


### How do we identify the right time to do this? (Is it now?)

As tools and datasets continue to proliferate, having standard ways of interacting with this crucial information is important.
Now is a good time to consider this.

Conversely, this problem has existed for a long time and we've been getting along "fine" with these sources of friction.


### Who is doing / will do the work?

Individuals who have expressed an interest in contributing to this effort include @gh:mfisher87 (geojupyter lead), @gh:espg (polar use case), @gh:jessicas11 (use case)


### Endorsements

In addition to the folks listed in the previous cell, these individuals have expressed interest in supporting this initiative @gh:thomasteisberg, @gh:yueyiche (polar use case) @gh:elliesch


### Other information

#### Motivation / background

Most geospatial workflows begin with declaration of some region of interest (ROI).
When input manually this is often done as a bounding box submitted as a `list`/`tuple` of floats (often `(x_min, y_min, x_max, y_max)`).
Points or polygons submitted as `list`s or `tuple`s of lat-lon pairs or external files (e.g. shapefiles or geojson) are also commonly used.
This ROI is then passed to various APIs to search for, obtain (order/download/stream), subset, plot, etc. data.
Multiple challenges arise with this paradigm:


<details>
<summary>Examples</summary>

A theoretical example for obtaining an ICESat-2 data product (ATL03) via multiple tools:
```
bbox = [ll_lon, ll_lat, ur_lon, ur_lat]

# Using the same bbox in 3 different ways to satisfy requirements of libraries
icepyx.Query(spatial=bbox)
earthaccess.Search(bbox=tuple(bbox)]
SlideRule.get_atl03(parms={"poly": sliderule.toregion(bbox)})
```

...the last of which relies on a custom function within/maintained by SlideRule I only learned about after working with the library for years; previously I was manually creating the spatial extent as:

```
sr_extent = [
        {
            "lon": bbox[0],
            "lat": bbox[1]
        },
        {
            "lon": bbox[2],
            "lat": bbox[1]
        },
        {
            "lon": bbox[2],
            "lat": bbox[3]
        },
        {
            "lon": bbox[0],
            "lat": bbox[3]
        },
        {
            "lon": bbox[0],
            "lat": bbox[1]
        }
    ]
```

...and perpetually hoping I didn't make any mistakes and got the right elements of bbox into the right spots to create a polygon of the bbox.

</details>


#### Use case examples (thanks @gh:espg)

To make a more explicit example-- if you have something in polar stereographic coordinates, you can calculate a a bounding box in polar stereographic that has two coordinates.
If you project into lat/lon, and calculate the two-coordinate bounding box, you'll have a geometry that covers a different area on the earth.
(Technically, even if you did use 4-coordinates, you'll still have different areas due to curvature of the lines to the vertices-- but it'll be much closer).

Having a 'coverage type' gets more appealing when we try to mix and match datasets that are defined in different types.
I should be able to combine three different coverages, and get a merged coverage that I can cast to new merged bounding space, and it shouldn't matter if they're defined in different projections or if the geometries are stored in different ways.


#### Datetime analogy (thanks @gh:espg)

A datetime object isn't just 'a time' -- it's the time.
Regardless of whether you default to UTC or a local time, the referencing is unambiguous, and the object doesn't exist unless that's been made explicit.
A shapely polygon that's holding lat/lon coords or Polar Stereographic coords is valid without the referencing information, which means it's **ambiguous by default**.
A coverage would require crs and associated unit information.
This would similarly mean that the object wouldn't be 'a spatial coverage', but the spatial coverage for items that are geospatial data.
My thinking here is that a coverage object would basically be the metadata and operations attached to any geometries that enforced typing and spatial referencing like geojson or Extended Well-Known Text/Binary.


### Open questions

* Is a "feature" type that includes properties (e.g. temperature, flow rate, area, name), not just geometry, in scope?
    * Matt: IMO, this is important. But probably should come later.
* Are there lower-level components that represent a gap in the ecosystem that should be developed first?
