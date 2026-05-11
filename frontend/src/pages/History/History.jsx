import { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { formatCurrency, formatDateTime } from '../../utils/format';
import StatusBadge from '../../components/StatusBadge/StatusBadge.jsx';
import styles from './History.module.css';

export default function History() {
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const [acc, list] = await Promise.all([
          api.myAccount(),
          api.myTransactions(),
        ]);
        if (cancelled) return;
        setAccount(acc);
        setTransactions(list?.transactions || []);
      } catch (err) {
        if (!cancelled) setError(err.message || 'Could not load history.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const filtered = transactions.filter((tx) => {
    if (filter === 'ALL') return true;
    const status = String(tx.status).toUpperCase();
    if (filter === 'WARNED_CONFIRMED') {
      return status === 'SETTLED' && tx.requires_password_confirmation;
    }
    if (filter === 'SETTLED') {
      return status === 'SETTLED' && !tx.requires_password_confirmation;
    }
    return status === filter;
  });

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.subtitle}>
            All transfers associated with your account.
          </p>
        </div>
        <div className={styles.filters}>
          {[
            { key: 'ALL', label: 'All' },
            { key: 'WARNED', label: 'Warned' },
            { key: 'WARNED_CONFIRMED', label: 'Warned' },
            { key: 'SETTLED', label: 'Settled' },
            { key: 'REJECTED', label: 'Rejected' },
            { key: 'CANCELED', label: 'Canceled' },
          ].map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`${styles.filterBtn} ${
                filter === f.key ? styles.filterActive : ''
              }`}
              type="button"
            >
              {f.label}
            </button>
          ))}
        </div>
      </header>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.card}>
        {loading ? (
          <div className={styles.empty}>Loading transactions…</div>
        ) : filtered.length === 0 ? (
          <div className={styles.empty}>No transactions found.</div>
        ) : (
          filtered.map((tx) => {
            const isOutgoing = tx.sender_id === account?.id;
            const counterpartyName = isOutgoing
              ? tx.receiver_name
              : tx.sender_name;
            const counterpartyIban = isOutgoing
              ? tx.receiver_iban
              : tx.sender_iban;
            return (
              <div key={tx.id} className={styles.row}>
                <div className={styles.left}>
                  <div
                    className={`${styles.icon} ${
                      isOutgoing ? styles.outgoing : styles.incoming
                    }`}
                  >
                    <span className="material-symbols-outlined">
                      {isOutgoing ? 'north_east' : 'south_west'}
                    </span>
                  </div>
                  <div className={styles.partyBlock}>
                    <div className={styles.title2}>
                      {isOutgoing ? 'To' : 'From'}:{' '}
                      {counterpartyName || 'Unknown account'}
                    </div>
                    <div className={styles.iban}>
                      {counterpartyIban || '—'}
                    </div>
                    <div className={styles.meta}>
                      {tx.description || 'No description'} ·{' '}
                      {formatDateTime(tx.created_at)}
                    </div>
                  </div>
                </div>
                <div className={styles.right}>
                  <StatusBadge
                    status={tx.status}
                    wasWarned={tx.requires_password_confirmation}
                  />
                  <span className={styles.amount}>
                    {isOutgoing ? '-' : '+'}
                    {formatCurrency(tx.amount, tx.currency)}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
