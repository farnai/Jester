import { guidanceItems } from './homeModel';

interface HomeDoDontProps {
  doItems?: string[] | string;
  dontItems?: string[] | string;
  isLoading: boolean;
  isError: boolean;
}

export function HomeDoDont({ doItems, dontItems, isLoading, isError }: HomeDoDontProps) {
  const dos = guidanceItems(doItems);
  const donts = guidanceItems(dontItems);

  if (isLoading) {
    return (
      <section className="home-section home-dodont-section" aria-label="გააკეთე და მოერიდე">
        <div className="home-card home-dodont-card">
          <div className="home-section-header">
            <div className="home-skeleton-line title" />
            <div className="home-skeleton-line short" />
          </div>
          <div className="home-dodont-grid">
            <div className="home-dodont-block home-do-card">
              <div className="home-skeleton-line title" />
              <div className="home-skeleton-line body" />
            </div>
            <div className="home-dodont-block home-dont-card">
              <div className="home-skeleton-line title" />
              <div className="home-skeleton-line body" />
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (isError || (dos.length === 0 && donts.length === 0)) {
    return null;
  }

  // Fallback defaults if endpoint returns fewer than 3
  const finalDos = dos.length > 0 ? dos.slice(0, 3) : ['პირველი ნაბიჯი', 'მყარი პოზიცია', 'მზერის გასწორება'];
  const finalDonts =
    donts.length > 0 ? donts.slice(0, 3) : ['სხვების გადათელვა', 'ზღვარს გადასვლა', 'პოზიორობა'];

  return (
    <section className="home-section home-dodont-section" aria-labelledby="home-dodont-heading">
      <div className="home-card home-dodont-card">
        <div className="home-section-header">
          <h2 id="home-dodont-heading" className="home-section-title">
            გააკეთე / მოერიდე
          </h2>
          <p className="home-section-subtitle">დღის ენერგიიდან გამომდინარე ფოკუსი და რისკები</p>
        </div>

        <div className="home-dodont-grid">
          {/* DO Column */}
          <div className="home-dodont-block home-do-card">
            <div className="home-do-header">
              <span className="home-do-icon" aria-hidden="true">
                ✓
              </span>
              <h3 className="home-do-title">რა გააკეთო (DO)</h3>
            </div>
            <ul className="home-dodont-list home-do-list">
              {finalDos.map((item, idx) => (
                <li key={`do-${idx}`} className="home-dodont-item home-do-item">
                  <span className="home-item-bullet">✦</span>
                  <span className="home-item-text">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* DON'T Column */}
          <div className="home-dodont-block home-dont-card">
            <div className="home-dont-header">
              <span className="home-dont-icon" aria-hidden="true">
                ✕
              </span>
              <h3 className="home-dont-title">რას მოერიდო (DON'T)</h3>
            </div>
            <ul className="home-dodont-list home-dont-list">
              {finalDonts.map((item, idx) => (
                <li key={`dont-${idx}`} className="home-dodont-item home-dont-item">
                  <span className="home-item-bullet">✕</span>
                  <span className="home-item-text">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}

