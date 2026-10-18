import { useState, type ReactNode } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { API } from '../../core/api/endpoints';
import type { ProfilePhoto, ProfileResponse } from '../../core/api/types';
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
      <ProfileInterests owner={profile.id} editable={editable} />
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
      <p>აირჩიე მინიმუმ 3 ინტერესი ან გაასუფთავე არჩევანი. არჩეულია: {selected.length}</p>
      <input aria-label="ინტერესების ძებნა" placeholder="მოძებნე ინტერესი" value={search} onChange={e => setSearch(e.target.value)} />
      {catalog.isPending && <p role="status">კატალოგი იტვირთება…</p>}
      {catalog.isError && <p role="alert">კატალოგი ვერ ჩაიტვირთა. <button type="button" onClick={() => catalog.refetch()}>ხელახლა ცდა</button></p>}
      <div className="social-tags">{catalog.data?.items.filter(i => `${i.name} ${i.category_name}`.toLowerCase().includes(search.toLowerCase())).map(item => <button disabled={mutation.isPending} type="button" key={item.id} aria-pressed={selected.includes(item.id)} onClick={() => setSelected(ids => ids.includes(item.id) ? ids.filter(id => id !== item.id) : [...ids, item.id])}>{item.name}</button>)}</div>
      <div className="social-editor-actions"><button type="submit" disabled={mutation.isPending || (selected.length > 0 && selected.length < 3) || !catalog.data}>{mutation.isPending ? 'ინახება…' : 'ინტერესების შენახვა'}</button><button type="button" disabled={mutation.isPending} onClick={() => setSelected([])}>გასუფთავება</button></div>
      {mutation.error && <p role="alert">{mutation.error.message}</p>}
    </form>}
    {mutation.isSuccess && <p role="status">ინტერესები შენახულია.</p>}
  </section>;
}
