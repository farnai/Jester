# Connections & Messaging MVP — implemented contract

Wave 4 completes the accepted-connection messaging loop without changing Synastry, discovery ranking or private-media authorization. See [API](API.md), [security](SECURITY.md) and migration `031_messaging_mvp.sql` for the durable contracts.

## Connection lifecycle

Incoming requests can be accepted or declined; outgoing requests can be cancelled. Accepted connections expose the existing conversation action on Discover, full Person Profile and Connections. Remove makes both history and sending inaccessible, while retaining storage. Reaccepting the canonical pair restores the same conversation. Unblock leaves the pair removed, never automatically accepted.

Only the blocking actor may unblock. The blocked participant cannot clear or steal a block through any transition, including remove or another block. Direct database clients cannot forge accepted connections or directly update/delete a connection.

## Inbox and chat

The inbox reads the conversations-list backend, ordered by actual last activity. It displays authorized name/photo, latest message, actual activity and caller-private unread count. Hidden profiles use a neutral name/avatar. Loading, empty, error and retry states are explicit.

History loads the latest 30 messages with UUID cursor pagination for older pages (server maximum 100). Overlapping responses are merged by ID and ordered by timestamp/ID. Older-page insertion preserves scroll position. Active bottom-of-thread viewing advances a private read pointer; background/scrolled-up views do not intentionally acknowledge unseen new messages. Read state is not a peer read receipt.

Each send carries a random UUID nonce. A failed acknowledgement retains the draft and nonce; retry with the same text cannot create another message. Editing the failed text creates a new submission. Drafts are in-memory, not a persistent offline outbox. Composer text is plain text; Enter adds a line, Ctrl/Cmd+Enter submits. The mobile layout follows VisualViewport changes and reserves bottom-navigation space; when the keyboard reduces the visual viewport, the bottom navigation is hidden.

Supabase Realtime `messages` INSERT and `connections` events invalidate authorized HTTP queries. Raw event bodies are never inserted into the UI cache. Re-subscription, online and visibility changes resynchronize. Five-second foreground connection/inbox/detail checks recover missed events, including blocks whose now-hidden row cannot reach the blocked recipient; chat history also refreshes every 15 seconds. In-flight history pagination is not cancelled by event invalidation. Logout clears query state through the existing auth lifecycle.

Starters reuse accepted-connection Why insights and only fill the editable composer. There is no new AI call, no private-message mining, no preview-auth fallback and no auto-send.

## Migration and verification

Migration 031 adds nonce/read state, indexes, a connection-gated INSERT trigger, stricter pending-only connection INSERT RLS, and connection Realtime publication. Preflight must verify environment, applied migration ledger and current rows. It performs no row deletion or historical message rewrite. Historical invalid bodies are preserved by a NOT VALID constraint; new writes are checked.

`scripts/prepare_social_profile_qa.py --wave4` creates two explicitly labeled, local-only Auth accounts, profile media and interests. Credentials stay in ignored scratch. `scripts/messaging-wave4-qa.cjs` logs in through real browser forms, uses real APIs and captures screenshots. Offline network mode is an explicit failure injection, not a mocked business contract. Cleanup verifies account IDs and email ownership before deleting only those QA accounts and their private media.

Use `python -m scripts.run_isolated_regression` for legacy destructive fixtures. Never run that legacy suite directly against the primary database. The scoped Wave 4 test module uses UUID-only cleanup and includes a real row-lock/block race.

## Public-release gates

- Reporting/moderation workflows and operational abuse response are not completed by this wave.
- Production 18+ enforcement remains an explicit release gate; QA uses adult local fixtures, which does not prove production age enforcement.
- Physical iOS/Android keyboard and background-resume checks remain device acceptance work; desktop Chrome viewport checks do not replace them.
- Founder visual approval is separate from technical verification. No public deployment is part of Wave 4.
- Read-only disconnect archives, message attachments, typing indicators, peer read receipts, push message notifications and persistent offline drafts are not implemented here. They must not be inferred from existing schema or proposal documents.
