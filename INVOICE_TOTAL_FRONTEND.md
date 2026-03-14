# Invoice total_price – auto-calculate in frontend

The backend **always** computes `total_price = subtotal - discount` and saves it. You can still show the total updating live in the form.

## Formula

```text
total_price = subtotal - discount
```

## React example (controlled inputs)

When the user changes `subtotal` or `discount`, update state and derive `total_price` for display (and send all three to the API; backend will overwrite `total_price`).

```jsx
import { useState, useMemo } from 'react';

function InvoiceForm() {
  const [subtotal, setSubtotal] = useState('');
  const [discount, setDiscount] = useState('');

  // Auto-calculated total for display (subtotal - discount)
  const totalPrice = useMemo(() => {
    const sub = parseFloat(subtotal) || 0;
    const disc = parseFloat(discount) || 0;
    return Math.max(0, sub - disc).toFixed(2);
  }, [subtotal, discount]);

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('/api/invoices/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subtotal: subtotal || '0',
        discount: discount || '0',
        total_price: totalPrice, // optional; backend recalculates
        // ...other fields: client_name, invoice_date, etc.
      }),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="number"
        step="0.01"
        value={subtotal}
        onChange={(e) => setSubtotal(e.target.value)}
        placeholder="Subtotal"
      />
      <input
        type="number"
        step="0.01"
        value={discount}
        onChange={(e) => setDiscount(e.target.value)}
        placeholder="Discount"
      />
      <input type="text" value={totalPrice} readOnly placeholder="Total (auto)" />
      <button type="submit">Save</button>
    </form>
  );
}
```

## Vanilla JS (single form)

```html
<input type="number" step="0.01" id="subtotal" placeholder="Subtotal" />
<input type="number" step="0.01" id="discount" placeholder="Discount" />
<input type="text" id="total_price" readonly placeholder="Total (auto)" />

<script>
  function updateTotal() {
    const sub = parseFloat(document.getElementById('subtotal').value) || 0;
    const disc = parseFloat(document.getElementById('discount').value) || 0;
    document.getElementById('total_price').value = Math.max(0, sub - disc).toFixed(2);
  }
  document.getElementById('subtotal').addEventListener('input', updateTotal);
  document.getElementById('discount').addEventListener('input', updateTotal);
</script>
```

## Summary

- **Backend**: `total_price` is computed on save as `subtotal - discount` and is read-only in the API.
- **Frontend**: Use `subtotal` and `discount` in state, compute `total_price` for the field (e.g. `subtotal - discount`) and show it in a read-only input so it updates automatically when the user edits the other prices.
