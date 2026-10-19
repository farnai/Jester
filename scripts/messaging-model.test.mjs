import test from 'node:test';
import assert from 'node:assert/strict';
import { chronologicalMessages, submission, isUnavailable } from '../frontend/src/modules/chat/messagingModel.ts';

test('replayed realtime refresh and overlapping pages render each message once', () => {
  const m = (id, created_at) => ({ id, created_at, body:id });
  const a=m('a','2026-10-19T10:00:00+00:00'), b=m('b','2026-10-19T10:00:01+00:00');
  assert.deepEqual(chronologicalMessages([{items:[b]},{items:[a,b]}]).map(x=>x.id),['a','b']);
});
test('equal timestamps have a deterministic UUID order', () => {
  assert.deepEqual(chronologicalMessages([{items:[{id:'b',created_at:'same'},{id:'a',created_at:'same'}]}]).map(x=>x.id),['a','b']);
});
test('lost acknowledgement retry retains its idempotency nonce', () => {
  const first=submission('  გამარჯობა  ');
  assert.equal(first.body,'გამარჯობა');
  assert.equal(submission('გამარჯობა',first),first);
});
test('edited draft and new submission get new nonces', () => {
  const first=submission('Hello');
  assert.notEqual(submission('Changed',first).nonce,first.nonce);
  assert.notEqual(submission('Hello').nonce,first.nonce);
});
test('only authorization/not-found responses hide a conversation', () => {
  assert.equal(isUnavailable({statusCode:404}),true);
  assert.equal(isUnavailable({statusCode:403}),true);
  assert.equal(isUnavailable({statusCode:500}),false);
  assert.equal(isUnavailable(new TypeError('offline')),false);
});
test('empty history is a valid initial state', () => assert.deepEqual(chronologicalMessages(),[]));
