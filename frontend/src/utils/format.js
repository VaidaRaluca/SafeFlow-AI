export function formatCurrency(amount, currency = 'EUR', locale = 'en-US') {
  if (amount === null || amount === undefined || amount === '') return '—';
  const num = typeof amount === 'number' ? amount : Number(amount);
  if (Number.isNaN(num)) return '—';
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    }).format(num);
  } catch {
    return `${num.toFixed(2)} ${currency}`;
  }
}

export function formatDateTime(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function maskIban(iban) {
  if (!iban) return '';
  if (iban.length <= 8) return iban;
  return `${iban.slice(0, 4)} •••• ${iban.slice(-4)}`;
}
