# 100 additional candidate research jobs for a crypto market autoresearcher

## Scope and status

These jobs expand the market and trading scope of the supplied idea list. “Additional” means the mechanism or question is distinct from that list; it does not claim priority over published work. External literature novelty is **unverified**. This is an ideation docket, not evidence, an approved result, or a change to the repository’s ECDLP research ledger.

The current autoresearcher repository is focused on cryptanalysis. This file is deliberately isolated as a market-research proposal and should only be adopted if that scope is intended for the project.

Each item states a falsifiable hypothesis and a first comparison. Apply the common data, execution, validation, and reporting contract below to every job. Reject a candidate if it fails its pre-registered out-of-sample test; do not promote it from an in-sample result.

## Portfolio construction and capital allocation

1. **Signal half-life turnover allocator** — Hypothesis: assigning each signal a turnover budget based on its measured decay produces better net portfolio utility than equal turnover caps. Test on point-in-time signals with identical assets, gross exposure, and fees; compare net utility and realized turnover walk-forward.
2. **Tail-correlation risk budget** — Hypothesis: sizing assets by conditional co-crash contribution controls portfolio drawdowns better than covariance-only risk parity. Compare both methods on frozen stress windows and untouched forward periods; measure expected shortfall and return sacrificed.
3. **Settlement-aware cash reserve** — Hypothesis: reserving capital according to observed withdrawal and settlement latency prevents forced deleveraging during venue stress. Compare latency-based reserves with a fixed cash fraction; measure missed fills, liquidation events, and return on deployable capital.
4. **Counterparty-diversified stablecoin sleeve** — Hypothesis: splitting idle quote collateral across issuers and redemption paths reduces portfolio tail loss at a modest carry cost. Compare with a single-stablecoin sleeve under historical and replayed issuer/venue outages.
5. **Collateral shadow-price allocator** — Hypothesis: treating collateral lockup and haircut as an asset-specific capital cost changes the optimal venue allocation. Compare capital-aware weights with notional-only weights; score net return per dollar of eligible collateral.
6. **Correlated liquidation exposure cap** — Hypothesis: limiting positions that share the same likely liquidation trigger reduces portfolio drawdowns beyond ordinary correlation limits. Compare trigger-cluster limits with volatility and correlation caps using historical stress replays.
7. **Drawdown-recovery policy** — Hypothesis: a pre-specified exposure ramp after drawdowns recovers risk-adjusted returns faster than an immediate reset to target leverage. Compare several fixed, causal ramps against a fixed-volatility baseline; measure recovery time and worst additional loss.
8. **Risk budget by executable depth** — Hypothesis: allocating risk from depth that could actually be executed at the strategy’s order size beats market-cap or volume weighting. Compare sizing rules after full depth-walk costs and capacity haircuts.
9. **Hedge-bleed-adjusted strategy ranking** — Hypothesis: ranking strategies by residual return after hedge basis, borrow, and collateral costs changes which sleeves deserve capital. Compare raw Sharpe allocation with fully funded net-return allocation; report turnover and drawdown.
10. **Capital reservation for concurrent signals** — Hypothesis: reserving capital for correlated strategies before they trigger reduces forced overlap and slippage. Replay simultaneous signal arrivals with a shared capital budget; compare the scheduler with independent strategy sizing.

## Crypto-linked public securities and capital structures

