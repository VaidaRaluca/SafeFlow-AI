import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client';
import { formatCurrency, formatDateTime } from '../../utils/format';
import StatusBadge from '../../components/StatusBadge/StatusBadge.jsx';
import styles from './Dashboard.module.css';

const POLL_INTERVAL_MS = 5000;

export default function Dashboard() {
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [acc, list] = await Promise.all([api.myAccount(), api.myTransactions()]);
      setAccount(acc);
      setTransactions(list?.transactions || []);
      setError(null);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const id = setInterval(loadData, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  const recent = useMemo(() => transactions.slice(0, 6), [transactions]);

  const totals = useMemo(() => {
    if (!account) return { sent: 0, received: 0 };
    let sent = 0;
    let received = 0;
    for (const tx of transactions) {
      if (String(tx.status).toUpperCase() !== 'SETTLED') continue;
      const amt = Number(tx.amount) || 0;
      if (tx.sender_id === account.id) sent += amt;
      if (tx.receiver_id === account.id) received += amt;
    }
    return { sent, received };
  }, [transactions, account]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Dashboard</h1>
          <p className={styles.subtitle}>
            Live view of your account and recent transactions.
          </p>
        </div>
        <Link to="/send" className={styles.cta}>
          <span className="material-symbols-outlined filled">send</span>
          Send Money
        </Link>
      </header>

      {error && <div className={styles.error}>{error}</div>}

      <section className={styles.bento}>
        <div className={styles.balanceCard}>
          <div className={styles.balanceTopRow}>
            <span className="material-symbols-outlined">account_balance_wallet</span>
            <span className={styles.balanceLabel}>Total Balance</span>
          </div>
          <div className={styles.balanceValue}>
            {loading
              ? '…'
              : formatCurrency(account?.balance, account?.currency || 'EUR')}
          </div>
          <div className={styles.balanceMeta}>
            {account ? (
              <>
                <span className="material-symbols-outlined">account_balance</span>
                IBAN: <strong>{account.iban}</strong>
              </>
            ) : (
              'Loading account…'
            )}
          </div>
        </div>

        <div className={styles.statCard}>
          <h3>Settled Sent</h3>
          <div className={styles.statValue}>
            {formatCurrency(totals.sent, account?.currency || 'EUR')}
          </div>
          <p>Outflows that have cleared.</p>
        </div>

        <div className={styles.statCard}>
          <h3>Settled Received</h3>
          <div className={styles.statValue}>
            {formatCurrency(totals.received, account?.currency || 'EUR')}
          </div>
          <p>Inflows that have cleared.</p>
        </div>
      </section>

      <section className={styles.activitySection}>
        <div className={styles.activityHeader}>
          <h2>Recent Activity</h2>
          <Link to="/history" className={styles.linkAction}>
            View all
            <span className="material-symbols-outlined">arrow_forward</span>
          </Link>
        </div>
        <div className={styles.activityCard}>
          {recent.length === 0 ? (
            <div className={styles.empty}>
              {loading ? 'Loading transactions…' : 'No transactions yet.'}
            </div>
          ) : (
            recent.map((tx) => (
              <TransactionRow
                key={tx.id}
                tx={tx}
                accountId={account?.id}
                currency={account?.currency || 'EUR'}
              />
            ))
          )}
        </div>
      </section>
    </div>
  );
}

function TransactionRow({ tx, accountId, currency }) {
  const isOutgoing = tx.sender_id === accountId;
  const sign = isOutgoing ? '-' : '+';
  const icon = isOutgoing ? 'north_east' : 'south_west';
  return (
    <div className={styles.txRow}>
      <div className={styles.txLeft}>
        <div className={`${styles.txIcon} ${isOutgoing ? styles.outgoing : styles.incoming}`}>
          <span className="material-symbols-outlined">{icon}</span>
        </div>
        <div>
          <div className={styles.txTitle}>
            {isOutgoing ? 'Outgoing transfer' : 'Incoming transfer'}
          </div>
          <div className={styles.txMeta}>
            {formatDateTime(tx.created_at)} · {tx.description || 'No description'}
          </div>
        </div>
      </div>
      <div className={styles.txRight}>
        <StatusBadge status={tx.status} />
        <span className={styles.txAmount}>
          {sign}
          {formatCurrency(tx.amount, tx.currency || currency)}
        </span>
      </div>
    </div>
  );
}
