#!/bin/bash
# SecDevAI DAST Scan Script
# Generates a RapiDAST configuration file and runs OWASP ZAP via the RapiDAST container image.
#
# Usage:
#   rapidast-scan.sh --target-url <URL> --app-name <NAME> --scan-type <openapi|spider|ajax-spider>
#                    [--openapi-url <URL>] [--max-duration <MINUTES>]
#                    [--auth-type <none|http_basic|http_header|cookie|oauth2>]
#                    [--auth-params <JSON>] [--active-scan] [--output-dir <DIR>]

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
TARGET_URL=""
APP_NAME="secdevai-dast-target"
SCAN_TYPE="spider"
OPENAPI_URL=""
MAX_DURATION=5
AUTH_TYPE="none"
AUTH_PARAMS="{}"
ACTIVE_SCAN=false
# Respect SECDEVAI_RESULTS_DIR env var (shared with other secdevai commands).
# Falls back to ./secdevai-results if not set.
OUTPUT_DIR="${SECDEVAI_RESULTS_DIR:-./secdevai-results}/dast"
# RapiDAST container image (pin tag here when upgrading).
RAPIDAST_IMAGE="quay.io/redhatproductsecurity/rapidast:2.13.0"

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --target-url)   TARGET_URL="$2";   shift 2 ;;
        --app-name)     APP_NAME="$2";     shift 2 ;;
        --scan-type)    SCAN_TYPE="$2";    shift 2 ;;
        --openapi-url)  OPENAPI_URL="$2";  shift 2 ;;
        --max-duration) MAX_DURATION="$2"; shift 2 ;;
        --auth-type)    AUTH_TYPE="$2";    shift 2 ;;
        --auth-params)  AUTH_PARAMS="$2";  shift 2 ;;
        --active-scan)  ACTIVE_SCAN=true;  shift ;;
        --output-dir)   OUTPUT_DIR="$2";   shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

# ── Validation ────────────────────────────────────────────────────────────────
if [[ -z "$TARGET_URL" ]]; then
    echo "Error: --target-url is required" >&2
    exit 1
fi

if [[ "$SCAN_TYPE" == "openapi" && -z "$OPENAPI_URL" ]]; then
    echo "Error: --openapi-url is required when --scan-type is openapi" >&2
    exit 1
fi

# ── Container runtime detection ───────────────────────────────────────────────
detect_runtime() {
    if command -v podman &>/dev/null; then
        echo "podman"
    elif command -v docker &>/dev/null; then
        echo "docker"
    else
        echo ""
    fi
}

RUNTIME=$(detect_runtime)
if [[ -z "$RUNTIME" ]]; then
    echo "Error: Neither podman nor docker was found. Install one to run RapiDAST." >&2
    exit 1
fi

echo "Container runtime: $RUNTIME"

# ── macOS host resolution ─────────────────────────────────────────────────────
# When the target is localhost, RapiDAST runs inside a container and cannot
# reach the host via 'localhost'. On macOS (Docker Desktop), substitute the
# special hostname that routes to the host machine.
SCAN_TARGET_URL="$TARGET_URL"
if [[ "$(uname -s)" == "Darwin" ]]; then
    SCAN_TARGET_URL="${TARGET_URL//localhost/host.docker.internal}"
    SCAN_TARGET_URL="${SCAN_TARGET_URL//127.0.0.1/host.docker.internal}"
fi

# Also fix the OpenAPI URL if needed
SCAN_OPENAPI_URL="$OPENAPI_URL"
if [[ "$(uname -s)" == "Darwin" && -n "$OPENAPI_URL" ]]; then
    SCAN_OPENAPI_URL="${OPENAPI_URL//localhost/host.docker.internal}"
    SCAN_OPENAPI_URL="${SCAN_OPENAPI_URL//127.0.0.1/host.docker.internal}"
fi

# ── Prepare output directory ──────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR_ABS=$(cd "$OUTPUT_DIR" && pwd)

# ── YAML-safe quoting ─────────────────────────────────────────────────────────
# Escapes backslashes, double quotes, and newlines so a value can be safely
# embedded in a YAML double-quoted string without breaking the document.
yaml_escape() {
    local val="$1"
    val="${val//\\/\\\\}"
    val="${val//\"/\\\"}"
    val="${val//$'\n'/\\n}"
    printf '%s' "$val"
}

