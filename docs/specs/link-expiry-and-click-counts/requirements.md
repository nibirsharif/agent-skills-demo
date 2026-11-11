# Requirements Specification: Link Expiry and Click Counts

**Version:** 1.2
**Date:** 2026-11-11
**Author:** Not given.
**Status:** Draft

## 1. Summary

Links expire, and owners see how many times each link was clicked. Owners see each link with its expiry date and click count in a table below the shortener prompt.

## 2. Scope

### In Scope

- Link expiry, set as a duration in days, with a default of 30 days
- Click counts for each link, counted for every redirection
- A table of links with expiry date and click count in the single page webapp

### Out of Scope

None given.

**Systems:** link shortener, single page webapp

## 3. Functional Requirements

FR-001: While a link has an expiry duration in days set by the owner of the link, when the hours equal to 24 times that number of days have elapsed since the creation of the link, the link shortener shall expire the link. <!-- Source: "Links should be able to expire"; answers to Q-002 and Q-008 -->

FR-002: While a link has no expiry duration set by the owner of the link, when 720 hours have elapsed since the creation of the link, the link shortener shall expire the link. <!-- Source: answers to Q-003 and Q-008 -->

FR-003: If a request is received for a link that has expired, then the link shortener shall return HTTP status 410 with the response body "resource is permanently deleted and will not return". <!-- Source: answers to Q-004 and Q-005 -->

FR-004: When a request for a link is redirected, the link shortener shall add 1 to the click count of that link. <!-- Source: "owners should see how many times each link was clicked"; answer to Q-007 -->

FR-005: When an owner opens the single page webapp, the single page webapp shall display each link of that owner, including each expired link, with the expiry date of the link in the time zone of the browser and the click count of the link in a table below the shortener prompt. <!-- Source: answers to Q-006, Q-010, and Q-011 -->

FR-006: If a link creation request sets an expiry duration that is not a positive whole number of days, then the link shortener shall reject the request and return HTTP status 400. <!-- Source: answer to Q-009 -->

FR-007: While a link has expired, the single page webapp shall display "Expired" for that link in the table. <!-- Source: answer to Q-011 -->

FR-008: If the single page webapp cannot retrieve the links of an owner, then the single page webapp shall display the error message "Could not load links". <!-- Source: answer to Q-012 -->

## 4. Non-Functional Requirements

None given.

## 5. Open Questions

Q-001: Closed. Which system expires links and counts clicks? Answer: link shortener. <!-- Source: "Links should be able to expire, and owners should see how many times each link was clicked." -->

Q-002: Closed. How does an owner set a link's expiry: a date and time with a time zone, or a duration after creation, and in which unit? Answer: a duration in days. <!-- Source: "Links should be able to expire" -->

Q-003: Closed. Must every link have an expiry, or only links whose owner sets one? Answer: yes, default to 30 days if not set. <!-- Source: "Links should be able to expire" -->

Q-004: Closed. Which HTTP status code is returned for a request to an expired link? Answer: 410. <!-- Source: "Links should be able to expire" -->

Q-005: Closed. What response body, if any, is returned for a request to an expired link? Answer: resource is permanently deleted and will not return. <!-- Source: "Links should be able to expire" -->

Q-006: Closed. Through which request or page does an owner see the click count of a link? Answer: single page webapp, the links with expiration date and count are shown in a table below the shortener prompt. <!-- Source: "owners should see how many times each link was clicked" -->

Q-007: Closed. What counts as one click: every request to the short link, or only requests that redirect to the destination URL? Answer: every redirection. <!-- Source: "owners should see how many times each link was clicked" -->

Q-008: Closed. Is one day of an expiry duration 24 hours? Answer: yes. <!-- Source: coverage gap in FR-001 -->

Q-009: Closed. What does the link shortener do when an owner sets an expiry duration that is not a positive whole number of days? Answer: reject the request with HTTP status 400. <!-- Source: coverage gap in FR-001 -->

Q-010: Closed. In which time zone does the single page webapp display the expiry date of a link? Answer: the browser's time zone. <!-- Source: coverage gap in FR-005 -->

Q-011: Closed. Does the single page webapp display an expired link and its click count in the table? Answer: yes, marked "Expired". <!-- Source: coverage gap in FR-005 -->

Q-012: Closed. What does the single page webapp display when it cannot retrieve the links of an owner? Answer: show an error message "Could not load links". <!-- Source: coverage gap in FR-005 -->

## 6. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-11 | Not given. | Initial draft: FR-001 to FR-005, Q-001 to Q-011; closed Q-001 to Q-007 |
| 1.1 | 2026-11-11 | Not given. | Added FR-006, FR-007; changed FR-001, FR-002, FR-005; closed Q-008 to Q-011; added Q-012 |
| 1.2 | 2026-11-11 | Not given. | Added FR-008; closed Q-012 |

## 7. References

None given.