11. **Digital-asset-treasury value per diluted share** — Hypothesis: changes in digital assets held per fully diluted share explain returns better than headline treasury holdings. Compare the share-adjusted measure with spot exposure and NAV premium across reporting dates.
12. **Treasury premium financing loop** — Hypothesis: a high premium to net asset value predicts future equity issuance and subsequent premium compression. Test event-time forecasts around issuance filings; control for asset returns and dilution.
13. **ATM issuance flow detector** — Hypothesis: disclosed at-the-market sales create a predictable return drag before issuance totals appear in quarterly filings. Compare public filing timestamps with volume, borrow, and price residuals; reject if the signal is not available in real time.
14. **Convertible reset hedge pressure** — Hypothesis: convertible notes with variable conversion terms create identifiable issuer-equity hedge flows that spill into the underlying crypto asset. Compare affected issuers with matched firms lacking reset clauses.
15. **Preferred-share carry versus treasury growth** — Hypothesis: high cash distributions on crypto-treasury preferreds are followed by changes in common-share financing or asset-sale behavior. Test total-return and dilution outcomes against fixed-income peers.
16. **Digital-asset debt maturity wall** — Hypothesis: debt due within a short refinancing window predicts asset sales or equity dilution beyond changes in asset prices. Build a point-in-time maturity panel and compare flagged issuers with matched controls.
17. **Treasury purchase funding-source effect** — Hypothesis: purchases funded by operating cash differ in persistence from purchases financed by new debt or equity. Classify announced and completed purchases by source; test subsequent asset holdings and issuer returns.
18. **Crypto proxy equity option spillover** — Hypothesis: dealer hedging in options on listed crypto proxies affects spot crypto near equity-market close. Compare spot returns and order flow on option-expiry and matched non-expiry days.
19. **Digital-asset index rebalance anticipation** — Hypothesis: predictable index eligibility and weight changes produce temporary demand before effective dates. Simulate historical rulebooks point-in-time and compare rebalance windows with synthetic non-constituents.
20. **Proxy-company capital raise arbitrage boundary** — Hypothesis: the expected dilution and hedge cost around announced offerings explains part of the gap between proxy equities and their crypto holdings. Test event returns after disclosure, excluding data unavailable at the timestamp.

## Mining, hardware, and energy economics

21. **Power-price-to-miner-sale transmission** — Hypothesis: local power-price spikes raise the probability that exposed miners sell newly mined assets. Link public miner locations, power prices, and attributable transfers; compare with miners on fixed-price power.
22. **Curtailment option value** — Hypothesis: miners with demand-response contracts have different downside exposure to power shocks than otherwise similar miners. Compare returns and production through high-price intervals, controlling for asset price and network difficulty.
23. **Used-ASIC price as capacity lead indicator** — Hypothesis: second-hand ASIC prices lead changes in marginal network capacity and miner profitability. Test whether resale indices forecast hashrate and difficulty changes beyond manufacturer delivery data.
24. **Fleet-efficiency break-even map** — Hypothesis: hardware-efficiency cohorts predict which miners become marginal sellers after energy or asset-price shocks. Estimate unit economics by machine vintage and validate against public production disclosures.
25. **Mining-pool payout policy and sell timing** — Hypothesis: payout frequency and payout asset influence the short-horizon timing of miner-originated exchange deposits. Compare pools with different payout policies while controlling for block rewards and fees.
26. **Fee-revenue dependence under congestion** — Hypothesis: miners whose revenue depends more on transaction fees respond differently to blockspace-demand shocks than subsidy-dependent miners. Test production, treasury transfers, and miner-equity returns across congestion regimes.
27. **Difficulty-adjustment supply elasticity** — Hypothesis: miner-originated sell pressure changes predictably after difficulty adjustments because marginal operators enter or exit. Compare post-adjustment periods with placebo dates and control for asset returns.
28. **Regional energy-basis exposure** — Hypothesis: regional electricity basis spreads explain differences in listed miner profitability and financing risk. Build a location-weighted basis index and test against public operating results.
29. **Hardware lead-time shock** — Hypothesis: long ASIC delivery delays change forward network-capacity expectations and miner-equity valuations before measured hashrate moves. Test manufacturer shipment notices against later difficulty and equity repricing.
30. **Grid-service revenue substitution** — Hypothesis: miners paid to curtail during grid stress have lower forced-sale risk than miners with no such contracts. Compare treasury movements and debt outcomes around independently recorded curtailment events.

## Exchange custody, solvency, and operating risk

