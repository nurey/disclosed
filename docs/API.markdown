# Disclosed.ca REST API Proposal

This document proposes a simple RESTful HTTP based API that exposes existing
disclosed.ca data in to easy to use, mashable representations.

*Status:* DRAFT

## Notation

This API should operate at some base URL, such as `/api` or `/data`.

Variables in URI paths are denoted with a leading `:` such as `/vendors/:vid/`.  These denote this part of the path is a variable, to be replaced by the proper identifier for that resource.

## Representations

Every resource and collection should have these representations:

### `text/html`

This representation should only be simple HTML, easily embeddable inside other applications.

Other applications could apply formatting and style to the HTML, so no formatting should be displayed on this representation.

Collections of resources should typically be expressed via `<ul>` and `<li>` with links to the resource.

### `text/plain`

This representation offers the simplest interface, useful as a programmatic interface.

This interface might not include all the data about the resource, just a simple subset.  Collections should expose newline separated lists of resource identifiers.

### `application/json`

This representation is used by web applications and other programs to retrieve more structured data.

The JSON blob should include data about the resource, and optionally also include URI links to itself and related resources.  This allows programs to "follow" paths between resources.

### Optional Representations

Other representations may be useful as well for particular resources or collections, such as `text/csv`, `application/xml` (eg: RSS, ...)

## Resources

This list of resources is based on examining disclosed.ca's existing exposed data.

### Agencies

Each agency has a collection of contracts it has disclosed.

### Contracts

Each contract has:
- an associated vendor
- reference number (aka a contract ID)
- a date
- a description
- a value (in CAD $)
- comments

Contracts may optionally also have other data bits.

### Vendors

Each vendor has a collection of contracts they have won.

## Collections

Collections are available for each of the resources.

## Collection Options

### Filters

Filters can be used to restrict the collection to only those matching the criteria.  Each collection may choose to implement some of these common filters, or others:

- `?name=term` - Return only the resources that have a name that matches `term` as a wildcard search.
- `?after=date` - Return only the resources with a date after `date`.
- `?before=date` - Return only the resources with a date before `date`.

### Order

Collection order can be requested via the `order` request parameter.  Each collection may choose to implement some of these orders, or others:

- `?order=name`
- `?order=date`
- `?order=price`

### Limit

Any collection that will potentially have many resources should accept the `limit` request parameter.

- `?limit=5`

`limit` and `order` together can be very effective for clients to display the newest resources.

## URI layout

To come.
