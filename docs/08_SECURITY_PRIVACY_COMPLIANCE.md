# 08 — Security, Privacy, Market-Data and Regulatory Compliance

**Release-blocking review required. This document is an engineering checklist, not legal advice.**

## 1. Market-data licence

The NSE Data Sharing & Usage Policy states that permitted use, handling and redistribution are governed by the relevant agreement and that redistribution is not permitted except as agreed. Kite Connect's current published terms state that its live market data cannot be displayed to the public at large and restrict redistribution. These examples demonstrate why an API being technically accessible does not itself grant commercial display rights.

Before production, obtain a provider/exchange agreement covering:

- Live/delayed/historical data and all fields used (price, volume, OI, identifiers and indices).
- Public or subscriber display, derived indicators/scores, screenshots and board snapshots.
- User count, devices, geographic restrictions, caching, persistence, retention, and deletion.
- Commercial/subscriber fees, audit/reporting requirements, attribution, and provider SLA.
- Permission to use the data in replay/backtest outputs or publicly reported metrics.

Do not publish live or derived market output to public users until the contract has been reviewed and written approval recorded. A local/private prototype may use a source only for purposes allowed by its current terms.

## 2. Indian securities-law review

SEBI's Research Analyst Regulations and related guidelines/circulars are current and have been updated over time; SEBI published a Research Analyst Master Circular dated 6 February 2026 and 2025 guidance/FAQs. A paid product that ranks stocks and presents directional scores/zones may require a fact-specific classification review. A disclaimer or the phrase “analytics tool” alone does not determine regulatory status.

Before public launch or accepting payment, qualified Indian securities counsel must review:

- Exact user-facing output (rankings, score bands, chart zones, alerts and any sector/index bias).
- Marketing wording, educational content, testimonials and performance claims.
- Whether the service could be treated as research/analysis, investment advice, or another regulated activity.
- If registration, exchange approvals, notices, standardized terms, conflict disclosures, recordkeeping, or other obligations apply.
- Community moderation and any communications by founders, employees, moderators or users.

Record the lawyer's written view and any required changes as a release artifact. Re-review whenever product scope changes to include recommendations, personalization, broker integration, or order execution.

## 3. Data protection and consumer requirements

India's Digital Personal Data Protection Rules, 2025 were published by MeitY with a staged enforcement timeline. Before launch, verify the then-current Act/Rules commencement dates and any amendments/corrigenda rather than assuming every provision commenced simultaneously.

Engineering baseline:

- Collect only necessary personal data and explain each purpose.
- Record required notices/consents and maintain a workable consent/withdrawal flow where applicable.
- Provide a privacy policy, contact/grievance channel, data access/correction/deletion workflow as legally required, and a documented retention schedule.
- Protect account, payment, device/session and journal data; limit staff access to personal journal entries.
- Encrypt data in transit and at rest; protect backups; use least-privilege access.
- Do not put personal data, access tokens, or secrets in application logs or analytics events.
- Establish procedures for suspected breaches, vendor incidents, data-subject requests and account deletion.
- Obtain a qualified review of GST, invoices, refund/cancellation wording, automatic renewal and consumer-protection obligations before collecting payments.

## 4. Authentication and session controls

- Verify Google OAuth/OIDC identity tokens server-side; never trust a client-supplied email address alone.
- Issue a secure, HTTP-only, same-site session cookie with short enough expiry/revocation controls for the risk.
- Use CSRF protection on state-changing endpoints where cookie authentication is used.
- Rate-limit authentication and OTP endpoints; protect against account enumeration.
- Use a provider for email/phone OTP only after its security, consent and delivery model is documented.
- Device limits should be transparent and revocable. Avoid covert fingerprinting.
- Use role-based authorization for owner, support and content editor. Require strong authentication for admin users.

## 5. Payments

- Store money in integer minor units or an explicit decimal type.
- Verify webhook signatures on the server against the raw body.
- Make webhook processing idempotent and handle duplicate/out-of-order delivery.
- Unlock access only after verified provider confirmation.
- Reconcile provider records against application records.
- Keep secrets in deployment secret storage, never the client bundle or repository.
- Clearly define plan term, renewal, cancellation, taxes, invoice and refund behavior after accounting/legal review.

## 6. Application and infrastructure security

- HTTPS everywhere; HSTS in production.
- Input validation, parameterized SQL, output encoding, and a restrictive Content Security Policy.
- Rate limiting at the edge and at sensitive API routes.
- CORS restricted to required origins.
- Admin audit log, dependency scanning, secret scanning, vulnerability updates and periodic access review.
- Separate dev/staging/production credentials and databases.
- Backups with tested restore procedure; encryption and limited access.
- Logs use request IDs and safe error codes; redact tokens, payment details and personal data.
- A support “view as user” function, if ever built, must be read-only, audited and permission-gated.

## 7. Trading-risk and marketing safeguards

- Show a clear, counsel-approved risk disclosure in the app and marketing site.
- Do not promise returns, hit rate, accuracy or consistent profits.
- Do not cherry-pick only winning examples. Any performance statistics must state sample, methodology, fees/slippage assumptions, test periods, known limitations and whether results are simulated.
- Testimonials must be genuine, documented and used with informed permission.
- Do not imply exchange, broker or regulator endorsement.
- Do not describe detected zones as proof of institutional orders or actual resting stops.
- The user takes any trading action independently outside ZoneScan.

## 8. Launch checklist

- [ ] Written data-provider permission and cost quote approved.
- [ ] Legal counsel's written classification/recommendations received and implemented.
- [ ] Current DPDP Act/Rules commencement and privacy obligations checked.
- [ ] Approved terms, privacy, refund/cancellation, disclosures and risk warning published.
- [ ] Payment provider merchant approval, test results and reconciliation process complete.
- [ ] Security review, access-control tests, backup/restore drill and incident contact list complete.
- [ ] Performance claims, testimonials, logos and all marketing reviewed.
- [ ] Paper-trading/replay period and algorithm report signed off.
