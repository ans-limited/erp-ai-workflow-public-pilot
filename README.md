# ERP AI Operating Standard v0.4 — isolated hosted pilot

Status: **DISPOSABLE PILOT ONLY — NOT ADOPTED**.

This repository contains a prototype risk-policy checker and an illustrative SQLite inventory/ledger module. Do not use as production accounting software or connect it to business repositories.

Run from repository root:

```sh
python -m unittest discover -s tests -v
```

The draft pull request triggers `unit-tests` and `risk-policy`. The risk-policy job compares the actual Git diff against the declared class in `.pilot/task.json`. For this bootstrap PR, class R3 is claimed because workflow and finance paths are introduced.

These prototype controls cannot establish source-design conformance, human Technical Accountable Reviewer authorization, or live branch protection. CODEOWNERS is advisory until branch rules require approvals. No production deployment is configured.

The standard remains unapproved. No merges or deployments are authorized.
