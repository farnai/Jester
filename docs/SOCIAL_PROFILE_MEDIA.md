# Social profiles and private gallery

## Implemented contract

ME manages persisted social identity, gallery and declared interests. Person Profile
shows authorized identity, images, interests and their actual intersection with the
viewer, followed by existing safe astrology and compare preview. Existing connection
transitions govern chat and deeper Why navigation. Home retains its design.

Migrations `028_social_profile_photos.sql` and `029_gallery_avatar_lifecycle.sql`
add the following persistence:

| Relation | Contract |
| --- | --- |
| `profile_photos` | UUID id, owner FK to `profiles` with cascade, position 0–5, unique deferred owner/position, exactly one of private `storage_path` or preserved `legacy_url`, creation time. |
| `profile_photo_cleanup` | Durable object-deletion/failed-upload compensation queue; independent of account lifetime. No client grants. |
| `profiles.photo_gallery_managed` | Server-owned lifecycle flag; prevents OAuth initialization or legacy writes from resurrecting an avatar after gallery deletion. |

Position zero is primary. `profiles.avatar_url` is a compatibility projection updated
by a database trigger, never an independently editable primary once a gallery exists.
It contains the legacy URL or an authenticated API media path. Existing avatar
consumers use `ProfileImage` to fetch private media with the current bearer token and
render a temporary browser blob URL. Blob URLs are revoked on unmount/account change.
New clients must support authenticated media paths, not assume every avatar is public.

## API

All routes require the existing JWT verification. `{owner}` is a UUID.

| Method / route | Behavior |
| --- | --- |
| `GET /v1/profiles/{owner}/photos` | Ordered list; owner or discoverable, mutually unblocked viewer. |
| `POST /v1/profiles/me/photos` | Raw binary image body with its MIME type; returns updated list, HTTP 201. |
| `PUT /v1/profiles/me/photos/order` | `{ "photo_ids": [...] }`, an exact permutation of the current gallery; first becomes primary. |
| `DELETE /v1/profiles/me/photos/{photo_id}` | Owner-only logical deletion and compacted order; returns updated list. |
| `GET /v1/profiles/{owner}/photos/{photo_id}/content` | Reauthorizes each request and proxies private WebP bytes; no reusable signed URL. |
| `GET /v1/interests/people/{profile_id}` | Authorized active interest items and `common_interest_ids` from stored selections. |

A photo DTO has `id`, `position`, `is_primary`, `url`, `is_legacy`. Paths and internal
storage metadata are not exposed. The existing structured error envelope is preserved:
413 size, 415 unsupported MIME, 400 invalid image/order, 409 seventh photo or conflicting
legacy avatar update, privacy-safe 404 for inaccessible photos/profiles, 503 Storage failure.

Uploads accept JPEG, PNG, WebP and GIF, up to 5 MiB and 25 million decoded pixels.
Server decoding verifies the MIME against the actual format, applies EXIF orientation,
strips metadata including GPS, limits dimensions to 1600×1600, and reencodes WebP quality
85. Animation becomes the first frame. No external image URL is fetched by the server.
Owners' mutations lock their profile row; the six-slot database constraint and complete
permutation check also protect concurrent uploads and stale reorder requests.

## Storage and privacy

New images use the private `profile-photos` bucket with **no client storage policies**.
Only backend service credentials access it. Gallery tables are service-only with RLS
enabled and explicit revocation from anonymous/authenticated client roles. The API
checks profile visibility and mutual blocking before listing or serving content.
Content responses use `Cache-Control: private, no-store`, `Vary: Authorization`, and
`X-Content-Type-Options: nosniff`. Tokens never appear in image query strings.

Existing `avatars` objects and external OAuth URLs are preserved as legacy references.
That bucket remains public for compatibility; a known URL or cached copy cannot be
revoked by RLS, blocking, hiding a profile, or removing its gallery reference. Removing
a legacy reference does not delete the old object. A separate, owner-approved migration
of historical public media is still needed for a fully private historical collection.

The proxy prevents new authorized requests after blocking, hiding or deletion. It cannot
recall bytes already displayed/downloaded or screenshots. No signed URLs are issued;
using signed URLs in the future would create a bearer-access window until expiration.
No moderation workflow, content classifier, or moderator dashboard is implemented.
Private storage and the proxy provide a server-side enforcement point for future policy.

## Failure recovery

Before upload, a durable cleanup intent is committed. Successful Storage upload plus
the gallery row commit clears that intent. A failed upload/DB transaction attempts
compensating Storage API deletion; if cleanup fails the intent remains retryable.
Crash-abandoned upload intents become eligible after one hour to avoid racing in-flight
requests. Successful logical photo deletion commits its cleanup intent atomically via
trigger before touching Storage. Thus a failed physical delete leaves inaccessible bytes,
not a broken visible gallery entry. Account deletion also enqueues private objects.

Run `python -m scripts.cleanup_profile_photos` from the repository root to process up to
100 eligible operations per invocation. It never deletes a referenced object and uses
the Storage API to remove physical bytes, not direct storage metadata SQL. Failed
operations remain queued. **No background scheduler is installed**; deployments must
schedule this command and monitor the queue. The existing legacy-avatar account cleanup
behavior is retained and is not claimed to guarantee physical deletion of historical files.

## Interests and compatibility

The existing category, interest and user-interest tables and catalog endpoint are reused.
`GET/PUT /v1/interests/me` remain the owner API. Replacement now uses an explicit DB
transaction and owner lock (the existing connection is autocommit). Zero selections or
at least three unique active interests retain the currently implemented selection rule.
The product foundation mentions an upper bound of seven; the existing API/UI did not
enforce that bound. This wave preserves that behavior rather than silently changing it.
Reconciling the upper limit remains an owner/product follow-up.

Other users' selections are now limited by both API authorization and `user_interests`
SELECT RLS to discoverable, mutually unblocked profiles. Shared counts use UUID set
intersection, not inferred preferences or a recommendation score. Hidden/inactive catalog
items are omitted from person presentation. Birth data and private astrology stay untouched.

## Verification and limits

`tests/backend/test_social_profiles.py` uses real local DB/Storage and UUID-scoped test
accounts. Its deliberately injected failure cases are labeled separately. The legacy
suite can be run with `python -m scripts.run_isolated_regression` against a disposable
database clone, because some existing fixtures truncate application tables.

`python -m scripts.prepare_social_profile_qa` creates two labeled local QA accounts with
random credentials in ignored `scratch/`; `node scripts/social-profile-qa.cjs` exercises
live authentication, gallery and interest flows with Playwright. Registration image assets
are used only in the labeled QA profiles. Production has honest empty states.
After verification, `python -m scripts.prepare_social_profile_qa --cleanup` removes only
the manifest-verified QA accounts, their private media, and their ignored credentials file.

Responsive artifacts cover 1440×900, 1280×800, 390×844 and 320×700. Visual approval remains
with the Founder. Age enforcement, recommendation ranking, moderation and production
deployment are outside this implementation.
