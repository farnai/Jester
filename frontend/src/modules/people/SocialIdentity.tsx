import { useState, type ReactNode } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import type { ProfilePhoto, ProfileResponse, VisibilityPolicy } from '../../core/api/types';
import { ProfileImage } from '../../shared/ui/ProfileImage';
import './social-profile.css';

export function SocialIdentity({ profile, editable = false, actions, connectionActions }: { profile: ProfileResponse; editable?: boolean; actions?: ReactNode; connectionActions?: ReactNode }) {
  const cache = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editingPhotos, setEditingPhotos] = useState(false);
  const [fileError, setFileError] = useState('');
  const photos = useQuery({ queryKey: ['photos', profile.id], queryFn: () => API.profiles.photos(profile.id), retry: false });
  const mutation = useMutation({
    mutationFn: (action: { file: File } | { ids: string[] } | { remove: string }) =>
      'file' in action ? API.profiles.uploadPhoto(action.file) : 'ids' in action ? API.profiles.orderPhotos(action.ids) : API.profiles.deletePhoto(action.remove),
    onSuccess: (items) => {
      cache.setQueryData(['photos', profile.id], items);
      cache.invalidateQueries({ queryKey: ['profile'] });
      cache.invalidateQueries({ queryKey: ['discovery'] });
      cache.invalidateQueries({ queryKey: ['discovery-people'] });
      cache.invalidateQueries({ queryKey: ['discovery-deck'] });
    },
  });
  const items = photos.data || [];
  const selected = items.find(item => item.id === selectedId) || items[0];
  const move = (item: ProfilePhoto, to: number) => {
    const ids = items.map(photo => photo.id);
    ids.splice(ids.indexOf(item.id), 1);
    ids.splice(to, 0, item.id);
    mutation.mutate({ ids });
  };
  return <section className="social-identity">
    <div className="social-gallery">
      <div className="social-portrait">
        {photos.isPending ? <p role="status">ფოტოები იტვირთება…</p> : photos.isError ? <div role="alert"><p>ფოტოები ვერ ჩაიტვირთა.</p><button onClick={() => photos.refetch()}>ხელახლა ცდა</button></div> : selected ? <ProfileImage key={selected.id} src={selected.url} alt={`${profile.display_name} — ფოტო ${selected.position + 1}`} /> : <div className="social-photo-empty"><span aria-hidden="true">◎</span><h2>ფოტო ჯერ არ არის</h2><p>{editable ? 'შენი ამბავი შენი ფოტოთი იწყება.' : 'მომხმარებელს ფოტო ჯერ არ დაუმატებია.'}</p></div>}
        {selected && <span className="social-photo-count">{selected.position + 1} / {items.length}</span>}
      </div>
      {items.length > 1 && <div className="social-thumbnails" aria-label="ფოტოების გალერეა">{items.map(item => <button key={item.id} aria-label={`ფოტო ${item.position + 1}`} aria-pressed={selected?.id === item.id} onClick={() => setSelectedId(item.id)}><ProfileImage src={item.url} alt="" /></button>)}</div>}
      {editable && <>
        <button className="social-text-button" onClick={() => setEditingPhotos(!editingPhotos)} aria-expanded={editingPhotos}>{editingPhotos ? 'მართვის დახურვა' : 'ფოტოების მართვა'} <span>{items.length}/6</span></button>
        {editingPhotos && <div className="social-photo-editor">
          <p>პირველი ფოტო მთავარია. JPEG, PNG, WebP ან GIF · მაქს. 5 MB. ანიმაცია ინახება ერთ კადრად.</p>
          <label className="social-upload">{mutation.isPending ? 'ინახება…' : items.length >= 6 ? 'დამატებულია 6 ფოტო' : '+ ფოტოს დამატება'}<input aria-label="ფოტოს დამატება" type="file" accept="image/jpeg,image/png,image/webp,image/gif" disabled={mutation.isPending || items.length >= 6 || photos.isError} onChange={event => {
            const file = event.target.files?.[0]; event.target.value = ''; setFileError('');
            if (!file) return;
            if (file.size > 5 * 1024 * 1024) { setFileError('ფოტო არ უნდა აღემატებოდეს 5 MB-ს.'); return; }
            mutation.mutate({ file });
          }} /></label>
          {items.map((item, index) => <div className="social-photo-row" key={item.id}>
            <button className="social-mini-photo" aria-label={`არჩევა ${index + 1}`} onClick={() => setSelectedId(item.id)}><ProfileImage src={item.url} alt="" /></button>
            <span>{index === 0 ? 'მთავარი' : `ფოტო ${index + 1}`}</span>
            <div className="social-photo-actions">
              <button disabled={mutation.isPending || index === 0} onClick={() => move(item, 0)} aria-label={`მთავარ ფოტოდ ${index + 1}`}>მთავარი</button>
              <button disabled={mutation.isPending || index === 0} onClick={() => move(item, index - 1)} aria-label={`წინ ${index + 1}`}>←</button>
              <button disabled={mutation.isPending || index === items.length - 1} onClick={() => move(item, index + 1)} aria-label={`უკან ${index + 1}`}>→</button>
              <button disabled={mutation.isPending} onClick={() => { if (window.confirm('წაიშალოს ეს ფოტო პროფილიდან?')) mutation.mutate({ remove: item.id }); }} aria-label={`წაშლა ${index + 1}`}>წაშლა</button>
            </div>
          </div>)}
          {items.some(item => item.is_legacy) && <p className="social-note">ძველი ავატარი შესაძლოა საჯარო ბმულითაც იყოს ხელმისაწვდომი. აქ წაშლა ძველ საჯარო ასლებს არ აუქმებს.</p>}
          {(fileError || mutation.error) && <p role="alert">{fileError || mutation.error?.message}</p>}
          {mutation.isSuccess && <p role="status">გალერეა შენახულია.</p>}
        </div>}
      </>}
    </div>
    <div className="social-story">
      <p className="social-eyebrow">{editable ? 'ME / ჩემი პროფილი' : 'YOU / გაიცანი ადამიანი'}</p>
      <h1>{profile.display_name}</h1>
      <p className="social-location">{[profile.city, profile.occupation].filter(Boolean).join(' · ') || 'ქალაქი ჯერ არ არის მითითებული'}</p>
      <p className="social-bio">{profile.bio || (editable ? 'მოუყევი სხვებს შენზე — რა გიყვარს, რა გაინტერესებს, რა გაბედნიერებს.' : 'აღწერა ჯერ არ არის დამატებული.')}</p>
      {editable && <p className="social-visibility">{profile.is_discoverable ? '● პროფილი აღმოჩენადია' : '○ პროფილი დამალულია'}</p>}
      <div className="social-identity-actions">{actions}</div>
      <div className="social-enrichment-sections">
        <ProfileInterests owner={profile.id} editable={editable} />
        <ProfilePersonality owner={profile.id} editable={editable} initialVisibility={profile.personality_visibility} />
        <ProfileIntentions owner={profile.id} editable={editable} initialVisibility={profile.intentions_visibility} />
      </div>
      {connectionActions}
    </div>
  </section>;
}