# ── Config generation ─────────────────────────────────────────────────────────
CONFIG_DIR=$(mktemp -d)
CONFIG_FILE="$CONFIG_DIR/rapidast-config.yaml"
trap 'rm -rf "$CONFIG_DIR"' EXIT

generate_auth_block() {
    local auth_type="$1"
    local params="$2"

    case "$auth_type" in
        http_basic)
            local username
            local password
            username=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('username',''))" 2>/dev/null || echo "")
            password=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('password',''))" 2>/dev/null || echo "")
            cat <<YAML
  authentication:
    type: http_basic
    parameters:
      username: "$(yaml_escape "$username")"
      password: "$(yaml_escape "$password")"
YAML
            ;;
        http_header)
            local header_name
            local header_value
            header_name=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('name','Authorization'))" 2>/dev/null || echo "Authorization")
            header_value=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('value',''))" 2>/dev/null || echo "")
            cat <<YAML
  authentication:
    type: http_header
    parameters:
      name: "$(yaml_escape "$header_name")"
      value: "$(yaml_escape "$header_value")"
YAML
            ;;
        cookie)
            local cookie_name
            local cookie_value
            cookie_name=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('name','session'))" 2>/dev/null || echo "session")
            cookie_value=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('value',''))" 2>/dev/null || echo "")
            cat <<YAML
  authentication:
    type: cookie
    parameters:
      name: "$(yaml_escape "$cookie_name")"
      value: "$(yaml_escape "$cookie_value")"
YAML
            ;;
        oauth2)
            local token_endpoint
            local client_id
            local rtoken_var
            token_endpoint=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('token_endpoint',''))" 2>/dev/null || echo "")
            client_id=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('client_id',''))" 2>/dev/null || echo "")
            rtoken_var=$(printf '%s\n' "$params" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('rtoken_var','RTOKEN'))" 2>/dev/null || echo "RTOKEN")
            cat <<YAML
  authentication:
    type: oauth2_rtoken
    parameters:
      token_endpoint: "$(yaml_escape "$token_endpoint")"
      client_id: "$(yaml_escape "$client_id")"
      rtoken_from_var: "$(yaml_escape "$rtoken_var")"
YAML
            ;;
        *)
            # none — no auth block
            echo ""
            ;;
    esac
}

generate_scanner_block() {
    local scan_type="$1"
    local openapi_url="$2"
    local target_url="$3"
    local max_duration="$4"
    local active_scan="$5"

    local active_block=""
    if [[ "$active_scan" == "true" ]]; then
        active_block="
    activeScan:
      policy: API-scan-minimal"
    fi

    case "$scan_type" in
        openapi)
            cat <<YAML
scanners:
  zap:
    apiScan:
      apis:
        apiUrl: "$(yaml_escape "$openapi_url")"
    passiveScan:
      disabledRules: "2,10015,10024,10027,10054,10096,10109,10112"${active_block}
    miscOptions:
      additionalAddons: "ascanrulesBeta"
YAML
            ;;
        ajax-spider)
            cat <<YAML
scanners:
  zap:
    spiderAjax:
      maxDuration: ${max_duration}
      url: "$(yaml_escape "$target_url")"
      browserId: firefox-headless
    passiveScan:
      disabledRules: "2,10015,10024,10027,10054,10096,10109,10112"${active_block}
    miscOptions:
      additionalAddons: "ascanrulesBeta"
YAML
            ;;
        spider|*)
            cat <<YAML
scanners:
  zap:
    spider:
      maxDuration: ${max_duration}
      url: "$(yaml_escape "$target_url")"
    passiveScan:
      disabledRules: "2,10015,10024,10027,10054,10096,10109,10112"${active_block}
    miscOptions:
      additionalAddons: "ascanrulesBeta"
YAML
            ;;
    esac
}

AUTH_BLOCK=$(generate_auth_block "$AUTH_TYPE" "$AUTH_PARAMS")
SCANNER_BLOCK=$(generate_scanner_block "$SCAN_TYPE" "$SCAN_OPENAPI_URL" "$SCAN_TARGET_URL" "$MAX_DURATION" "$ACTIVE_SCAN")

# Sanitize app name for YAML (no spaces or special chars, strip leading/trailing dashes)
APP_NAME_SAFE=$(echo "$APP_NAME" | tr -cs '[:alnum:]-_' '-' | tr '[:upper:]' '[:lower:]' | sed 's/^-*//;s/-*$//')

