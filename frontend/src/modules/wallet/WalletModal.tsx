import React, { useEffect } from 'react';
import { useWallet } from './useWallet';
import './wallet.css';

interface WalletModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const WalletModal: React.FC<WalletModalProps> = ({ isOpen, onClose }) => {
  const { wallet, transactions, transactionsLoading, pricing } = useWallet();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const balance = wallet?.balance ?? 0;
  const totalEarned = wallet?.total_earned ?? 0;
  const totalSpent = wallet?.total_spent ?? 0;

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString('ka-GE', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="home-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="wallet-modal-title">
      <div className="home-modal-backdrop" onClick={onClose} />
      <div className="home-modal-card wallet-modal-card">
        {/* Header */}
        <div className="wallet-modal-header">
          <div className="wallet-modal-header-info">
            <h3 id="wallet-modal-title" className="wallet-modal-title">
              <span>✦</span> ვარსკვლავების საფულე
            </h3>
            <p className="wallet-modal-subtitle">JESTER-ის შიდა ვირტუალური ვალუტა</p>
          </div>
          <button
            type="button"
            className="home-modal-close-btn"
            onClick={onClose}
            aria-label="დახურვა"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="wallet-modal-body">
          {/* Hero Balance Card */}
          <div className="wallet-hero-card">
            <span className="wallet-hero-label">ხელმისაწვდომი ბალანსი</span>
            <div className="wallet-hero-balance-row">
              <span className="wallet-hero-star">✦</span>
              <span className="wallet-hero-number">{balance.toLocaleString()}</span>
              <span className="wallet-hero-currency">ვარსკვლავი</span>
            </div>
            <div className="wallet-hero-stats">
              <div className="wallet-hero-stat-item">
                მიღებული: <span>+{totalEarned.toLocaleString()} ✦</span>
              </div>
              <div className="wallet-hero-stat-item">
                დახარჯული: <span>-{totalSpent.toLocaleString()} ✦</span>
              </div>
            </div>
          </div>

          {/* Pricing & Value Grid */}
          <div className="wallet-pricing-section">
            <h4 className="wallet-section-heading">განბლოკვის ტარიფები</h4>
            <div className="wallet-pricing-grid">
              <div className="wallet-pricing-item">
                <span className="wallet-pricing-name">კვირის ენერგია</span>
                <span className="wallet-pricing-cost">{pricing?.weekly_energy_stars ?? 5} ✦</span>
                <span className="wallet-pricing-note">1 კალენდარული კვირა</span>
              </div>
              <div className="wallet-pricing-item">
                <span className="wallet-pricing-name">პირადი შრე</span>
                <span className="wallet-pricing-cost">{pricing?.personal_layer_stars ?? 5} ✦</span>
                <span className="wallet-pricing-note">მუდმივი წვდომა თითო შრეზე</span>
              </div>
            </div>

            <div className="wallet-free-features">
              <strong>ყოველთვის უფასო:</strong> დღის ენერგია, Do & Don't რჩევები, Discovery აღმოჩენა და საჯარო პროფილები.
            </div>
          </div>

          {/* Transactions Ledger */}
          <div className="wallet-history-section">
            <h4 className="wallet-section-heading">ტრანზაქციების ისტორია</h4>
            {transactionsLoading ? (
              <div className="wallet-empty-history">იტვირთება…</div>
            ) : transactions.length === 0 ? (
              <div className="wallet-empty-history">ტრანზაქციები ჯერ არ არის</div>
            ) : (
              <div className="wallet-transactions-list">
                {transactions.map((tx) => {
                  const isCredit = tx.amount > 0;
                  return (
                    <div key={tx.id} className="wallet-tx-item">
                      <div className="wallet-tx-info">
                        <span className="wallet-tx-desc">{tx.description_ka}</span>
                        <span className="wallet-tx-date">{formatDate(tx.created_at)}</span>
                      </div>
                      <div className="wallet-tx-amount-col">
                        <span className={`wallet-tx-amount ${isCredit ? 'is-credit' : 'is-debit'}`}>
                          {isCredit ? `+${tx.amount.toLocaleString()}` : `${tx.amount.toLocaleString()}`} ✦
                        </span>
                        <span className="wallet-tx-balance-after">
                          ნაშთი: {tx.balance_after.toLocaleString()} ✦
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <p className="wallet-footer-notice">
            ℹ MVP ეტაპზე ვარსკვლავები წარმოადგენს აპლიკაციის შიდა ვირტუალურ სისტემას. რეალური ფული და საბანკო გადახდები არ მონაწილეობს.
          </p>
        </div>
      </div>
    </div>
  );
};