31. **Proof-of-liabilities disclosure quality premium** — Hypothesis: independently verifiable liability coverage is associated with lower venue-specific liquidity discounts than reserve-only attestations. Score disclosures before outcomes and test spreads and withdrawal behavior around stress.
32. **Withdrawal queue as latent credit spread** — Hypothesis: queue age and completion rate predict venue-specific price discounts earlier than net exchange-flow aggregates. Compare queue-based signals with public reserve and order-book measures.
33. **Shared reserve-asset contagion map** — Hypothesis: venues and custodians with overlapping reserve assets transmit stress through common liquidation channels. Build only from disclosed exposures and test whether the map predicts cross-venue liquidity deterioration.
34. **Customer-asset segregation disclosure test** — Hypothesis: clear legal and operational segregation reduces venue-specific risk premia during market stress. Code policy changes point-in-time and compare affected venues with matched controls.
35. **Insurance-fund adequacy versus ADL risk** — Hypothesis: insurance resources relative to open obligations predict the probability of socialized losses or auto-deleveraging. Score each venue with published rules and stress-test against realized events.
36. **Margin-rule change repricing** — Hypothesis: changes to venue margin rules reprice affected instruments before aggregate open interest moves. Compare instruments with changed and unchanged risk tiers around effective timestamps.
37. **Withdrawal-halt reopening path** — Hypothesis: the order in which deposits, withdrawals, and trading resume predicts the persistence of venue-specific discounts. Build event studies with exchange and asset controls.
38. **Deposit-crediting latency penalty** — Hypothesis: slow or variable crediting times reduce executable arbitrage and widen local price gaps. Estimate the penalty from published status histories and matched periods of normal operation.
39. **Legal recovery haircut by venue structure** — Hypothesis: disclosed bankruptcy remoteness, jurisdiction, and custody arrangements explain variation in customer-recovery expectations priced into venue products. Use event studies and avoid inferring legal conclusions from price alone.
40. **Fiat-rail concentration risk score** — Hypothesis: dependence on a small number of banking partners predicts venue funding interruptions and local price dislocations. Test against dated partner disclosures and operational incident records.

## Margin, clearing, and collateral mechanics

41. **Stress-tested collateral haircuts** — Hypothesis: haircuts calibrated to joint asset and venue shocks reduce liquidation losses versus static exchange haircuts. Replay disclosed collateral rules on historical stress windows and compare shortfall per unit of capital.
42. **Cross-margin versus isolated-margin utilization** — Hypothesis: cross-margin improves capital efficiency in calm regimes but increases contagion loss in correlated shocks. Compare both policies on identical portfolios and liquidation rules.
43. **Collateral correlation break detector** — Hypothesis: correlations among posted collateral assets rise before margin shortfalls. Estimate online correlation-break alerts and compare lead time and false-alarm rate with volatility thresholds.
44. **Liquidation waterfall reconstruction** — Hypothesis: public execution traces can identify venue-specific liquidation priority and improve loss forecasts. Infer rules on past events, then test prospectively on held-out events.
45. **Auto-deleveraging rank estimator** — Hypothesis: public position and insurance data can approximate which accounts face ADL first. Validate predicted rank only against disclosed or observed ADL cases; reject if required private data is unavailable.
46. **Spot-margin recall shock** — Hypothesis: lender recalls create a distinct forced-cover pattern in spot markets that is not captured by perpetual funding. Compare recall notices and borrow availability with spot order flow.
47. **Settlement-obligation netting value** — Hypothesis: netting settlement obligations across instruments reduces the capital needed to maintain a hedge without increasing default exposure. Simulate venue rules and compare capital usage and worst-case shortfall.
48. **Margin headroom as execution constraint** — Hypothesis: order routers that price the loss of margin headroom avoid fills that trigger disproportionate liquidation risk. Compare headroom-aware and price-only routing in deterministic replay.
49. **Collateral substitution under stress** — Hypothesis: users substitute toward safer collateral before venue haircuts change, making collateral composition an early stress indicator. Test composition changes against later margin events.
50. **Cross-venue collateral portability value** — Hypothesis: transfer time and eligibility restrictions determine whether nominally hedged positions can remain hedged during stress. Simulate venue outages and report hedge-break probability and cost.