function ProfileInterests({ owner, editable }: { owner: string; editable: boolean }) {
  const cache = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const interests = useQuery({ queryKey: ['person-interests', owner], queryFn: () => API.interests.forPerson(owner) });
  const catalog = useQuery({ queryKey: ['interests-catalog'], queryFn: API.interests.list, enabled: editing });
  const saved = useQuery({ queryKey: ['my-interests'], queryFn: API.interests.getMyInterests, enabled: editable });
  const mutation = useMutation({ mutationFn: API.interests.setMyInterests, onSuccess: () => {
    cache.invalidateQueries({ queryKey: ['person-interests'] });
    cache.invalidateQueries({ queryKey: ['my-interests'] });
    cache.invalidateQueries({ queryKey: ['discovery-deck'] });
    setEditing(false);
  } });
  const common = interests.data?.common_interest_ids || [];
  return <section className="social-interests">
    <div className="social-section-heading"><h2>ინტერესები</h2>{editable && <button disabled={!saved.data} onClick={() => { setSelected(saved.data?.interest_ids || []); setEditing(!editing); mutation.reset(); }}>{editing ? 'გაუქმება' : 'რედაქტირება'}</button>}</div>
    {interests.isPending ? <p role="status">ინტერესები იტვირთება…</p> : interests.isError || saved.isError ? <p role="alert">ინტერესები ვერ ჩაიტვირთა. <button onClick={() => { interests.refetch(); saved.refetch(); }}>ხელახლა ცდა</button></p> : <>
      {!editable && <p className="social-common">{common.length ? `${common.length} საერთო ინტერესი` : 'საერთო ინტერესები ჯერ არ გაქვთ'}</p>}
      <div className="social-tags">{interests.data?.items.map(item => <span className={common.includes(item.id) ? 'is-common' : ''} key={item.id}>{common.includes(item.id) ? '↔ ' : ''}{item.name}</span>)}</div>
      {!interests.data?.items.length && <p className="social-note">ინტერესები ჯერ არ არის არჩეული.</p>}
    </>}
    {editing && <form className="social-interest-editor" onSubmit={event => { event.preventDefault(); mutation.mutate(selected); }}>
      <p>აირჩიე 0-დან 7 ინტერესამდე (ან გაასუფთავე არჩევანი). არჩეულია: {selected.length} / 7</p>
      <input aria-label="ინტერესების ძებნა" placeholder="მოძებნე ინტერესი (ქართულად ან ინგლისურად)" value={search} onChange={e => setSearch(e.target.value)} />
      {catalog.isPending && <p role="status">კატალოგი იტვირთება…</p>}
      {catalog.isError && <p role="alert">კატალოგი ვერ ჩაიტვირთა. <button type="button" onClick={() => catalog.refetch()}>ხელახლა ცდა</button></p>}
      <div className="social-tags">{catalog.data?.items.filter(i => {
        const q = search.toLowerCase().trim();
        if (!q) return true;
        const haystack = [i.name, i.name_ka || '', i.name_en || '', ...(i.aliases || []), i.category_name, i.category_name_ka || '', i.category_name_en || ''].join(' ').toLowerCase();
        return haystack.includes(q);
      }).map(item => <button disabled={mutation.isPending} type="button" key={item.id} aria-pressed={selected.includes(item.id)} onClick={() => setSelected(ids => {
        if (ids.includes(item.id)) return ids.filter(id => id !== item.id);
        if (ids.length >= 7) return ids;
        return [...ids, item.id];
      })}>{item.name}</button>)}</div>
      <div className="social-editor-actions"><button type="submit" disabled={mutation.isPending || selected.length > 7 || !catalog.data}>{mutation.isPending ? 'ინახება…' : 'ინტერესების შენახვა'}</button><button type="button" disabled={mutation.isPending} onClick={() => setSelected([])}>გასუფთავება</button></div>
      {mutation.error && <p role="alert">{mutation.error.message}</p>}
    </form>}
    {mutation.isSuccess && <p role="status">ინტერესები შენახულია.</p>}
  </section>;
}