cat > "$CONFIG_FILE" <<YAML
config:
  configVersion: 6
  base_results_dir: "/opt/rapidast/results"

application:
  shortName: "$(yaml_escape "$APP_NAME_SAFE")"
  url: "$(yaml_escape "$SCAN_TARGET_URL")"

general:
${AUTH_BLOCK}

${SCANNER_BLOCK}
YAML

echo "Generated RapiDAST config:"
echo "─────────────────────────────────────────────"
cat "$CONFIG_FILE"
echo "─────────────────────────────────────────────"

# ── Run RapiDAST ─────────────────────────────────────────────────────────────
echo ""
echo "Starting RapiDAST scan using ${RUNTIME}..."
echo "Image: ${RAPIDAST_IMAGE}"
echo "Target: ${SCAN_TARGET_URL}"
echo "Output: ${OUTPUT_DIR_ABS}"
echo ""

# Additional flags for macOS (Docker Desktop needs host.docker.internal, no :Z needed)
VOLUME_FLAGS="-v ${CONFIG_FILE}:/opt/rapidast/config/config.yaml"
RESULTS_FLAGS="-v ${OUTPUT_DIR_ABS}:/opt/rapidast/results"

if [[ "$(uname -s)" == "Linux" ]]; then
    # SELinux relabeling for RHEL/Fedora/CentOS
    VOLUME_FLAGS="${VOLUME_FLAGS}:Z"
    RESULTS_FLAGS="${RESULTS_FLAGS}:Z,U"
else
    # macOS — no SELinux labels, but results need to be writable
    RESULTS_FLAGS="${RESULTS_FLAGS}"
fi

# Pass OAuth2 refresh token env var if oauth2 auth is configured
OAUTH2_ENV_FLAG=""
if [[ "$AUTH_TYPE" == "oauth2" ]]; then
    RTOKEN_VAR=$(printf '%s\n' "$AUTH_PARAMS" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('rtoken_var','RTOKEN'))" 2>/dev/null || echo "RTOKEN")
    # Validate the var name is a safe identifier before using it in a -e flag
    if [[ ! "$RTOKEN_VAR" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
        echo "Error: rtoken_var '${RTOKEN_VAR}' is not a valid environment variable name" >&2
        exit 1
    fi
    if [[ -n "${!RTOKEN_VAR:-}" ]]; then
        OAUTH2_ENV_FLAG="-e ${RTOKEN_VAR}=${!RTOKEN_VAR}"
    fi
fi

# ZAP exits non-zero when findings exist — capture exit code without triggering set -e
# shellcheck disable=SC2086
"$RUNTIME" run --rm \
    $VOLUME_FLAGS \
    $RESULTS_FLAGS \
    ${OAUTH2_ENV_FLAG} \
    "$RAPIDAST_IMAGE" && EXIT_CODE=0 || EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "RapiDAST scan completed successfully."
else
    echo "RapiDAST scan finished with exit code ${EXIT_CODE} (may include findings — check results)."
fi

# ── Flatten RapiDAST output into rapidast_result/ ────────────────────────────
# RapiDAST creates a nested structure like <shortName>/DAST-<timestamp>-RapiDAST/.
# Flatten it to $OUTPUT_DIR_ABS/rapidast_result/ for a predictable layout.
RAPIDAST_RESULT_DIR="${OUTPUT_DIR_ABS}/rapidast_result"
NESTED_DIR=$(find "$OUTPUT_DIR_ABS" -mindepth 2 -maxdepth 2 -type d -name "DAST-*" 2>/dev/null | head -n 1)

if [[ -n "$NESTED_DIR" ]]; then
    echo "Reorganizing RapiDAST output into rapidast_result/ ..."
    rm -rf "$RAPIDAST_RESULT_DIR"
    mv "$NESTED_DIR" "$RAPIDAST_RESULT_DIR"
    # Remove the now-empty parent directory left by RapiDAST (e.g. <shortName>/)
    PARENT_DIR=$(dirname "$NESTED_DIR")
    rmdir "$PARENT_DIR" 2>/dev/null || true
    echo "Done."
fi

echo "Results directory: ${OUTPUT_DIR_ABS}"

# Print SARIF file location if found
SARIF_FILE=$(find "$OUTPUT_DIR_ABS" -name "*.sarif" 2>/dev/null | head -n 1)
if [[ -n "$SARIF_FILE" ]]; then
    echo "SARIF report: ${SARIF_FILE}"
fi

exit $EXIT_CODE
