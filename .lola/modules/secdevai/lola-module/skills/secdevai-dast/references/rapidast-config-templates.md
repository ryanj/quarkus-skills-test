# RapiDAST Configuration Templates

Reference for `secdevai-dast`. The `rapidast-scan.sh` script generates these automatically — use this file when you need to understand, debug, or manually customize a config.

**RapiDAST docs**: https://github.com/RedHatProductSecurity/rapidast/blob/development/docs/USER-GUIDE.md

---

## 1. OpenAPI (Swagger) Scan — Passive Only

```yaml
config:
  configVersion: 6
  base_results_dir: "/opt/rapidast/results"

application:
  shortName: "myapp"
  url: "https://myapp.example"

general:
  # authentication block goes here (see section 4)

scanners:
  zap:
    apiScan:
      apis:
        apiUrl: "https://myapp.example/openapi.json"
        # alternative: apiFile: "/opt/rapidast/config/openapi.json"
    passiveScan:
      disabledRules: "2,10015,10024,10027,10054,10096,10109,10112"
    miscOptions:
      additionalAddons: "ascanrulesBeta"
```

---

## 2. OpenAPI Scan — Passive + Active

```yaml
config:
  configVersion: 6
  base_results_dir: "/opt/rapidast/results"

application:
  shortName: "myapp"
  url: "https://myapp.example"

general:
  # authentication block goes here (see section 4)

scanners:
  zap:
    apiScan:
      apis:
        apiUrl: "https://myapp.example/openapi.json"
    passiveScan:
      disabledRules: "2,10015,10024,10027,10054,10096,10109,10112"
    activeScan:
      policy: "API-scan-minimal"
      # maxRuleDurationInMins: 10   # cap per-rule duration
      # maxScanDurationInMins: 60   # overall active scan cap
    miscOptions:
      additionalAddons: "ascanrulesBeta"
```

Available policies: `API-scan-minimal`, `Default Policy`, `Light`, `Medium`, `Heavy`, `SQL-Injection-Active`

---

## 3. Spider Scan (HTML link following)

```yaml
config:
  configVersion: 6
  base_results_dir: "/opt/rapidast/results"

application:
  shortName: "myapp"
  url: "https://myapp.example"

general:
  # authentication block goes here (see section 4)

scanners:
  zap:
    spider:
      maxDuration: 5      # minutes; 0 = unlimited
      url: "https://myapp.example"  # optional, defaults to application.url
    passiveScan:
      disabledRules: "2,10015,10024,10027,10054,10096,10109,10112"
    miscOptions:
      additionalAddons: "ascanrulesBeta"
```

---

## 4. Ajax Spider Scan (JavaScript / SPA apps)

```yaml
config:
  configVersion: 6
  base_results_dir: "/opt/rapidast/results"

application:
  shortName: "myapp"
  url: "https://myapp.example"

general:
  # authentication block goes here (see section 4)

scanners:
  zap:
    spiderAjax:
      maxDuration: 10     # minutes; 0 = unlimited
      url: "https://myapp.example"
      browserId: firefox-headless
      # maxCrawlStates: 10   # limit for memory-constrained environments
      # maxCrawlDepth: 10    # default: unlimited
    passiveScan:
      disabledRules: "2,10015,10024,10027,10054,10096,10109,10112"
    miscOptions:
      additionalAddons: "ascanrulesBeta"
```

**Note**: Ajax Spider requires more resources. Set `--shm-size=2g` when running the RapiDAST container if Firefox crashes (see Troubleshooting).

---

## 5. Authentication Configuration Blocks

Place under the `general:` section.

### 5a. HTTP Basic

```yaml
general:
  authentication:
    type: http_basic
    parameters:
      username: "user"
      password: "mypassw0rd"
```

### 5b. HTTP Header (API key or Bearer token)

```yaml
general:
  authentication:
    type: http_header
    parameters:
      name: "Authorization"          # header name
      value: "Bearer my-api-token"   # or use value_from_var: API_TOKEN_ENV_VAR
```

### 5c. Cookie

```yaml
general:
  authentication:
    type: cookie
    parameters:
      name: "session"
      value: "abc123"
```