function ProfilePersonality({ owner, editable, initialVisibility }: { owner: string; editable: boolean; initialVisibility?: VisibilityPolicy }) {
  const cache = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [visibility, setVisibility] = useState<VisibilityPolicy>(initialVisibility || 'public');
  const traits = useQuery({ queryKey: ['person-traits', owner], queryFn: () => API.personality.forPerson(owner) });
  const catalog = useQuery({ queryKey: ['personality-catalog'], queryFn: API.personality.list, enabled: editing });
  const saved = useQuery({ queryKey: ['my-traits'], queryFn: API.personality.getMyTraits, enabled: editable });

  const mutation = useMutation({
    mutationFn: async ({ traitIds, vis }: { traitIds: string[]; vis: VisibilityPolicy }) => {
      await API.personality.setMyTraits(traitIds);
      await API.profiles.updateMyProfile({ personality_visibility: vis });
    },
    onSuccess: () => {
      cache.invalidateQueries({ queryKey: ['person-traits'] });
      cache.invalidateQueries({ queryKey: ['my-traits'] });
      cache.invalidateQueries({ queryKey: ['profile'] });
      setEditing(false);
    },
  });

  return (
    <section className="social-interests social-personality">
      <div className="social-section-heading">
        <h2>ჩემი ხასიათი</h2>
        {editable && (
          <button
            disabled={!saved.data}
            onClick={() => {
              setSelected(saved.data?.trait_ids || []);
              if (initialVisibility) setVisibility(initialVisibility);
              setEditing(!editing);
              mutation.reset();
            }}
          >
            {editing ? 'გაუქმება' : 'რედაქტირება'}
          </button>
        )}
      </div>

      {traits.isPending ? (
        <p role="status">ხასიათის თვისებები იტვირთება…</p>
      ) : traits.isError || saved.isError ? (
        <p role="alert">
          თვისებები ვერ ჩაიტვირთა.{' '}
          <button onClick={() => { traits.refetch(); saved.refetch(); }}>ხელახლა ცდა</button>
        </p>
      ) : (
        <>
          <div className="social-tags">
            {traits.data?.items.map((item) => (
              <span key={item.id}>{item.name_ka || item.name}</span>
            ))}
          </div>
          {!traits.data?.items.length && <p className="social-note">ხასიათის თვისებები ჯერ არ არის არჩეული.</p>}
        </>
      )}

      {editing && (
        <form
          className="social-interest-editor"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate({ traitIds: selected, vis: visibility });
          }}
        >
          <p>აირჩიე 0-დან 5 თვისებამდე (არჩეულია: {selected.length} / 5)</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
            <label htmlFor="personality-vis-select">ხილვადობა:</label>
            <select
              id="personality-vis-select"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value as VisibilityPolicy)}
              style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid #CBD5E1' }}
            >
              <option value="public">საჯარო (Public)</option>
              <option value="connections_only">მხოლოდ კონტაქტებისთვის (Connections)</option>
              <option value="private">პირადი (Private)</option>
            </select>
          </div>

          {catalog.isPending && <p role="status">კატალოგი იტვირთება…</p>}
          <div className="social-tags">
            {catalog.data?.items.map((item) => (
              <button
                disabled={mutation.isPending}
                type="button"
                key={item.id}
                aria-pressed={selected.includes(item.id)}
                onClick={() =>
                  setSelected((ids) => {
                    if (ids.includes(item.id)) return ids.filter((id) => id !== item.id);
                    if (ids.length >= 5) return ids;
                    return [...ids, item.id];
                  })
                }
              >
                {item.name_ka || item.name}
              </button>
            ))}
          </div>

          <div className="social-editor-actions">
            <button type="submit" disabled={mutation.isPending || selected.length > 5 || !catalog.data}>
              {mutation.isPending ? 'ინახება…' : 'თვისებების შენახვა'}
            </button>
            <button type="button" disabled={mutation.isPending} onClick={() => setSelected([])}>
              გასუფთავება
            </button>
          </div>
          {mutation.error && <p role="alert">{mutation.error.message}</p>}
        </form>
      )}
      {mutation.isSuccess && <p role="status">ხასიათის თვისებები შენახულია.</p>}
    </section>
  );
}

