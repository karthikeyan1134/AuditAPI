# Version Pinning Recommendations

Based on breaking changes detected in monitored SDK changelogs.

## stripe

**Breaking changes detected in:** 22.1.0, 22.1.0, 22.1.0

### Python (`requirements.txt`)

```text
# Pin below breaking version until migration is complete
stripe<22.1.0
```

### Node.js (`package.json`)

```json
{
  "stripe": "<22.1.0"
}
```

**When to unpin:** After applying migration guides and testing thoroughly.
**Reason:** Breaking changes in 22.1.0 may affect your codebase.

---

## openai

**Breaking changes detected in:** 2.35.0, 2.35.0, 2.25.0

### Python (`requirements.txt`)

```text
# Pin below breaking version until migration is complete
openai<2.35.0
```

### Node.js (`package.json`)

```json
{
  "openai": "<2.35.0"
}
```

**When to unpin:** After applying migration guides and testing thoroughly.
**Reason:** Breaking changes in 2.35.0 may affect your codebase.

---

## twilio

**Breaking changes detected in:** T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned, T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned, T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned

### Python (`requirements.txt`)

```text
# Pin below breaking version until migration is complete
twilio<T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned
```

### Node.js (`package.json`)

```json
{
  "twilio": "<T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned"
}
```

**When to unpin:** After applying migration guides and testing thoroughly.
**Reason:** Breaking changes in T-Mobile A2P 10DLC Daily Limit Warning Error Codes 30025, 30026, and 30027 Being Decommissioned may affect your codebase.

---
