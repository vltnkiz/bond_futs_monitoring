# Bond Futures Gross & Net Basis Monitor — Implementation Plan

**Scope:** All FGBL expiries simultaneously (one `TickStateStore` per expiry)
**Basis:** Gross + Net simultaneously
**Latency:** Async `queue.Queue` between feed thread and engine
**Output:** Persist results to file/DB

---

## Step 1 — Fix Existing Bugs

- Fix `bidszie` typo → `bidsize` in `market_data_feed/core/models/tick.py`
- Change `return NotImplementedError` → `raise NotImplementedError()` in `market_data_feed/core/ports/market_data_feed.py`
- Move `__instruments_subscribed` and `__fields_subscribed` from class-level to instance-level `__init__` in `market_data_feed/adapters/market_data_feed/lseg_market_data_feed.py`
- Fix `datetime.datetime.now()` → `datetime.datetime.now(tz=datetime.timezone.utc)` in the same file
- Fix `TickStateStore._gross_basis` from a single `float` to a `dict[str, float]` (per ISIN) in `calculation_engine/tick_state_storage.py`
- Fix `GrossBasisResult` import in `tick_state_storage.py` — currently imported from `gross_basis_calculation_engine`, but defined in `models`

---

## Step 2 — Add RIC Field to Bond Model

- Add `RIC: Optional[str]` to `static_data_loader/core/models/Bond.py` including `to_dict`/`from_dict`
- Populate it in the static data loader via LSEG `GOV_CORP_INSTRUMENTS` view (ISIN → RIC lookup)
- This runs once at definition-update time, not during live monitoring

---

## Step 3 — Build a `TickRouter` (the Missing Bridge)

New file: `market_data_feed/core/tick_router.py`

- Constructed with a `dict[str, str]` (`ric → isin`) for bonds and a `dict[str, str]` (`ric → contract_symbol`) for futures
- Single method: `route(tick: Tick)` → looks up the RIC and dispatches to the correct `TickStateStore` instance (`update_bond` or `update_futures`)
- Lives in the application/wiring layer — it is the adapter between the feed abstraction and the calculation engine abstraction
- A bond tick fans out to **all** stores that contain that ISIN; a futures tick routes only to the matching contract's store

---

## Step 4 — Scale to Multiple Contracts

- At startup, iterate `FutureDefinition` for all `FGBL*` contracts
- Instantiate one `TickStateStore` per contract (same `DeliverableBasket`, different `FuturesContract(ric=...)`)
- `TickRouter` holds the map of all stores and routes accordingly

---

## Step 5 — Async Queue Between Feed and Engine

- LSEG callbacks write `Tick` objects into a `queue.Queue` (thread-safe, no asyncio)
- A separate consumer thread reads from the queue and calls `tick_router.route(tick)`
- Decouples LSEG network thread from computation; avoids blocking the feed on slow calculations
- **Rationale for `queue.Queue` over `asyncio`:** LSEG uses threads internally, not coroutines; mixing concurrency models would add complexity with no benefit

---

## Step 6 — Build a `NetBasisEngine`

New component: `calculation_engine/net_basis_calculation_engine.py`

**Formula:**
```
net_basis = gross_basis - carry
carry = (clean_price × repo_rate × days_to_delivery / 360) - accrued_interest
```

- New frozen dataclass `NetBasisInput`: all fields of `BasisCalcInput` plus `coupon_rate`, `maturity_date`, `day_count_conv`, `repo_rate`, `delivery_date`
- New class `NetBasisEngine`: same subscriber pattern as `GrossBasisEngine`, receives a `GrossBasisResult` + bond static data enrichment
- Accrued interest: standard ACT/ACT calculation using coupon rate and last/next coupon dates derived from maturity
- Repo rate: configurable `repo_rate_map: dict[str, float]` passed at construction; easy to swap with a live source later via a new port
- New result dataclass `NetBasisResult`: all `GrossBasisResult` fields plus `net_basis`, `accrued_interest`, `carry`, `repo_rate`

---

## Step 7 — Build the Result State Store

New module: `tick_state_storage/` (currently an empty directory)

- `ResultStateStore` holds the latest `NetBasisResult` keyed by `(isin, contract_symbol)`
- Separate from `TickStateStore` (which holds live bid/ask/mid prices) — this stores computed outputs
- Methods: `update(result: NetBasisResult)`, `get_all() → list[NetBasisResult]`
- Subscribed to `NetBasisEngine` output

---

## Step 8 — Add Persistence

New port: `ResultWriter` ABC with `write(result: NetBasisResult) → None`

Adapter options (pick one or both):
- `CSVResultWriter`: appends a row per update to a timestamped CSV file
- `SQLiteResultWriter`: inserts into a local SQLite DB

Each row captures: `timestamp`, `isin`, `contract_symbol`, `gross_basis`, `net_basis`, `bond_mid`, `futures_mid`, `conversion_factor`, `accrued_interest`, `carry`, `repo_rate`

---

## Step 9 — Wire `main.py`

```python
# Pseudocode outline
bond_def = BondDefinition("data/portfolios/bond_definition.json")
future_def = FutureDefinition("data/portfolios/future_definition.json")

ric_to_isin = {bond.RIC: bond.ISIN for bond in bond_def.get_all_bonds() if bond.RIC}
ric_to_contract = {future.ric: future.ContractSymbol for future in future_def.get_all_futures()}

stores: dict[str, TickStateStore] = {}
for future in future_def.get_all_futures():
    if not future.ContractSymbol.startswith("FGBL"):
        continue
    basket = build_deliverable_basket(future, bond_def)
    contract = FuturesContract(ric=future.ric)
    store = TickStateStore(basket, contract)
    gross_engine = GrossBasisEngine()
    net_engine = NetBasisEngine(bond_def, repo_rate_map={...})
    result_store = ResultStateStore()
    writer = CSVResultWriter("data/results/net_basis.csv")
    store.subscribe(gross_engine.on_calc_input)
    gross_engine.subscribe(net_engine.on_gross_basis_result)
    net_engine.subscribe(result_store.update)
    net_engine.subscribe(writer.write)
    stores[future.ContractSymbol] = store

tick_queue = queue.Queue()
router = TickRouter(ric_to_isin=ric_to_isin, ric_to_contract=ric_to_contract, stores=stores)

consumer_thread = threading.Thread(target=consume, args=(tick_queue, router), daemon=True)
consumer_thread.start()

all_rics = list(ric_to_isin.keys()) + list(ric_to_contract.keys())
feed = LSEGMarketDataFeed()
feed.add_instruments(all_rics)
feed.start(on_tick=tick_queue.put)
```

---

## Verification Plan

1. **Unit tests** for each new component in isolation (extend existing pattern in `calculation_engine/test.py`)
2. **Integration smoke test**: replay a manual tick sequence, verify gross and net basis match hand-calculated values
3. **Live test**: run `main.py`, confirm results are written to file and update correctly on each tick

---

## Open Questions / Future Work

- Repo rate source: hardcoded map → configurable file → live repo rate feed (same ports pattern)
- Extend `NotionalValue`/`TickValue` population to all product families beyond FGBL
- Add a `FutureDefinition` filename consistency fix (`futures_definition.json` vs `future_definition.json`)
- Terminal UI (noted in `notes.txt`): `rich` live table refreshed on each `ResultStateStore.update()`
- Logging: replace all `print` with `logging` (noted in `notes.txt`)
- Handle partial ticks: LSEG may send an update with only bid or only ask — current `update_bond` logic already handles this correctly (only overwrites non-None values)
