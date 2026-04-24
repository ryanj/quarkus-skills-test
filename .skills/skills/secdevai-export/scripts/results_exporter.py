#!/usr/bin/env python3
"""
SecDevAI Results Exporter
Exports security review results to Markdown and SARIF formats.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# SARIF schema version
SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

# Allow a persistent base directory via environment variable.
# Set SECDEVAI_RESULTS_DIR in your shell profile to avoid retyping it each run.
# Example: export SECDEVAI_RESULTS_DIR=~/my-project/security-results
_ENV_RESULTS_DIR = "SECDEVAI_RESULTS_DIR"
_DEFAULT_RESULTS_DIR = "secdevai-results"


def confirm_result_directory(default: str = _DEFAULT_RESULTS_DIR) -> Path:
    """
    Prompt user to confirm result directory.

    Checks SECDEVAI_RESULTS_DIR env var first; uses it as the default when set
    so users can configure a persistent base directory without retyping it each run.

    Args:
        default: Fallback default directory name (used when env var is not set)

    Returns:
        Path object for the result directory
    """
    env_override = os.environ.get(_ENV_RESULTS_DIR)
    effective_default = env_override if env_override else default

    if env_override:
        print("\nSave results to directory: (from $SECDEVAI_RESULTS_DIR)")
    else:
        print("\nSave results to directory:")

    prompt = f"Result directory [{effective_default}]: "
    result_dir_input = input(prompt).strip() or effective_default

    result_dir = Path(result_dir_input).expanduser().resolve()

    # Create directory if it doesn't exist
    result_dir.mkdir(parents=True, exist_ok=True)

    print(f"✓ Results will be saved to: {result_dir}\n")

    return result_dir


def severity_to_sarif_level(severity: str) -> str:
    """Convert SecDevAI severity to SARIF level."""
    severity_upper = severity.upper()
    if severity_upper in ("CRITICAL", "HIGH"):
        return "error"
    elif severity_upper == "MEDIUM":
        return "warning"
    elif severity_upper == "LOW":
        return "note"
    else:
        return "none"


def severity_to_sarif_severity(severity: str) -> str:
    """Convert SecDevAI severity to SARIF severity."""
    severity_upper = severity.upper()
    if severity_upper == "CRITICAL":
        return "critical"
    elif severity_upper == "HIGH":
        return "high"
    elif severity_upper == "MEDIUM":
        return "medium"
    elif severity_upper == "LOW":
        return "low"
    else:
        return "info"


def convert_to_markdown(data: Dict[str, Any]) -> str:
    """
    Convert security review results to Markdown format.
    
    Args:
        data: Security review results dictionary
        
    Returns:
        Markdown formatted string
    """
    lines = []
    
    # Header
    lines.append("# SecDevAI Security Review Report")
    lines.append("")
    
    # Metadata
    metadata = data.get("metadata", {})
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- **Tool**: {metadata.get('tool', 'secdevai')}")
    lines.append(f"- **Version**: {metadata.get('version', '1.0.0')}")
    lines.append(f"- **Timestamp**: {metadata.get('timestamp', datetime.now().isoformat())}")
    
    target_file = metadata.get("target_file")
    if target_file:
        lines.append(f"- **Target File**: `{target_file}`")
    
    analyzer = metadata.get("analyzer")
    if analyzer:
        lines.append(f"- **Analyzer**: {analyzer}")
    
    lines.append("")
    
    # Summary
    summary = data.get("summary", {})
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Findings**: {summary.get('total_findings', 0)}")
    lines.append(f"- **Critical**: {summary.get('critical', 0)}")
    lines.append(f"- **High**: {summary.get('high', 0)}")
    lines.append(f"- **Medium**: {summary.get('medium', 0)}")
    lines.append(f"- **Low**: {summary.get('low', 0)}")
    lines.append(f"- **Info**: {summary.get('info', 0)}")
    lines.append("")
    
    # Findings
    findings = data.get("findings", [])
    if findings:
        lines.append("## Findings")
        lines.append("")
        
        # Group by severity
        severity_groups = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
            "INFO": [],
        }
        
        for finding in findings:
            severity = finding.get("severity", "INFO").upper()
            if severity in severity_groups:
                severity_groups[severity].append(finding)
            else:
                severity_groups["INFO"].append(finding)
        
        # Emoji mapping for severity
        severity_emoji = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "INFO": "ℹ️",
        }
        
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            group_findings = severity_groups[severity]
            if not group_findings:
                continue
            
            emoji = severity_emoji.get(severity, "")
            lines.append(f"### {emoji} **{severity} Severity** ({len(group_findings)})")
            lines.append("")
            
            for finding in group_findings:
                finding_id = finding.get("id", "")
                title = finding.get("title", "")
                
                lines.append(f"#### {finding_id}: {title}")
                lines.append("")
                
                # Location
                location = finding.get("location", {})
                if location:
                    file_path = location.get("file", "")
                    start_line = location.get("start_line")
                    end_line = location.get("end_line")
                    
                    if file_path:
                        if start_line and end_line:
                            lines.append(f"**Location**: `{file_path}:{start_line}-{end_line}`")
                        elif start_line:
                            lines.append(f"**Location**: `{file_path}:{start_line}`")
                        else:
                            lines.append(f"**Location**: `{file_path}`")
                        lines.append("")
                
                # OWASP Category and CWE
                owasp_category = finding.get("owasp_category")
                cwe = finding.get("cwe")
                
                if owasp_category or cwe:
                    lines.append("**Classification**:")
                    if owasp_category:
                        lines.append(f"- OWASP: {owasp_category}")
                    if cwe:
                        lines.append(f"- CWE: {cwe}")
                    lines.append("")
                
                # Description
                description = finding.get("description")
                if description:
                    lines.append("**Description**:")
                    lines.append("")
                    lines.append(description)
                    lines.append("")
                
                # Risk
                risk = finding.get("risk")
                if risk:
                    lines.append("**Risk**:")
                    lines.append("")
                    lines.append(risk)
                    lines.append("")
                
                # Attack Vector
                attack_vector = finding.get("attack_vector")
                if attack_vector:
                    lines.append("**Attack Vector**:")
                    lines.append("")
                    lines.append(attack_vector)
                    lines.append("")
                
                # Attack Example
                attack_example = finding.get("attack_example")
                if attack_example:
                    lines.append("**Attack Example**:")
                    lines.append("")
                    lines.append("```")
                    lines.append(attack_example)
                    lines.append("```")
                    lines.append("")
                
                # Vulnerable Code
                vulnerable_code = finding.get("vulnerable_code")
                if vulnerable_code:
                    lines.append("**Vulnerable Code**:")
                    lines.append("")
                    lines.append("```python")
                    lines.append(vulnerable_code)
                    lines.append("```")
                    lines.append("")
                
                # Remediation
                remediation = finding.get("remediation", {})
                if remediation:
                    approach = remediation.get("approach")
                    code = remediation.get("code")
                    
                    if approach:
                        lines.append("**Remediation**:")
                        lines.append("")
                        lines.append(approach)
                        lines.append("")
                    
                    if code:
                        lines.append("**Fixed Code**:")
                        lines.append("")
                        lines.append("```python")
                        lines.append(code)
                        lines.append("```")
                        lines.append("")
                
                # Impact
                impact = finding.get("impact", [])
                if impact:
                    lines.append("**Impact**:")
                    lines.append("")
                    for item in impact:
                        lines.append(f"- {item}")
                    lines.append("")
                
                # References
                references = finding.get("references", [])
                if references:
                    lines.append("**References**:")
                    lines.append("")
                    for ref in references:
                        lines.append(f"- {ref}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
    
    # Affected Endpoints
    affected_endpoints = data.get("affected_endpoints", [])
    if affected_endpoints:
        lines.append("## Affected Endpoints")
        lines.append("")
        for endpoint in affected_endpoints:
            endpoint_name = endpoint.get("endpoint", "")
            file_path = endpoint.get("file", "")
            line = endpoint.get("line", "")
            vulnerability = endpoint.get("vulnerability", "")
            user_input = endpoint.get("user_input", "")
            
            lines.append(f"### {endpoint_name}")
            lines.append("")
            if file_path:
                lines.append(f"- **File**: `{file_path}:{line}`")
            if vulnerability:
                lines.append(f"- **Vulnerability**: {vulnerability}")
            if user_input:
                lines.append(f"- **User Input**: {user_input}")
            lines.append("")
    
    # Recommendations
    recommendations = data.get("recommendations", {})
    if recommendations:
        lines.append("## Recommendations")
        lines.append("")
        
        immediate = recommendations.get("immediate_actions", [])
        if immediate:
            lines.append("### Immediate Actions")
            lines.append("")
            for action in immediate:
                lines.append(f"- {action}")
            lines.append("")
        
        long_term = recommendations.get("long_term_improvements", [])
        if long_term:
            lines.append("### Long-term Improvements")
            lines.append("")
            for improvement in long_term:
                lines.append(f"- {improvement}")
            lines.append("")
    
    return "\n".join(lines)


# Headers that must never appear in exported artifacts.
# These can carry credentials, session tokens, or other secrets.
_REDACTED_HEADERS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "proxy-authorization",
        "x-api-key",
        "x-auth-token",
        "x-csrf-token",
        "x-forwarded-authorization",
    }
)
_REDACTED_PLACEHOLDER = "[redacted]"


def _redact_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *headers* with sensitive values replaced."""
    return {
        name: (_REDACTED_PLACEHOLDER if name.lower() in _REDACTED_HEADERS else value)
        for name, value in headers.items()
    }


