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
    return String(tx.status).toUpperCase() === filter;
  });

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Transaction History</h1>
          <p className={styles.subtitle}>
            All transfers associated with your account.
          </p>
        </div>
        <div className={styles.filters}>
          {['ALL', 'PENDING', 'WARNED', 'SETTLED', 'REJECTED', 'CANCELED'].map(
            (f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`${styles.filterBtn} ${
                  filter === f ? styles.filterActive : ''
                }`}
                type="button"
              >
                {f}
              </button>
            )
          )}
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
                  <div>
                    <div className={styles.title2}>
                      {isOutgoing ? 'Outgoing' : 'Incoming'} ·{' '}
                      {tx.description || 'No description'}
                    </div>
                    <div className={styles.meta}>
                      {formatDateTime(tx.created_at)} · ID {tx.id.slice(0, 8)}…
                    </div>
                  </div>
                </div>
                <div className={styles.right}>
                  <StatusBadge status={tx.status} />
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
