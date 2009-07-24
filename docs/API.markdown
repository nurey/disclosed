# Disclosed.ca REST API Proposal

This document proposes a simple RESTful HTTP based API that exposes existing disclosed.ca data in to easy to use, mashable representations.

*Status:* DRAFT

## Resources

This list of resources is based on examining disclosed.ca's existing exposed data.

### Agencies

Each agency has a collection of contracts it has disclosed.

Fields:

- `name` - Name of the agency
- `contracts` - list of contract ID's associated with this agency.
- `num_contracts` - number of contracts associated with this agency
- `total_value` - total value of all contracts associated with this agency

### Contracts

Each contract has:

- `vendor_id` - an associated vendor
- `contract_id` - reference number
- `date`
- `description`
- `value` (in CAD $)
- `comments`

### Vendors

Each vendor has a collection of contracts they have won.

Fields:
- `name` - Name of the vendor
- `contracts` - list of contract ID's associated with this vendor.
- `num_contracts` - number of contracts associated with this vendor.
- `total_value` - total value of all contracts associated with this vendor.

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

Collections with large numbers of resources should consider a default limit for all collection requests, to avoid exposing the server to requests that are too large.  Such collections may also wish to enforce a hard limit on the number of items that can be returned.

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

## URI Layout

This section describes the URI map to bind URIs to collections and resources.  Unless otherwise noted, all paths are defined for GET requests only.

### Content Types

The API should allow requests of the Content-Type through both the HTTP `Accept` header and via a file extension.

- `.html` - `text/html` (also the default if no type is requested)
- `.txt`  - `text/plain` 
- `.json` - `application/json`

Accepting both formats strikes a good balance between API accessability and function.

### Notation

Variables in URI paths are denoted with a leading `:` such as `/vendors/:vid/`.  These denote this part of the path is a variable, to be replaced by the proper identifier for that resource.

This API should operate at some base URL, such as `/api` or `/data`.

### Basic resources and collections:

- `/agencies` - list of all agencies in the database
 - Filters: `name`
 - Orders: `name`, `num_contracts`, `total_value`
- `/agencies/:agency_id` - a specific database identified by the given ID (or optionally name)
- `/agencies/:agency_id/contracts` - a collection of contracts disclosed by the specified agency.
 - Filters and Orders: See `/contracts` below.
- `/contracts` - the list of all contracts in the database
 - Filters: `name`, `date`
 - Orders: `name`, `date`, `value`
- `/contracts/:contract_id` - a specific contract identified by the given ID
- `/vendors` - the list of all vendors in the database
 - Filters: `name`
 - Orders: `name`, `num_contracts`, `total_value`
- `/vendors/:vendor_id` - a specific vendor identified by the given ID (or optionally name)
- `/vendors/:vendor_id/contracts` - a collection of contracts awarded to the specified vendor.
 - Filters and Orders: See `/contracts` above.

### HTTP Response Codes

Because the API as specified is read-only, we need very few response codes.

- `200 OK` - everything is good on your GET request
- `404 NOT FOUND` - the resource you specified could not be found
- `407 NOT ACCEPTABLE` - the Accept type you specified is not supported

### Future Considerations

The following API elements are not considered for this initial API, but could be considered in future versions.

Social metadata could be added to disclosed.ca and exposed via the API.

These features could be implemented first by building a new REST API, and then improving the user interface to POST, PUT or DELETE to these resources.

- `GET :resource/tags` - retrieve the tags applied to the specified resource
- `PUT :resource/tags` - apply a tag to the specified resource
- `GET :resource/comments` - retrieve the comments attached to this resource
- `PUT :resource/comments` - add a comment about this resource
- `GET :resource/flags` - retrieve the number of times this resource has been flagged
- `PUT :resource/flags` - flag a resource (according to some socially defined standard of what flagging means)

Exposing other metadata about the resources collected by the system is useful as well to show popular content.

- `GET :collection?order=views;limit=10` - Top 10 most viewed resources of the given collection

Building social features implies user accounts and this moves the simple read-only REST API to a new level of complexity. For this reason these features are considered out of scope for this document.
