import test from 'node:test';
import assert from 'node:assert/strict';
import { connectionFor, visibleHomePeople, personObservation, guidanceItems, calendarKey, georgianDate } from '../frontend/src/modules/home/homeModel.ts';

test('canonical pairs hide blocked people regardless of pair order, preserving server order', () => {
  const people = [{ id: 'viewer' }, { id: 'z' }, { id: 'blocked' }, { id: 'a' }];
  const connections = [{ user_a_id: 'blocked', user_b_id: 'viewer', status: 'blocked' }];
  assert.deepEqual(visibleHomePeople(people, connections, 'viewer').map(p => p.id), ['z', 'a']);
  assert.equal(connectionFor(connections, 'viewer', 'blocked').status, 'blocked');
  assert.equal(connectionFor(connections, 'stranger', 'blocked'), undefined);
});

test('unsupported or fallback sign provenance never produces a personalized hook', () => {
  for (const source of [undefined, null, '', 'fallback', 'default']) {
    assert.equal(personObservation({ presence_sign_source: source, hook_observation: { text: 'generic fallback' } }), null);
  }
  for (const source of ['sun', 'ascendant']) {
    assert.equal(personObservation({ presence_sign_source: source, hook_observation: { text: ' observed ' } }), 'observed');
    assert.equal(personObservation({ presence_sign_source: source }), null);
    assert.equal(personObservation({ presence_sign_source: source, hook_observation: { text: ' ' } }), null);
  }
});

test('optional guidance remains absent, accepts both API representations', () => {
  assert.deepEqual(guidanceItems(undefined), []);
  assert.deepEqual(guidanceItems(' one '), ['one']);
  assert.deepEqual(guidanceItems([' ', ' one ', 'two']), ['one', 'two']);
});

test('calendar cache changes at the profile timezone midnight with safe invalid-zone fallback', () => {
  const instant = new Date('2026-10-17T21:00:00Z');
  assert.equal(calendarKey(instant, 'Asia/Tbilisi'), '2026-10-18');
  assert.equal(calendarKey(instant, 'UTC'), '2026-10-17');
  assert.equal(calendarKey(instant, 'invalid-zone'), '2026-10-17');
  assert.equal(georgianDate('2026-10-18'), '18 ოქტომბერი');
  assert.equal(georgianDate(undefined), '');
  assert.equal(georgianDate('2026-13-40'), '');
});

// Render the real components without adding a browser/test dependency or a preview route.
// Only network/auth boundaries are substituted; fixtures never enter application code.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const frontendRequire = createRequire(new URL('../frontend/package.json', import.meta.url));
const ts = frontendRequire('typescript');
const React = frontendRequire('react');
const { renderToStaticMarkup } = frontendRequire('react-dom/server');
function loadSource(relative, overrides = {}) {
  const source = readFileSync(new URL(relative, import.meta.url), 'utf8');
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  const module = { exports: {} };
  const require = name => Object.hasOwn(overrides, name) ? overrides[name] : name.endsWith('.css') ? {} : frontendRequire(name);
  new Function('require', 'module', 'exports', js)(require, module, module.exports);
  return module.exports;
}
const elements = loadSource('../frontend/src/modules/home/HomeElements.tsx', { '../../shared/ui/ProfileImage': { ProfileImage: props => React.createElement('img', props) } });

