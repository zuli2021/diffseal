# COMMERCIAL_RELEASE_POLICY

Status: Closed Decision

## Release And Launch

Release is not launch.
Public publication requires explicit owner authorization.
No public namespace change is authorized without explicit governance.

## Frozen Identities

- Product identity: `DiffSeal`
- CLI identity: `diffseal`
- Python package identity: `diffseal`
- Repository identity: `diffseal`
- GitHub Action identity: `DiffSeal`

Repository or Action renaming after adoption MUST be treated as a compatibility-breaking distribution concern.

## Licensing And Delivery

- Community is Apache-2.0.
- Pro is proprietary.
- Initial founding experiment price is `$19` one-time.
- Polar is the primary payment and delivery candidate.
- Initial Pro delivery SHOULD be a versioned wheel and/or ZIP through the merchant of record.
- No runtime DRM or license server.
- No mandatory telemetry.

## Distribution Surfaces

Planned technical distribution surfaces include GitHub repository, GitHub Releases, PyPI, GitHub Actions Marketplace, product documentation, and direct checkout artifacts.

GitHub availability alone MUST NOT be interpreted as launch.

## Launch Channels And Assets

Intentional launch SHOULD use qualified external distribution such as targeted developer outreach, a technical demonstration or article, an appropriate technical community, and Product Hunt only if launch assets justify it.

Required launch assets include usable product documentation, a demo, install guidance, and the simple launch worksheet needed for the initial experiment.

## 14-Day Funnel

Funnel:

```text
qualified exposure
    ->
product-page visit
    ->
Community install
    ->
successful first run
    ->
repeated use / Action use
    ->
Pro interest
    ->
checkout
    ->
purchase
    ->
successful Pro use
```

Important distinctions:

- GitHub view is not a qualified visitor.
- download is not activation.
- install is not successful first run.
- Community use is not Pro interest.
- checkout start is not purchase.
- purchase is not successful Pro activation.

Activation means a successful first run of the Community product with usable evidence output.

## Metrics And Experiment Logic

The first experiment is a 14-day manual worksheet, not analytics infrastructure.

Suggested worksheet fields:

- date
- source
- qualified
- installed
- first_run
- repeated_use
- pro_interest
- checkout
- purchase
- feedback

The initial price MUST remain fixed during the first experiment.

Continue, reposition, or pivot decisions SHOULD be based on qualified traffic, activated users, positioning attempts, and real willingness-to-pay evidence rather than raw GitHub traffic.

## Constraints

- No compliance claims.
- No public namespace changes without explicit governance.
- Public publication remains owner-gated.
