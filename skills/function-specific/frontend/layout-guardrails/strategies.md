name: layout-guardrails
rules:
  - id: RG-01-container-scoped-z
    severity: error
    selector: "[data-scope],[data-z-layer]"
    assert: max(z-index) <= scope_cap[scope]
  - id: RG-02-parent-overflow-clip
    severity: error
    selector: "[aria-overflow]"
    assert: floating_parents must use position-fixed OR add padding
  - id: RG-03-portal-restack
    severity: warn
    selector: "[data-portal]"
    assert: re-applies stacking-context after mount
scope_caps:
  global: 50
  page: 30
  entity: 20
  sub-entity: 10