## Banking, payments, and fiat settlement

51. **Bank-wire cutoff premium** — Hypothesis: fiat wire cutoffs create recurring price or spread changes in venues with limited overnight funding. Compare cutoff windows against venues with continuous stablecoin settlement.
52. **ACH funding latency and retail order timing** — Hypothesis: funding-credit delays shift retail order arrival into predictable windows. Test with authorized account-level aggregate timing data or public processor timestamps, with privacy-preserving aggregation.
53. **Merchant stablecoin settlement retention** — Hypothesis: merchants that retain a portion of stablecoin receipts generate more persistent on-chain payment volume than immediate-conversion merchants. Test using opt-in processor cohorts and matched merchants.
54. **Remittance corridor conversion friction** — Hypothesis: corridor-specific conversion and cash-out costs explain stablecoin usage better than raw transfer counts. Measure end-to-end cost and retention in opt-in or public aggregate corridor data.
55. **Payroll payment cycle and household liquidity** — Hypothesis: crypto purchases funded around recurring payroll dates differ in persistence from one-off exchange deposits. Test only with consented, anonymized aggregates and compare post-payday retention.
56. **Treasury settlement use versus idle balances** — Hypothesis: stablecoins used for repeated commercial settlement have different velocity and redemption patterns from balances held as exchange collateral. Distinguish use with labeled, privacy-safe flows.
57. **Payment-processor conversion fee pass-through** — Hypothesis: processor fee changes alter merchant crypto acceptance and settlement choice. Run event studies around announced fee changes with unaffected processors as controls.
58. **Card-to-wallet funding delay** — Hypothesis: card-funded wallet credits cause a measurable execution and reversal-risk premium compared with settled bank or on-chain funding. Compare funding rails on authorized aggregate datasets.
59. **Capital-control access premium** — Hypothesis: local fiat access restrictions explain persistent crypto conversion spreads after controlling for global liquidity. Use lawful public exchange quotes and dated policy events; exclude restricted or unsafe execution routes.
60. **Reserve-duration sensitivity** — Hypothesis: stablecoin reserve duration changes the issuer’s rate sensitivity and secondary-market discount under rapid redemption. Test disclosed reserve composition against rate shocks and redemption data.

## Tax, accounting, and reporting calendars

61. **Tax-loss realization calendar** — Hypothesis: tax-driven selling is concentrated in assets with large unrealized losses and differs by jurisdictional tax-year end. Compare affected assets with matched assets and pre-register jurisdictions and dates.
62. **Tax-lot selection and rebound** — Hypothesis: high dispersion in investor cost basis predicts temporary selling followed by a measurable reversal around tax deadlines. Test with aggregate, privacy-safe cost-basis estimates and falsify against placebo dates.
63. **Fair-value accounting adoption** — Hypothesis: accounting-rule adoption changes the likelihood and timing of corporate crypto holdings. Compare adopters with matched non-adopters after adoption dates; separate announcements from actual purchases.
64. **Quarter-end crypto mark policy** — Hypothesis: disclosed valuation and custody policies predict quarter-end trading or balance-sheet adjustments by public holders. Use filing timestamps and compare with non-reporting windows.
65. **Tax treatment change sensitivity** — Hypothesis: assets with more taxable on-chain usage react differently to tax guidance than passive holdings. Build exposure from documented use cases and test event-time returns against controls.
66. **Fund reporting window dressing** — Hypothesis: reporting-date incentives affect disclosed holdings of liquid crypto proxies even when underlying economic exposure is unchanged. Compare reported positions, derivatives, and post-report reversals.
67. **Regulatory eligibility and venue migration** — Hypothesis: changes in investor or product eligibility shift volume across venues before they change total asset demand. Study dated rule changes with matched assets and venue share as the outcome.
68. **Audit-cycle custody friction** — Hypothesis: audit evidence requirements create predictable operational delays in moving crypto holdings near reporting dates. Test only from disclosed corporate/venue records, not inferred private positions.
69. **Reserve attestation timing gap** — Hypothesis: long gaps between reserve attestations correlate with wider venue risk discounts than frequent independent updates. Compare disclosure cadence while controlling for venue size and liquidity.
70. **Public-company crypto disclosure completeness** — Hypothesis: standardized disclosures reduce uncertainty discounts around reported holdings. Score filings before returns and test whether completeness improves forecast calibration beyond holdings size.

