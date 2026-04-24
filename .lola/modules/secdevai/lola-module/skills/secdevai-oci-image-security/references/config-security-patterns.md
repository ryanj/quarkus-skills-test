# Configuration Security Patterns

Common patterns observed in OCI container image security analysis. Load this file during configuration security analysis steps.

---

## Pattern 1: Default Service Credentials with No Enforcement Mechanism

**Risk:** Services that ship with default credentials (empty passwords, well-known defaults) and do not enforce credential rotation on first use create a persistent authentication bypass condition.

**How to detect:**
- Search entrypoint scripts and config files for default credential patterns:
  ```
  grep -rE "(password|passwd|secret|token)\s*=\s*(\"\"|\"|''|none|changeme|admin|default)" /etc /opt /app
  ```
- Review service documentation for "default credentials" mentions.
- Check if a credential change is enforced before the service accepts connections, or if the service is usable with defaults.

**Example scenario:**
> A system monitoring service container image ships with a default empty password for its primary daemon, with no enforced credential change on first run. An attacker with network access to the service port can authenticate without credentials. This type of finding is distinct from a CVE — it is a configuration security issue in the image defaults.

**Escalation criteria:**
- Default credentials are empty or well-known
- No documented procedure to change credentials before service is accessible
- Service is network-exposed by default (listens on 0.0.0.0 or has published port)

---

## Pattern 2: TLS Advertised but Disabled or Optional by Default

**Risk:** A service that documents TLS support but ships with TLS disabled or optional by default may be deployed without encryption, even by operators who believe they are protected.

**How to detect:**
- Compare image documentation/labels claiming TLS support against actual config file defaults.
- Look for config keys like `tls_enabled = false`, `ssl = off`, `require_ssl = no`, or equivalent.
- Check whether TLS is opt-in (must be explicitly enabled) versus opt-out (enabled by default, can be disabled).

**Example scenario:**
> A security-sensitive service container image documents TLS as a supported feature in its README and image labels. However, the default configuration shipped in the image has TLS disabled for a key component. Deployments following the "quick start" path run without TLS encryption, contradicting the service's security claims. This type of finding is a configuration security issue, not a CVE — the misconfiguration is in the shipped defaults.

**Escalation criteria:**
- TLS is explicitly advertised as a security feature but off by default
- The service handles sensitive data (keys, attestation results, credentials)
- The quick-start or default deployment path bypasses TLS entirely

---

## Pattern 3: Credential Files with Insecure Permissions in Image Layers

**Risk:** Configuration files containing credentials (API keys, database passwords, TLS private keys) baked into an image with world-readable permissions expose those credentials to any process running in the container.

**How to detect:**
- Inspect image layers for credential file permission issues:
  ```
  find / \( -name "*.key" -o -name "*.pem" -o -name "*secret*" -o -name "*password*" \) \
    -not -path "/proc/*" -exec ls -la {} \; 2>/dev/null
  ```
- Check for files with 0644 or 0755 permissions that contain private key material.

**Escalation criteria:**
- Private key or credential file is world-readable (mode 644 or broader)
- Credential is a default that is not rotated per-deployment
- File is in a layer that would be accessible to other containers sharing the image

---

## Pattern 4: Environment Variable Credential Injection without Documentation

**Risk:** Images that accept credentials via environment variables without documenting this pattern may lead operators to hardcode secrets in `docker run` commands, CI/CD scripts, or Kubernetes manifests in plaintext.

**How to detect:**
- Review entrypoint scripts for `$PASSWORD`, `$SECRET`, `$API_KEY`, `$TOKEN` references.
- Check whether the image documentation recommends using secrets management (Kubernetes Secrets, Vault, etc.) or simply shows `docker run -e PASSWORD=...`.

**Escalation criteria:**
- Credentials consumed from environment variables with no secrets management guidance
- Image documentation shows plaintext credential examples without disclaimer
- No support for file-based credential injection (e.g., `/run/secrets/`)

---

## Pattern 5: Privileged Runtime Requirements Baked into Default Configuration

**Risk:** Images that require `--privileged`, `CAP_SYS_ADMIN`, or other elevated capabilities by default unnecessarily expand the blast radius of container escape vulnerabilities.

**How to detect:**
- Review entrypoint scripts for capability-dependent operations (mount, raw socket, device access).
- Check image documentation for capability requirements.
- Test image startup without elevated capabilities to identify the minimal required set.

**Escalation criteria:**
- `--privileged` is required for basic (non-advanced) functionality
- `CAP_SYS_ADMIN` or `CAP_NET_ADMIN` required without documented justification
- No documented least-privilege capability set provided
