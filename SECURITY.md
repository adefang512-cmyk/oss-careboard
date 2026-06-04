# Security Policy

## Supported versions

Security fixes are applied to the latest release.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose tokens,
private repository metadata, or another user's information. Contact the
maintainer privately through the method listed on their GitHub profile.

Include the affected version, reproduction steps, likely impact, and any
suggested mitigation. Please allow a reasonable period for investigation
before public disclosure.

## Token safety

OSS Careboard only needs read access. Use the narrowest token permissions
available, prefer short-lived tokens, and never commit a token or snapshot from
a private repository.

OSS Careboard does not use OpenAI APIs, paid model APIs, or metered third-party
services. Do not add service credentials to a workflow unless a future feature
clearly documents why they are needed and how costs are controlled.
