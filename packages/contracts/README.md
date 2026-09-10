# `@afrosite/contracts`

Frontière typée Afrosite. Le schéma `Blueprint JSON` est défini **une fois** ici.

- Zod : `src/blueprint.schema.ts`
- Exemples valides : `src/examples.ts` (commerce, restaurant, services)
- Miroir Pydantic : `python/afrosite_contracts/blueprint.py`

Toute modification = PR + accord Souraka. Zod et Pydantic doivent rester alignés.

```bash
# depuis packages/contracts (Node 22+)
pnpm install
pnpm check
```