test('distinct people with identical names and bios remain visible', () => {
  const people = [{ id: 'a', display_name: 'Same', bio: 'Same' }, { id: 'b', display_name: 'Same', bio: 'Same' }];
  assert.deepEqual(visibleHomePeople([...people, people[0]], [], 'viewer').map(p => p.id), ['a', 'b']);
});
const editorial = loadSource('../frontend/src/modules/home/HomeEditorial.tsx', {
  './HomeElements': elements,
  '../../assets/registration/hero_portrait.jpg': { default: '/editorial-portrait.jpg' },
  '../../assets/registration/hero_woman_highres.jpg': { default: '/editorial-secondary.jpg' },
  'react-router-dom': { Link: ({ to, children, ...props }) => React.createElement('a', { ...props, href: to }, children) },
});
const model = loadSource('../frontend/src/modules/home/homeModel.ts');
const carousel = loadSource('../frontend/src/modules/home/HomePersonCarousel.tsx', {
  './HomeElements': elements,
  './homeModel': model,
  'react-router-dom': { Link: ({ to, children, ...props }) => React.createElement('a', { ...props, href: to }, children) },
});
const success = data => ({ data, isSuccess: true, refetch() {} });
function renderHome(states) {
  const { HomePage } = loadSource('../frontend/src/modules/home/HomePage.tsx', {
    '@tanstack/react-query': { useQuery: ({ queryKey }) => states[queryKey[0]] || success(undefined) },
    '../../core/auth/useAuth': { useAuth: () => ({ user: { id: 'viewer' } }) },
    '../../core/api/endpoints': { API: { profiles: {}, connections: {} } },
    'react-router-dom': { Link: ({ to, children, ...props }) => React.createElement('a', { ...props, href: to }, children) },
    './HomeElements': elements, './homeModel': model, './HomeEditorial': editorial, './HomePersonCarousel': carousel,
  });
  return renderToStaticMarkup(React.createElement(HomePage));
}
test('loading and independent API errors render honest accessible states', () => {
  const loading = renderHome(Object.fromEntries(['profile', 'daily-energy', 'connections', 'discovery-people'].map(key => [key, { isLoading: true }])));
  assert.match(loading, /aria-label="იტვირთება"/);
  assert.doesNotMatch(loading, /home-score/);
  const errors = renderHome(Object.fromEntries(['profile', 'daily-energy', 'connections', 'discovery-people'].map(key => [key, { isError: true, refetch() {} }])));
  assert.equal((errors.match(/role="alert"/g) || []).length, 4);
  assert.match(errors, /ხელახლა ცდა/);
  assert.doesNotMatch(errors, /\/why/);
});
test('empty Home and fallback daily content do not invent people, scores or transit claims', () => {
  const empty = renderHome({ connections: success([]), 'discovery-people': success([]) });
  assert.match(empty, /დაკვირვებები ჯერ არ ჩანს/);
  assert.match(empty, /შენი დაკვირვება ჯერ არ არის ხელმისაწვდომი/);
  assert.doesNotMatch(empty, /home-score|\/why/);
  const fallback = renderHome({ 'daily-energy': success({ detection_mode: 'fallback_sun_sign', interpretation: { text: 'Fixture insight' } }) });
  assert.match(fallback, /შენი პროფილის დაკვირვება/);
  assert.doesNotMatch(fallback, /დღის დაკვირვება/);
});
test('pending profiles never receive deep comparison links or discovery fallback scores', () => {
  const pending = { user_a_id: 'viewer', user_b_id: 'candidate', initiated_by: 'viewer', status: 'pending' };
  const person = { id: 'candidate', display_name: 'Fixture', presence_sign_source: 'sun', hook_observation: { text: 'Fixture observation' }, score: 60 };
  const html = renderHome({ connections: success([pending]), 'discovery-people': success([person]) });
  assert.match(html, /მოთხოვნა გაგზავნილია/);
  assert.match(html, /href="\/people\/candidate"/);
  assert.doesNotMatch(html, /\/why|home-score/);
  const blocked = renderHome({ connections: success([{ ...pending, status: 'blocked' }]), 'discovery-people': success([person]) });
  assert.doesNotMatch(blocked, /Fixture observation|\/people\/candidate/);
});

test('accepted connection summary uses backend identity even outside the discovery page', () => {
  const html = renderHome({
    connections: success([{ id: 'connection', user_a_id: 'viewer', user_b_id: 'friend', status: 'accepted', other_display_name: 'Real friend', other_avatar_url: '/authorized-photo' }]),
    'discovery-people': success([]),
  });
  assert.match(html, /Real friend/);
  assert.match(html, /href="\/people\/friend"/);
  assert.match(html, /src="\/authorized-photo"/);
  assert.match(html, /home-conversation-invitation[\s\S]*href="\/messages"/);
  assert.doesNotMatch(html, /\/people\/friend\/why|home-score/);
  const empty = renderHome({ connections: success([]), 'discovery-people': success([]) });
  assert.match(empty, /home-conversation-invitation[\s\S]*href="\/discover"/);
});
