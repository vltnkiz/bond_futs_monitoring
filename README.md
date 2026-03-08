## Calculations

### Notation

| Symbol | Meaning |
|--------|---------|
| $P^{\text{clean}}$ | Bond clean mid price |
| $P^{\text{dirty}}$ | Bond dirty price (clean + accrued interest) |
| $F$ | Futures mid price |
| $CF$ | Conversion factor of the bond for the future |
| $C$ | Annual coupon rate (as a decimal, e.g. 0.03 for 3%) |
| $r$ | Repo rate interpolated to the delivery date |
| $t_0$ | Today |
| $t_D$ | Delivery date of the future |
| $t_{\text{cpn}}$ | Next coupon date |
| $t_{\text{cpn}-1}$ | Last coupon date |

---

### Gross Basis

The gross basis measures the difference between the bond's current clean price and the price implied by the futures contract:

$$\text{Gross Basis} = P^{\text{clean}} - F \times CF$$

A positive gross basis means the bond is expensive relative to the future. The **cheapest-to-deliver (CTD)** bond is the one with the lowest gross basis.

> Prices should be expressed consistently (e.g. per 100 nominal). The futures price is quoted clean — accrued interest is excluded.

---

### Carry

Carry is the net income from holding the bond and financing it to delivery.

**Coupon Income** (ACT/ACT)

If the next coupon date falls *after* delivery (no coupon received before delivery):

$$\text{Coupon Income} = C \times \frac{(t_D - t_0)}{t_{\text{cpn}} - t_{\text{cpn}-1}}$$

If the next coupon date falls *on or before* delivery (coupon received before delivery):

$$\text{Coupon Income} = C + C \times \frac{(t_D - t_{\text{cpn}})}{t_{\text{cpn}} - t_{\text{cpn}-1}}$$

**Financing Cost** (ACT/365)

$$\text{Financing Cost} = P^{\text{dirty}} \times r \times \frac{(t_D - t_0)}{365}$$

where $r$ is obtained by interpolating the repo curve at $t_D$.

**Carry**

$$\text{Carry} = \text{Coupon Income} - \text{Financing Cost}$$

---

### Net Basis

$$\boxed{\text{Net Basis} = \text{Gross Basis} - \text{Carry}}$$

Equivalently:

$$\text{Net Basis} = \left(P^{\text{clean}} - F \times CF\right) - \left(\text{Coupon Income} - \text{Financing Cost}\right)$$

A **negative net basis** means it is profitable to buy the bond and deliver it via the future (cash-and-carry arbitrage). The CTD bond is the one with the most negative net basis.