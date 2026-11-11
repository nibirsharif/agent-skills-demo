# Implementation Plan: Link Expiry and Click Counts

**Version:** 1.0
**Date:** 2026-11-11
**Requirements:** requirements.md, version 1.2
**Status:** Draft

## 1. Approach

Extend the existing `shortener` package, which has a SQLite `LinkStore` (`shortener/storage.py`) and a standard-library HTTP handler (`shortener/server.py`). Phase 1 adds expiry and click counting to the store and to the create and redirect endpoints, so the behaviour is testable through the API alone. Phase 2 adds the owner's table of links in a single page webapp; the repository has no web page yet, so that phase adds one, served by the same server.

| Phase | Delivers | Requirements |
|-------|----------|--------------|
| 1 | Link expiry and click counting in the API | FR-001, FR-002, FR-003, FR-004, FR-006 |
| 2 | Single page webapp table of links | FR-005, FR-007, FR-008 |

## 2. Phases

### Phase 1: Link expiry and click counting in the API

**Scope:** Store an expiry and a click count for each link, set the expiry at creation (owner-set duration in days, else 30 days), reject an invalid duration, return 410 for an expired link, and count each redirection. Listing links and the webapp are left for Phase 2.

**Requirements:** FR-001, FR-002, FR-003, FR-004, FR-006

**Size:** about 5 files

**Reuse:**

- `shortener/storage.py`: `LinkStore` and its `links` table, extended with the expiry and click count
- `shortener/server.py`: `do_POST` (validation and 400 responses) and `do_GET` (redirect)
- `tests/test_server.py`: the `ServerTest` helpers `request` and `create`
- `tests/test_storage.py`: the `LinkStoreTest` pattern

**Interface and data changes:**

- `links` table gains `expires_at` and `click_count` columns; `LinkStore.__init__` adds them to a database file that already has the table
- `POST /links` accepts an optional body field for the expiry duration in days (planned name: `expires_in_days`); a value that is not a positive whole number returns 400
- `LinkStore.create` takes the duration in days and stores `created_at` plus 24 hours per day, or 30 days (720 hours) when none is given
- `LinkStore.get` returns the expiry and click count; a new `LinkStore` method adds 1 to the click count
- `GET /<code>` returns 410 with the body `resource is permanently deleted and will not return` for an expired link, and adds 1 to the click count only when it returns the redirect

**Verify:**

- FR-001: storage test that a link created with 3 days has an expiry of exactly 72 hours after creation, and a test that a request after that instant returns 410
- FR-002: storage test that a link created with no duration has an expiry of exactly 720 hours after creation
- FR-003: server test that a request for an expired link returns status 410 and the exact body text
- FR-004: server test that two redirects raise the click count from 0 to 2, and that a 410 or 404 response does not change it
- FR-006: server test that durations 0, -1, 1.5, and "x" each return 400 and create no link

**Open questions:** None.

### Phase 2: Single page webapp table of links

**Scope:** Let an owner list their links with expiry date and click count, and show them in a table below the shortener prompt in a page served by the server. The repository has no page yet, so this phase adds a minimal page whose link-creation form is the shortener prompt. It builds on the expiry and click count from Phase 1.

**Requirements:** FR-005, FR-007, FR-008

**Size:** about 6 files

**Reuse:**

- `shortener/server.py`: `Handler`, `_send_json`, and the `X-User` owner check in `do_POST`
- `shortener/storage.py`: the `links` table and `LinkStore.get`, for the new list method
- `tests/test_server.py`: `ServerTest` helpers `request` and `create`

**Interface and data changes:**

- `LinkStore` method that returns the links of one owner with code, URL, expiry, and click count, expired links included
- `GET /links` with the `X-User` header returns that owner's links as JSON, each with an expired flag; it is matched before the `GET /<code>` route
- `GET /` serves the new page from a static file in the `shortener` package
- the page shows the shortener prompt, a table below it with the expiry date in the browser's time zone, the click count, and "Expired" for an expired link, and the text "Could not load links" when the list request fails
- README gains the page address

**Verify:**

- FR-005: server test that `GET /links` returns only the requesting owner's links, expired ones included, with expiry and click count; run `python3 -m shortener`, open `/` in a browser, and check the table sits below the prompt and the expiry date matches the browser's time zone
- FR-007: server test that an expired link has its expired flag set; in the browser, check that the row shows "Expired"
- FR-008: in the browser, stop the server or make `GET /links` fail, reload the page, and check that "Could not load links" appears

**Open questions:** None.

## 3. Blocked Requirements

None.

## 4. Open Questions

None.

## 5. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-11-11 | Initial plan from requirements.md 1.2 |
