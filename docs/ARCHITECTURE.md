# ARCHITECTURE

Status: Closed Decision

## Architecture Style

DiffSeal uses a small modular monolith.

## Responsibility Boundaries

- Core models, configuration, evaluation, and execution remain in one Python package boundary.
- Collectors normalize raw tool execution into normalized check results.
- Reporters emit canonical JSON first and derived Markdown second.
- The CLI is the local entrypoint over the same core.
- The GitHub Action MUST remain a thin adapter over the same CLI and core logic.

## Conceptual Module Layout

```text
diffseal/
    models.py
    config.py
    run.py
    evaluate.py

    collectors/
        python.py

    reporters/
        json.py
        markdown.py

    cli.py

action/
    action.yml
```

The exact packaging layout MAY be refined later if Python packaging conventions require it, but the responsibility boundaries MUST remain intact.

## Execution Flow

```text
raw tool execution
    ->
normalized CheckResult
    ->
EvidenceBundle
    ->
evaluation
    ->
GateDecision
    ->
canonical JSON
    ->
derived Markdown
```

## Collector Boundary

Collectors MUST focus on tool invocation and normalization. They MUST NOT define separate gate policy semantics outside the shared evaluation path.

## Action Boundary

The GitHub Action MUST remain thin and MUST NOT duplicate business logic in Action YAML.

## Community And Pro Boundary

- Community core is the base product.
- Pro extends Community.
- Community MUST NOT depend on Pro.
- Pro MUST NOT duplicate the core engine.

## Guardrails

- No generic plugin framework.
- No backend, database, or SaaS architecture.
- New abstractions SHOULD be introduced only when a real second implementation or external boundary requires them.
