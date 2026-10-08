# Security and responsible disclosure

Living System v0.1 is an **experimental reference implementation**, not an authentication, access-control or secret-management product. The review tool records a reviewer name for provenance but **does not verify identity**. AI instructions do not enforce security boundaries.

**Do not put real credentials, personal records or confidential client content in this example repository.** Use a separate private environment for your own organisational data.

If you identify a vulnerability, please **do not post exploit details, tokens or sensitive data in a public issue**. Use GitHub's private reporting: open this repository's **Security** tab, go to **Advisories**, and choose **Report a vulnerability**. If that button is not available, open a public issue that asks only for a private reporting route and contains **no technical details**.

Public issues are suitable for non-sensitive errors, documentation mistakes and enhancement proposals. No fixed security response SLA is promised for this experimental v0.1.

## For maintainers

Immediately after making the repository public, and **before announcing the release**, enable private vulnerability reporting: **Settings → Advanced Security → Private vulnerability reporting → Enable** ([GitHub documentation](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository)). GitHub offers this feature for public repositories. Until it is enabled, reporters have no private channel.
