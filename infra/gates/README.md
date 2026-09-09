"""OPA gate policies for Afrosite.

Six gates (G1–G6) live in `policies.rego`. Role → route matrix in
`permissions.yaml`. Evaluate with Open Policy Agent:

    opa test infra/gates -v
    opa eval -d infra/gates/policies.rego -i input.json 'data.afrosite.gates.allow'
"""