def _build_web_request(req: Dict[str, Any]) -> Dict[str, Any]:
    """Build a SARIF webRequest object (spec section 3.46).

    Sensitive headers (Authorization, Cookie, etc.) are redacted.
    Request bodies are omitted to avoid leaking payload data.
    """
    sarif_req: Dict[str, Any] = {}
    if "protocol" in req:
        sarif_req["protocol"] = req["protocol"]
    if "version" in req:
        sarif_req["version"] = req["version"]
    if "method" in req:
        sarif_req["method"] = req["method"]
    if "target" in req:
        sarif_req["target"] = req["target"]
    if "headers" in req:
        sarif_req["headers"] = _redact_headers(req["headers"])
    if "parameters" in req:
        sarif_req["parameters"] = req["parameters"]
    # Bodies are intentionally excluded — they can contain credentials or PII.
    return sarif_req


def _build_web_response(resp: Dict[str, Any]) -> Dict[str, Any]:
    """Build a SARIF webResponse object (spec section 3.47).

    Sensitive headers (Set-Cookie, etc.) are redacted.
    Response bodies are omitted to avoid leaking application data.
    """
    sarif_resp: Dict[str, Any] = {}
    if "protocol" in resp:
        sarif_resp["protocol"] = resp["protocol"]
    if "version" in resp:
        sarif_resp["version"] = resp["version"]
    if "statusCode" in resp:
        sarif_resp["statusCode"] = resp["statusCode"]
    if "reasonPhrase" in resp:
        sarif_resp["reasonPhrase"] = resp["reasonPhrase"]
    if "headers" in resp:
        sarif_resp["headers"] = _redact_headers(resp["headers"])
    # Bodies are intentionally excluded — they can contain credentials or PII.
    return sarif_resp


