# Implementation Tasks: Link Expiry and Click Counts

**Version:** 1.0
**Date:** 2026-11-11
**Plan:** plan.md, version 1.0

## 1. Overview

The tasks build on the `shortener` package: store changes first in `shortener/storage.py`, then the endpoints in `shortener/server.py`, each with its tests in `tests/`. Phase 2 follows Phase 1 and adds the web page, the only new non-test files.

| Phase | Tasks | Requirements |
|-------|-------|--------------|
| 1 | T-1.1 to T-1.7 | FR-001, FR-002, FR-003, FR-004, FR-006 |
| 2 | T-2.1 to T-2.7 | FR-005, FR-007, FR-008 |

## 2. Tasks

### Phase 1: Link expiry and click counting in the API

#### T-1.1: Store an expiry on each link

**Covers:** FR-001, FR-002

**Files:** `shortener/storage.py`, `tests/test_storage.py`

**Depends on:** None.

**Done when:** FR-001: storage test that a link created with 3 days has an expiry exactly 72 hours after creation; FR-002: storage test that a link created with no duration has an expiry exactly 720 hours after creation

**Status:** Done

#### T-1.2: Accept an expiry duration when creating a link

**Covers:** FR-001, FR-002

**Files:** `shortener/server.py`, `tests/test_server.py`

**Depends on:** T-1.1

**Done when:** FR-001: server test that `POST /links` with `expires_in_days` 3 stores a link that expires 72 hours after creation; FR-002: server test that `POST /links` without it stores a link that expires 720 hours after creation

**Status:** Done

#### T-1.3: Reject an invalid expiry duration

**Covers:** FR-006

**Files:** `shortener/server.py`, `tests/test_server.py`

**Depends on:** T-1.2

**Done when:** FR-006: server test that `expires_in_days` values 0, -1, 1.5, and "x" each return 400 and create no link

**Status:** Done

#### T-1.4: Return 410 for an expired link

**Covers:** FR-001, FR-003

**Files:** `shortener/server.py`, `tests/test_server.py`

**Depends on:** T-1.1

**Done when:** FR-001: server test that a link whose expiry instant has passed is no longer redirected; FR-003: server test that a request for it returns status 410 with the body `resource is permanently deleted and will not return`

**Status:** Done

#### T-1.5: Store a click count on each link

**Covers:** FR-004

**Files:** `shortener/storage.py`, `tests/test_storage.py`

**Depends on:** None.

**Done when:** FR-004: storage test that a new link has a click count of 0 and two calls of the increment method make it 2

**Status:** Done

#### T-1.6: Count each redirection

**Covers:** FR-004

**Files:** `shortener/server.py`, `tests/test_server.py`

**Depends on:** T-1.4, T-1.5

**Done when:** FR-004: server test that two redirects raise the click count from 0 to 2, and that a 410 response and a 404 response leave it unchanged

**Status:** Done

#### T-1.7: Verify the phase

**Covers:** FR-001, FR-002, FR-003, FR-004, FR-006

**Files:** None.

**Depends on:** T-1.3, T-1.4, T-1.6

**Done when:** FR-001: T-1.1 and T-1.2 tests pass; FR-002: T-1.1 and T-1.2 tests pass; FR-003: T-1.4 test passes; FR-004: T-1.5 and T-1.6 tests pass; FR-006: T-1.3 test passes; `python3 -m unittest` is green

**Status:** Done

### Phase 2: Single page webapp table of links

#### T-2.1: List the links of one owner in the store

**Covers:** FR-005

**Files:** `shortener/storage.py`, `tests/test_storage.py`

**Depends on:** T-1.1, T-1.5

**Done when:** FR-005: storage test that the new method returns only the given owner's links, expired ones included, each with code, URL, expiry, and click count

**Status:** Done

#### T-2.2: Add the endpoint that lists an owner's links

**Covers:** FR-005, FR-007

**Files:** `shortener/server.py`, `tests/test_server.py`

**Depends on:** T-2.1

**Done when:** FR-005: server test that `GET /links` with `X-User: alice` returns only alice's links with expiry and click count; FR-007: server test that an expired link has its expired flag set and an unexpired link does not

**Status:** Done

#### T-2.3: Serve the page with the shortener prompt and the table

**Covers:** FR-005

**Files:** `shortener/server.py`, new: `shortener/static/index.html` page with the link-creation prompt and a table of links, `tests/test_server.py`

**Depends on:** T-2.2

**Done when:** FR-005: server test that `GET /` returns 200 HTML; run `python3 -m shortener`, open `/` in a browser, and see the table below the prompt with each link's expiry date in the browser's time zone and its click count

**Status:** Done

#### T-2.4: Show "Expired" for an expired link in the table

**Covers:** FR-007

**Files:** `shortener/static/index.html`

**Depends on:** T-2.3

**Done when:** FR-007: in the browser, a link past its expiry shows "Expired" in the table and an unexpired link does not

**Status:** Done

#### T-2.5: Show the error message when the links cannot be loaded

**Covers:** FR-008

**Files:** `shortener/static/index.html`

**Depends on:** T-2.3

**Done when:** FR-008: in the browser, with the server stopped or `GET /links` failing, reloading the page shows "Could not load links"

**Status:** Done

#### T-2.6: Document the page address in the README

**Covers:** FR-005

**Files:** `README.md`

**Depends on:** T-2.3

**Done when:** FR-005: README names the address of the page, and opening that address after `python3 -m shortener` shows the table

**Status:** Done

#### T-2.7: Verify the phase

**Covers:** FR-005, FR-007, FR-008

**Files:** None.

**Depends on:** T-2.4, T-2.5, T-2.6

**Done when:** FR-005: T-2.2 and T-2.3 tests pass and the browser check of T-2.3 shows the table below the prompt in the browser's time zone; FR-007: T-2.2 test passes and the browser check of T-2.4 shows "Expired"; FR-008: the browser check of T-2.5 shows "Could not load links"; `python3 -m unittest` is green

**Status:** Done

## 3. Blocked Requirements

None.

## 4. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-11-11 | Initial tasks from plan.md 1.0 |