function ProfileIntentions({ owner, editable, initialVisibility }: { owner: string; editable: boolean; initialVisibility?: VisibilityPolicy }) {
  const cache = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [visibility, setVisibility] = useState<VisibilityPolicy>(initialVisibility || 'public');
  const intentions = useQuery({ queryKey: ['person-intentions', owner], queryFn: () => API.intentions.forPerson(owner) });
  const catalog = useQuery({ queryKey: ['intentions-catalog'], queryFn: API.intentions.list, enabled: editing });
  const saved = useQuery({ queryKey: ['my-intentions'], queryFn: API.intentions.getMyIntentions, enabled: editable });

  const mutation = useMutation({
    mutationFn: async ({ intentionIds, vis }: { intentionIds: string[]; vis: VisibilityPolicy }) => {
      await API.intentions.setMyIntentions(intentionIds);
      await API.profiles.updateMyProfile({ intentions_visibility: vis });
    },
    onSuccess: () => {
      cache.invalidateQueries({ queryKey: ['person-intentions'] });
      cache.invalidateQueries({ queryKey: ['my-intentions'] });
      cache.invalidateQueries({ queryKey: ['profile'] });
      setEditing(false);
    },
  });

  return (
    <section className="social-interests social-intentions">
      <div className="social-section-heading">
        <h2>რას ვეძებ</h2>
        {editable && (
          <button
            disabled={!saved.data}
            onClick={() => {
              setSelected(saved.data?.intention_ids || []);
              if (initialVisibility) setVisibility(initialVisibility);
              setEditing(!editing);
              mutation.reset();
            }}
          >
            {editing ? 'გაუქმება' : 'რედაქტირება'}
          </button>
        )}
      </div>

      {intentions.isPending ? (
        <p role="status">მიზნები იტვირთება…</p>
      ) : intentions.isError || saved.isError ? (
        <p role="alert">
          მიზნები ვერ ჩაიტვირთა.{' '}
          <button onClick={() => { intentions.refetch(); saved.refetch(); }}>ხელახლა ცდა</button>
        </p>
      ) : (
        <>
          <div className="social-tags">
            {intentions.data?.items.map((item) => (
              <span key={item.id}>
                {item.icon ? `${item.icon} ` : ''}
                {item.name_ka || item.name}
              </span>
            ))}
          </div>
          {!intentions.data?.items.length && <p className="social-note">მიზნები ჯერ არ არის არჩეული.</p>}
        </>
      )}

      {editing && (
        <form
          className="social-interest-editor"
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate({ intentionIds: selected, vis: visibility });
          }}
        >
          <p>აირჩიე 0-დან 3 მიზნამდე (არჩეულია: {selected.length} / 3)</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
            <label htmlFor="intentions-vis-select">ხილვადობა:</label>
            <select
              id="intentions-vis-select"
              value={visibility}
              onChange={(e) => setVisibility(e.target.value as VisibilityPolicy)}
              style={{ padding: '4px 8px', borderRadius: '6px', border: '1px solid #CBD5E1' }}
            >
              <option value="public">საჯარო (Public)</option>
              <option value="connections_only">მხოლოდ კონტაქტებისთვის (Connections)</option>
              <option value="private">პირადი (Private)</option>
            </select>
          </div>

          {catalog.isPending && <p role="status">კატალოგი იტვირთება…</p>}
          <div className="social-tags">
            {catalog.data?.items.map((item) => (
              <button
                disabled={mutation.isPending}
                type="button"
                key={item.id}
                aria-pressed={selected.includes(item.id)}
                onClick={() =>
                  setSelected((ids) => {
                    if (ids.includes(item.id)) return ids.filter((id) => id !== item.id);
                    if (ids.length >= 3) return ids;
                    return [...ids, item.id];
                  })
                }
              >
                {item.icon ? `${item.icon} ` : ''}
                {item.name_ka || item.name}
              </button>
            ))}
          </div>

          <div className="social-editor-actions">
            <button type="submit" disabled={mutation.isPending || selected.length > 3 || !catalog.data}>
              {mutation.isPending ? 'ინახება…' : 'მიზნების შენახვა'}
            </button>
            <button type="button" disabled={mutation.isPending} onClick={() => setSelected([])}>
              გასუფთავება
            </button>
          </div>
          {mutation.error && <p role="alert">{mutation.error.message}</p>}
        </form>
      )}
      {mutation.isSuccess && <p role="status">მიზნები შენახულია.</p>}
    </section>
  );
}