## Tokenized assets and on-chain capital markets

71. **Tokenized Treasury weekend redemption discount** — Hypothesis: tokenized cash-like assets trade at larger weekend discounts when redemption is unavailable. Compare token prices with contemporaneous NAV proxies and matched weekday sessions.
72. **Transfer-restricted asset liquidity haircut** — Hypothesis: investor eligibility and transfer restrictions predict secondary-market discounts beyond asset credit risk. Measure executable spreads by restriction class and test out of sample.
73. **Composable collateral concentration penalty** — Hypothesis: tokenized assets reused across multiple protocols create hidden common liquidation exposure. Map public collateral paths and compare stressed losses with single-use collateral.
74. **On-chain fund flow versus NAV flow** — Hypothesis: subscription and redemption transactions forecast tokenized fund liquidity more accurately than wallet transfer volume. Compare both against official shares outstanding and NAV updates.
75. **Oracle holiday mark staleness** — Hypothesis: non-trading-day oracle marks create measurable risk premiums in tokenized securities and funds. Compare price deviations during market holidays with assets using live redemption prices.
76. **Tokenized credit repayment cycle** — Hypothesis: payment and redemption timing of on-chain credit products predicts secondary-market discount changes near maturity. Test by vintage and disclosed payment schedule.
77. **On-chain credit maturity wall** — Hypothesis: clustered loan maturities create predictable liquidity needs in collateral tokens even without borrower distress. Compare maturity concentration with subsequent market depth and realized slippage.
78. **Commodity-token inventory backing lag** — Hypothesis: verification and delivery lags explain discounts in commodity-backed tokens. Compare tokens by independently documented redemption time and custody process.
79. **Permissioned-token eligibility churn** — Hypothesis: changes in eligible investor sets affect liquidity and price dispersion even when underlying NAV is stable. Test dated allowlist policy changes using public execution data.
80. **Tokenized fund settlement atomicity** — Hypothesis: atomic delivery-versus-payment settlement lowers failed-trade and price-gap rates versus asynchronous settlement. Compare product designs on matched transaction sizes and counterparties.

## Investor behavior and capital-flow mechanisms

81. **Mandate-bound investor exposure ceiling** — Hypothesis: institutional allocation limits create nonlinear flows when crypto weight approaches a disclosed mandate cap. Test at public portfolio reporting thresholds and compare with unconstrained funds.
82. **Treasury-company index-weight feedback** — Hypothesis: rising index weight in digital-asset treasury companies creates feedback between passive flows and treasury financing capacity. Model rule-based index flows and test with matched issuers.
83. **Custodian-supported versus unsupported demand** — Hypothesis: investor demand shifts toward assets supported by their mandated custodians, independent of chain activity. Test asset-level listing or custody additions against unaffected assets.
84. **Crypto balance-sheet disclosure surprise** — Hypothesis: unexpected changes in institutional digital-asset holdings move related assets more when disclosure is hard to infer from prior filings. Score surprise point-in-time and test against expected holdings.
85. **DAO treasury spending and token float** — Hypothesis: recurring treasury disbursements to service providers affect token float differently from one-time grants. Link public proposals to vesting and wallet movements; measure realized sell-through.
86. **Pension/insurance allocation constraint** — Hypothesis: changes in documented investment policy predict slow-moving demand for regulated crypto products. Compare institutions before and after policy changes using public filings and product flows.
87. **Crypto-lender collateral mark cycles** — Hypothesis: lenders’ collateral valuation cadence causes lagged margin tightening and asset sales. Use disclosed valuation rules and dated margin notices; compare with market-price-only controls.
88. **Yield-product redemption queue premium** — Hypothesis: redemption queues on yield products create a tradable discount distinct from asset depeg risk. Test queue age against product NAV and executable exit prices.
89. **Corporate cash allocation substitution** — Hypothesis: changes in short-term cash yields alter corporate allocation between cash instruments and crypto holdings with measurable lag. Compare treasury disclosures across firms and rates regimes.
90. **Regional institutional access window** — Hypothesis: local product approval and custodian availability shift demand into specific trading sessions. Test dated access changes against session-level volume share and unaffected regions.

