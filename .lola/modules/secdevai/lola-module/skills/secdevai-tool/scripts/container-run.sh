#!/bin/bash
# SecDevAI Container Runner
# Generic wrapper that detects podman/docker and runs any image
# in a hardened, read-only container with the target mounted at /src.
#
# Usage: container-run.sh [flags...] <image> [args...]
#
# Flags (must precede the image):
#   --env KEY=VALUE   Pass an environment variable to the container (repeatable)
#   --                Stop flag parsing
#
# Network access is always disabled (--network=none) to enforce isolation.
#
# The target directory is always the current working directory,
# mounted read-only at /src inside the container.

set -euo pipefail

detect_runtime() {
    if command -v podman &>/dev/null; then
        echo "podman"
    elif command -v docker &>/dev/null; then
        echo "docker"
    else
        cat >&2 <<'MSG'
Error: No container runtime found.

SecDevAI requires podman or docker to run security tools in isolated,
read-only containers. Please install one of the following:

  Podman (recommended):
    macOS  : brew install podman && podman machine init && podman machine start
    Fedora : sudo dnf install podman
    Ubuntu : sudo apt install podman

  Docker:
    All OS : https://docs.docker.com/get-docker/

After installing, re-run this command.
MSG
        exit 1
    fi
}

# --env values and image names are specified by SKILL.md instructions,
# not by end users directly.
env_args=()
while [[ "${1:-}" == --* ]]; do
    case "$1" in
        --env)
            shift
            env_args+=(-e "${1:?--env requires KEY=VALUE}")
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unknown flag: $1" >&2
            exit 1
            ;;
    esac
done

image="${1:-}"
if [[ -z "$image" ]]; then
    echo "Usage: container-run.sh [--env K=V]... <image> [args...]" >&2
    exit 1
fi
shift

runtime="$(detect_runtime)"
echo "Using runtime: ${runtime}" >&2
echo "Running image: ${image}" >&2

exec "$runtime" run --rm --read-only \
    --cap-drop ALL \
    --security-opt=no-new-privileges \
    --user "$(id -u):$(id -g)" \
    --memory=512m \
    --pids-limit=256 \
    --network=none \
    ${env_args[@]+"${env_args[@]}"} \
    --tmpfs /tmp:rw,noexec,nosuid,size=64m \
    -v "$(pwd):/src:ro,Z" \
    -w /src \
    "$image" "$@"
