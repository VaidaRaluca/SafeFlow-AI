import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import { formatCurrency } from '../../utils/format';
import styles from './SendMoney.module.css';

export default function SendMoney() {
  const navigate = useNavigate();
  const [account, setAccount] = useState(null);
  const [form, setForm] = useState({
    receiver_iban: '',
    receiver_name: '',
    amount: '',
    description: '',
  });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    api
      .myAccount()
      .then((acc) => {
        if (!cancelled) setAccount(acc);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || 'Could not load account.');
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!account) return;

    const trimmedIban = form.receiver_iban.replace(/\s+/g, '');
    if (trimmedIban.length < 15) {
      setError('Please enter a valid IBAN (min. 15 characters).');
      return;
    }
    const amount = Number(form.amount);
    if (!amount || amount <= 0) {
      setError('Amount must be greater than zero.');
      return;
    }
    if (amount > Number(account.balance)) {
      setError('Amount exceeds your available balance.');
      return;
    }

    setSubmitting(true);
    try {
      const tx = await api.createPayment({
        receiver_iban: trimmedIban,
        amount: amount.toFixed(2),
        currency: account.currency,
        description: form.description || null,
      });
      navigate(`/transactions/${tx.id}/evaluate`, { replace: true });
    } catch (err) {
      setError(err.message || 'Could not initiate transfer.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.headerBlock}>
        <h1 className={styles.title}>Send Money</h1>
        <p className={styles.subtitle}>
          Securely transfer funds. Every transaction is monitored.
        </p>
      </div>

      <div className={styles.card}>
        <div className={styles.aiBanner}>
          <span className="material-symbols-outlined">smart_toy</span>
          <span>
            This transaction will be analyzed in real-time by SafeFlow AI for
            security.
          </span>
        </div>

        <div className={styles.balancePill}>
          Available balance:&nbsp;
          <strong>
            {account
              ? formatCurrency(account.balance, account.currency)
              : 'Loading…'}
          </strong>
        </div>

        {error && <div className={styles.errorBanner}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="amount">Amount ({account?.currency || 'EUR'})</label>
            <div className={styles.amountWrap}>
              <span className={styles.currencyMark}>
                {account?.currency === 'USD'
                  ? '$'
                  : account?.currency === 'GBP'
                  ? '£'
                  : account?.currency === 'RON'
                  ? 'lei'
                  : '€'}
              </span>
              <input
                id="amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                value={form.amount}
                onChange={update('amount')}
                className={styles.amountInput}
                required
              />
            </div>
          </div>

          <hr className={styles.divider} />

          <h3 className={styles.section}>Receiver Details</h3>

          <div className={styles.field}>
            <label htmlFor="receiver_name">Full Name (optional)</label>
            <div className={styles.inputWrap}>
              <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                person
              </span>
              <input
                id="receiver_name"
                type="text"
                placeholder="e.g. Jane Doe"
                value={form.receiver_name}
                onChange={update('receiver_name')}
                className={styles.input}
              />
            </div>
          </div>

          <div className={styles.field}>
            <label htmlFor="receiver_iban">Account Number (IBAN)</label>
            <div className={styles.inputWrap}>
              <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                account_balance
              </span>
              <input
                id="receiver_iban"
                type="text"
                placeholder="e.g. RO49AAAA1B31007593840000"
                value={form.receiver_iban}
                onChange={update('receiver_iban')}
                className={styles.input}
                required
                minLength={15}
              />
            </div>
          </div>

          <div className={styles.field}>
            <label htmlFor="description">Description</label>
            <div className={styles.inputWrap}>
              <span className={`material-symbols-outlined ${styles.inputIcon}`}>
                description
              </span>
              <input
                id="description"
                type="text"
                placeholder="What is this payment for?"
                value={form.description}
                onChange={update('description')}
                className={styles.input}
                maxLength={500}
              />
            </div>
          </div>

          <div className={styles.actions}>
            <button
              type="button"
              className={styles.btnGhost}
              onClick={() => navigate('/dashboard')}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={styles.btnPrimary}
              disabled={submitting || !account}
            >
              {submitting ? 'Submitting…' : 'Initiate Transfer'}
              <span className="material-symbols-outlined">arrow_forward</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