## Execution systems and deployability

91. **Fee-tier hysteresis controller** — Hypothesis: choosing whether to maintain or abandon a venue fee tier by expected future turnover beats a rule based only on the next order’s fee. Replay real tier schedules; score total fees, rebates, and adverse selection.
92. **Inventory-location-aware routing** — Hypothesis: routing based on pre-positioned inventory and transfer cost beats best-quote routing when balances are fragmented across venues. Compare fill quality plus post-trade rebalancing cost.
93. **One-leg-fill hedge policy** — Hypothesis: a state-aware hedge after partial execution reduces unhedged tail loss versus immediate full hedge. Replay synchronized fills with latency and compare hedge cost and maximum exposure.
94. **Atomic versus asynchronous hedge selection** — Hypothesis: the value of atomic execution depends on volatility and settlement risk, not just quoted spread. Compare atomic routes with sequential routes under matched size and outage replay.
95. **Balance-sheet-aware order sizing** — Hypothesis: sizing from available borrow, collateral, and venue limits avoids rejected orders and liquidation risk better than target-notional sizing. Measure realized fill rate and net return.
96. **Clock-skew execution robustness** — Hypothesis: strategies that survive realistic timestamp uncertainty retain more live alpha than those ranked on idealized synchronized feeds. Perturb feed clocks using measured venue error distributions.
97. **Queue reset after venue reconnect** — Hypothesis: reconnecting after network interruption loses queue priority often enough to change maker-versus-taker choice. Measure reconnect fill hazards against uninterrupted sessions.
98. **Transfer-failure reserve policy** — Hypothesis: reserving enough local inventory to survive a failed transfer improves hedge completion and reduces emergency execution cost. Stress-test observed transfer failure and delay distributions.
99. **Order minimum and tick-size capacity cliff** — Hypothesis: discrete minimum size and price increments create sharp capacity limits that continuous slippage models miss. Sweep order sizes around venue constraints and compare predicted with realized shortfall.
100. **Live-shadow deployment gate** — Hypothesis: a shadow-execution period with frozen predictions catches venue-state failures that historical backtests miss. Compare shadow fills and risk events with the backtest forecast; require pre-set calibration bounds before any live promotion.

## Required evaluation contract

Every job must produce:

- A falsifiable hypothesis, causal mechanism, and named scope.
- Required datasets, point-in-time timestamps, data lineage, and explicit universe/exclusion rules.
- A simple baseline and a cost model including fees, spread, slippage, funding, borrow, gas, transfer, and financing costs where applicable.
- Chain reorganization and finality handling for on-chain observations; token delistings, migrations, and symbol changes handled without survivorship bias.
- Walk-forward results with untouched time periods, pre-registered controls, and placebo or falsification tests.
- Capacity and turnover estimates at realistic order sizes, plus stress scenarios for venue, custodian, settlement, and data outages.
- Reproducible code, configuration, seeds, raw outputs, timestamps, and data-source versioning.
- A final verdict: **reject**, **monitor**, or **promote**. Promotion requires replicated out-of-sample evidence and a documented execution path; a high backtest Sharpe alone is insufficient.

Before any item becomes a canonical research hypothesis, compare it against the project’s existing corpus and relevant published work. Until that check is recorded, set novelty status to **unverified**.