### 5d. OAuth2 Refresh Token

```yaml
general:
  authentication:
    type: oauth2_rtoken
    parameters:
      token_endpoint: "https://sso.example.com/token"
      client_id: "my-client"
      rtoken_from_var: "RTOKEN"   # name of env var holding the refresh token
      # preauth: false            # set true for short scans; uses one token throughout
```

Pass the token to the RapiDAST container:

```bash
podman run --rm \
  -e RTOKEN="$RTOKEN" \
  -v ./config.yaml:/opt/rapidast/config/config.yaml:Z \
  -v ./results:/opt/rapidast/results/:Z,U \
  quay.io/redhatproductsecurity/rapidast:latest
```

### 5e. Browser-based (form login)

```yaml
general:
  authentication:
    type: browser
    parameters:
      username: "user"
      password: "mypassw0rd"
      loginPageUrl: "https://myapp.example/login"
      verifyUrl: "https://myapp.example/api/user/me"
      loginPageWait: 2
      loggedInRegex: "\\Q 200 OK\\E"
      loggedOutRegex: "\\Q 403 Forbidden\\E"
```

---

## 6. Container Run Commands

### Linux (podman — recommended)

```bash
podman run --rm \
  -v ./config.yaml:/opt/rapidast/config/config.yaml:Z \
  -v ./results:/opt/rapidast/results/:Z,U \
  quay.io/redhatproductsecurity/rapidast:latest
```

### Linux (docker)

```bash
docker run --rm \
  -v ./config.yaml:/opt/rapidast/config/config.yaml \
  -v ./results:/opt/rapidast/results \
  quay.io/redhatproductsecurity/rapidast:latest
```

### macOS (Docker Desktop)

On macOS, `localhost` in the config must become `host.docker.internal` so the RapiDAST container can reach services running on the host:

```bash
docker run --rm \
  -v ./config.yaml:/opt/rapidast/config/config.yaml \
  -v ./results:/opt/rapidast/results \
  quay.io/redhatproductsecurity/rapidast:latest
```

The `rapidast-scan.sh` script handles this substitution automatically.

### Ajax Spider (extra resources required)

```bash
podman run --rm \
  --shm-size=2g \
  --pids-limit=-1 \
  -v ./config.yaml:/opt/rapidast/config/config.yaml:Z \
  -v ./results:/opt/rapidast/results/:Z,U \
  quay.io/redhatproductsecurity/rapidast:latest
```

---

## 7. Result Exclusion Rules (CEL filters)

Add under `config.results.exclusions` to filter known false positives from the consolidated SARIF:

```yaml
config:
  configVersion: 6
  results:
    exclusions:
      enabled: true
      rules:
        - name: "Exclude admin paths"
          cel_expression: '.result.locations.exists(loc, loc.physicalLocation.artifactLocation.uri.startsWith("https://myapp.example/admin"))'
        - name: "Exclude known FP rule"
          cel_expression: '.result.ruleId == "10112" && .result.webResponse.statusCode == 401'
```

---

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Error getting access token` | OAuth2 misconfiguration | Verify `token_endpoint`, `client_id`, and the env var name |
| `Failed to parse swagger defn null` | OpenAPI spec unreachable or invalid | Check the `apiUrl` is accessible from inside the container |
| `java.lang.OutOfMemoryError: Java heap space` | Large OpenAPI spec | Add `miscOptions.memMaxHeap: "6144m"` |
| `Failed to start browser firefox-headless` | Insufficient `/dev/shm` | Add `--shm-size=2g` to the container run command |
| `pthread_create failed (EAGAIN)` | Too many threads | Add `--pids-limit=-1` to the container run command |
| `YAML exceeds limit: 3145728 code points` | Huge Swagger v2 file | Convert to OpenAPI v3, or set `_JAVA_OPTIONS=-DmaxYamlCodePoints=99999999` |
| Container can't reach `localhost` | Network isolation | On macOS use `host.docker.internal`; on Linux use `--network host` |
| ZAP plugins missing | Known ZAP bug | Set `miscOptions.updateAddons: true` to force addon re-download |
