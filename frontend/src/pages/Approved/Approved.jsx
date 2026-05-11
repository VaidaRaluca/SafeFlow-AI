import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api } from '../../api/client';
import { formatCurrency, formatDateTime } from '../../utils/format';
import styles from './Approved.module.css';

export default function Approved() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tx, setTx] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .transaction(id)
      .then(setTx)
      .catch((err) => setError(err.message || 'Could not load transaction.'));
  }, [id]);

  return (
    <main className={styles.page}>
      <div className={styles.iconWrap}>
        <span className="material-symbols-outlined filled">check_circle</span>
      </div>

      <h1 className={styles.title}>Transaction Approved</h1>
      <p className={styles.subtitle}>
        Your payment {tx ? <>of <strong>{formatCurrency(tx.amount, tx.currency)}</strong></> : ''} has been
        successfully settled.
      </p>

      {error && <div className={styles.errorBanner}>{error}</div>}

      {tx && (
        <div className={styles.card}>
          <h2 className={styles.cardLabel}>Transaction Details</h2>
          <DetailRow label="Transaction ID" value={tx.id} mono />
          <DetailRow label="Date & Time" value={formatDateTime(tx.created_at)} />
          <DetailRow label="Settled At" value={formatDateTime(tx.settled_at)} />
          <DetailRow
            label="Amount"
            value={formatCurrency(tx.amount, tx.currency)}
          />
          <DetailRow
            label="Status"
            value={<span className={styles.pill}>{tx.status}</span>}
          />
        </div>
      )}

      <div className={styles.actions}>
        <button className={styles.btnPrimary} onClick={() => navigate('/dashboard')}>
          <span className="material-symbols-outlined">dashboard</span>
          Go to Dashboard
        </button>
        <Link to="/history" className={styles.btnSecondary}>
          <span className="material-symbols-outlined">receipt_long</span>
          View History
        </Link>
      </div>
    </main>
  );
}

function DetailRow({ label, value, mono }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={`${styles.rowValue} ${mono ? styles.mono : ''}`}>{value}</span>
    </div>
  );
}
