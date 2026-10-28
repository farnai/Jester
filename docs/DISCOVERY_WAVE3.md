# Wave 3: bounded discovery and social profiles

This describes implemented local behavior. The larger Discovery Preferences & Feed Engine V1 remains a separate specification: ranking, intent partitioning, behavioral telemetry and photo eligibility gates are not implemented here.

## API

`GET /v1/discovery/people` requires bearer authentication; the viewer is its JWT subject.

| Parameter | Contract |
| --- | --- |
| `limit` | Default 12; integer 1–24 |
| `after` | Exclusive UUID cursor from `next_cursor` |
| `q` | Trimmed, case-insensitive literal display-name substring, maximum 80 characters |
| `city_id` | Exact canonical current-city UUID; never birth location |
| `shared_only` | At least one mutually declared active interest in an active category |

Response: `{items: DiscoveryPerson[], next_cursor: UUID | null}`. Ordering is ascending immutable profile UUID, not ranking. The cursor is the last returned UUID when another page exists. This is not a snapshot: eligibility changes apply to subsequent requests; newly inserted lower UUIDs appear after restarting. Names and biographies are never deduplication keys.

Items contain safe identity, ordered Wave 2 photo metadata, active interests, `common_interest_ids`, `same_city`, canonical `connection_id` and `connection_state` (`none`, `pending_out`, `pending_in`, `accepted`). Safe astrology and an optional corpus presence observation come only from fresh stored ascendant/Sun signals. Missing/stale signals yield no invented sign or hook. `compatibility_score` is always `null`; the existing authorized profile preview still supplies on-demand Synastry.

`GET /v1/interpretations/discovery-people` retains its list response and viewer-impersonation rejection, accepts the same pagination/filter parameters, and delegates to the bounded service. Clients needing `next_cursor` use the new endpoint. The legacy route no longer calculates per-candidate Synastry.

## Privacy and performance

SQL excludes self, non-discoverable profiles and blocking in both directions before pagination. A nonempty page uses three batched SELECTs: bounded candidate rows, photo metadata and interests. There is no per-person query, chart recalculation or compatibility computation. Database filtering may scan rows; this is not a constant-time claim. Migration `030_discovery_pagination.sql` adds partial UUID and city/UUID indexes without changing data, columns, grants or RLS. Plan write-lock tolerance before applying ordinary index creation to a large deployment; the checked local database is small.

No private birth payload or `astro_private` is selected for serialization. Birth-data version is consulted only to reject stale stored safe signals. Exact coordinates and birth details never enter the DTO.

Wave 2's authenticated photo proxy accepts `?size=card`, using the same private authorization and storage path. Output is WebP bounded to 720×900 with `Cache-Control: private, no-store`. Default full-size behavior is unchanged. Each card request currently reads/decodes the original; persistent thumbnails are not implemented. Legacy public avatars retain their existing boundary.

The deck mounts only the current selected photo and the next person's primary photo. Promotion preserves the preloaded component. Unmount/account changes abort downloads and revoke blob URLs. The full Person gallery retains Wave 2 thumbnail behavior.

## UI

- Left swipe, focused ArrowLeft or Next advances locally, with no dislike/rejection/match/telemetry write.
- Right swipe, focused ArrowRight or Connect opens a modal. Only explicit Send creates the canonical request; Escape/cancel sends nothing.
- Horizontal displacement must exceed 65px and dominate vertical displacement. Native vertical touch scrolling cancels navigation. Reduced motion removes drag translation/transition. Photo taps and separate buttons switch photos.
- URL state preserves filters, view and active person through profile navigation. Cached pages support return; direct return links fetch bounded pages as needed. Discovery refreshes periodically and on mount/focus. Already viewed pixels cannot be retroactively revoked.
- Desktop presents filters, center photo card and social context. A browsable list avoids candidate photo downloads.
- Shared connection controls reflect outgoing pending, incoming accept/decline and accepted conversation/Why. No Likes or Matches model is added.
- Person Profile orders identity, biography, interests, connection, brief allowed preview and collapsed safe astrology. Mobile connection actions remain above navigation. Opening the disclosure fetches astrology without gating identity rendering. Strangers receive no accepted-only Why link.

## Release boundary

Local-only. Enforced 18+ eligibility, report/flag and moderation, account deletion and Architecture v1.2's other public launch gates remain outstanding. No age enforcement is claimed. Wave 2's legacy-public-media and unscheduled cleanup-worker limitations remain. Photo-first discovery deck interaction is **`FOUNDER_APPROVED`** under [FDR-2026-01](FOUNDER_DECISION_RECORDS.md#fdr-2026-01-photo-first-human-discovery-touch-native-swipe-interaction-policy); public deployment remains gated by Wave 5 requirements.