def _build_related_locations(
    related: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """Build SARIF relatedLocations array (spec section 3.27.22)."""
    sarif_locs = []
    for idx, loc in enumerate(related):
        sarif_loc: Dict[str, Any] = {"id": idx}
        if "message" in loc:
            sarif_loc["message"] = {"text": loc["message"]}
        phys: Dict[str, Any] = {}
        if "file" in loc:
            phys["artifactLocation"] = {"uri": loc["file"]}
        region: Dict[str, Any] = {}
        if "start_line" in loc:
            region["startLine"] = loc["start_line"]
        if "end_line" in loc:
            region["endLine"] = loc["end_line"]
        if region:
            phys["region"] = region
        if "snippet" in loc:
            ctx_start = loc.get("start_line", 1)
            phys["contextRegion"] = {
                "startLine": ctx_start,
                "snippet": {"text": loc["snippet"]},
            }
        if phys:
            sarif_loc["physicalLocation"] = phys
        sarif_locs.append(sarif_loc)
    return sarif_locs


def _build_code_flows(
    steps: list[Dict[str, Any]],
    flow_message: str = "",
) -> list[Dict[str, Any]]:
    """Build SARIF codeFlows array (spec section 3.27.18 / 3.36 / 3.37)."""
    thread_flow_locations = []
    for step in steps:
        tfl: Dict[str, Any] = {}
        loc: Dict[str, Any] = {}
        if "message" in step:
            loc["message"] = {"text": step["message"]}
        phys: Dict[str, Any] = {}
        if "file" in step:
            phys["artifactLocation"] = {"uri": step["file"]}
        region: Dict[str, Any] = {}
        if "start_line" in step:
            region["startLine"] = step["start_line"]
        if "end_line" in step:
            region["endLine"] = step["end_line"]
        if region:
            phys["region"] = region
        if phys:
            loc["physicalLocation"] = phys
        tfl["location"] = loc
        thread_flow_locations.append(tfl)

    code_flow: Dict[str, Any] = {
        "threadFlows": [{"locations": thread_flow_locations}],
    }
    if flow_message:
        code_flow["message"] = {"text": flow_message}
    return [code_flow]


def convert_to_sarif(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert security review results to SARIF format.

    Supports DAST source-correlation fields per SARIF v2.1.0:
      - webRequest / webResponse  (spec sections 3.27.14-15, 3.46-47)
      - relatedLocations          (spec section 3.27.22)
      - codeFlows                 (spec sections 3.27.18, 3.36-37)

    These fields are emitted when the corresponding keys are present in a
    finding dict (web_request, web_response, related_locations, code_flow).

    Args:
        data: Security review results dictionary

    Returns:
        SARIF formatted dictionary
    """
    metadata = data.get("metadata", {})
    findings = data.get("findings", [])

    run: Dict[str, Any] = {
        "tool": {
            "driver": {
                "name": metadata.get("tool", "secdevai"),
                "version": metadata.get("version", "1.0.0"),
                "informationUri": "https://github.com/RedHatProductSecurity/secdevai",
                "rules": [],
            }
        },
        "results": [],
        "invocations": [
            {
                "executionSuccessful": True,
                "exitCode": 0,
            }
        ],
    }

    sarif = {
        "version": SARIF_VERSION,
        "$schema": SARIF_SCHEMA,
        "runs": [run],
    }

    # Run-level caches for webRequests / webResponses (spec sections 3.14.21-22)
    web_requests_cache: list[Dict[str, Any]] = []
    web_responses_cache: list[Dict[str, Any]] = []
    web_req_index: Dict[str, int] = {}
    web_resp_index: Dict[str, int] = {}

    # Extract unique rules
    rules: Dict[str, Dict[str, Any]] = {}
    for finding in findings:
        rule_id = finding.get("id", "")
        if rule_id and rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "name": finding.get("title", ""),
                "shortDescription": {
                    "text": finding.get("title", ""),
                },
                "fullDescription": {
                    "text": finding.get("description", ""),
                },
                "properties": {
                    "tags": [],
                },
            }

            owasp_category = finding.get("owasp_category")
            if owasp_category:
                rules[rule_id]["properties"]["tags"].append(owasp_category)

            cwe = finding.get("cwe")
            if cwe:
                rules[rule_id]["properties"]["tags"].append(cwe)

    run["tool"]["driver"]["rules"] = list(rules.values())

    # Convert findings to SARIF results
    for finding in findings:
        location = finding.get("location", {})
        file_path = location.get("file", "")
        start_line = location.get("start_line")
        end_line = location.get("end_line")

        result: Dict[str, Any] = {
            "ruleId": finding.get("id", ""),
            "level": severity_to_sarif_level(finding.get("severity", "INFO")),
            "message": {
                "text": finding.get("description", ""),
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_path,
                        },
                    }
                }
            ],
            "properties": {
                "severity": severity_to_sarif_severity(
                    finding.get("severity", "INFO")
                ),
            },
        }

        # Add region (line numbers)
        if start_line:
            region: Dict[str, int] = {"startLine": start_line}
            if end_line:
                region["endLine"] = end_line
            result["locations"][0]["physicalLocation"]["region"] = region

        # Add code snippet if available
        vulnerable_code = finding.get("vulnerable_code")
        if vulnerable_code and start_line:
            result["locations"][0]["physicalLocation"]["contextRegion"] = {
                "startLine": start_line,
                "snippet": {
                    "text": vulnerable_code,
                },
            }

        # --- DAST source-correlation fields ---

        # webRequest (spec section 3.27.14)
        raw_req = finding.get("web_request")
        if raw_req:
            sarif_req = _build_web_request(raw_req)
            cache_key = json.dumps(sarif_req, sort_keys=True)
            if cache_key not in web_req_index:
                idx = len(web_requests_cache)
                sarif_req_cached = {**sarif_req, "index": idx}
                web_requests_cache.append(sarif_req_cached)
                web_req_index[cache_key] = idx
            result["webRequest"] = {"index": web_req_index[cache_key]}

        # webResponse (spec section 3.27.15)
        raw_resp = finding.get("web_response")
        if raw_resp:
            sarif_resp = _build_web_response(raw_resp)
            cache_key = json.dumps(sarif_resp, sort_keys=True)
            if cache_key not in web_resp_index:
                idx = len(web_responses_cache)
                sarif_resp_cached = {**sarif_resp, "index": idx}
                web_responses_cache.append(sarif_resp_cached)
                web_resp_index[cache_key] = idx
            result["webResponse"] = {"index": web_resp_index[cache_key]}

        # relatedLocations (spec section 3.27.22)
        raw_related = finding.get("related_locations")
        if raw_related:
            result["relatedLocations"] = _build_related_locations(raw_related)

        # codeFlows (spec section 3.27.18)
        raw_flow = finding.get("code_flow")
        if raw_flow:
            flow_msg = finding.get("code_flow_message", "")
            result["codeFlows"] = _build_code_flows(raw_flow, flow_msg)

        run["results"].append(result)

    # Attach run-level caches when present
    if web_requests_cache:
        run["webRequests"] = web_requests_cache
    if web_responses_cache:
        run["webResponses"] = web_responses_cache

    return sarif


def export_results(
    data: Dict[str, Any],
    result_dir: Optional[Path] = None,
    command_type: str = "review",
) -> tuple[Path, Path]:
    """
    Export security review results to Markdown and SARIF formats.
    
    Args:
        data: Security review results dictionary
        result_dir: Directory to save results (will prompt if None)
        command_type: Type of command (review, fix, tool)
        
    Returns:
        Tuple of (markdown_path, sarif_path)
    """
    if result_dir is None:
        result_dir = confirm_result_directory()
    
    # Generate timestamp for directory and filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create datetime-based subdirectory with 'secdevai-' prefix
    timestamp_dir = result_dir / f"secdevai-{timestamp}"
    timestamp_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = f"secdevai-{command_type}-{timestamp}"
    
    # Save Markdown
    markdown_content = convert_to_markdown(data)
    markdown_path = timestamp_dir / f"{base_name}.md"
    markdown_path.write_text(markdown_content, encoding="utf-8")
    print(f"✓ Markdown report saved: {markdown_path}")
    
    # Save SARIF
    sarif_content = convert_to_sarif(data)
    sarif_path = timestamp_dir / f"{base_name}.sarif"
    sarif_path.write_text(json.dumps(sarif_content, indent=2), encoding="utf-8")
    print(f"✓ SARIF report saved: {sarif_path}")
    
    return markdown_path, sarif_path



