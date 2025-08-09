#!/bin/bash

echo "==============================="
echo " Atlas OCC Runtime Setup 🧱"
echo "==============================="

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# All paths below are relative to the script's location (e.g., if script is in 'tools/',
# '..' refers to the repository root).

VCPKG_ROOT_DIR="../vcpkg" # Points to vcpkg in the repository root
VCPKG_TRIPLET="x64-linux-dynamic"
OCC_VCPKG_PORT="opencascade" # Corrected: Using 'opencascade'

# RUNTIME_DIR is the final destination for your wrapper and its libraries.
# This is also the location where your pre-compiled atlas_occ.so is expected to be.
RUNTIME_DIR="../atlas_runtime/runtime/linux_x64"
WRAPPER_NAME="atlas_occ.so" # Your pre-compiled wrapper filename

# --- Function to check if a command exists ---
command_exists () {
    type "$1" &> /dev/null ;
}

# --- Step 1: Clone, Bootstrap, and Install Dependencies with vcpkg ---
# This assumes vcpkg will be cloned into a folder named 'vcpkg' in the repo root
if [ ! -d "$VCPKG_ROOT_DIR" ]; then
  echo "[⬇️] Cloning vcpkg..."
  # Clone vcpkg to the repository root
  git clone https://github.com/microsoft/vcpkg.git "$VCPKG_ROOT_DIR"
  echo "[⚙️] Bootstrapping vcpkg..."
  # Run bootstrap from the vcpkg directory in the repository root
  (cd "$VCPKG_ROOT_DIR" && ./bootstrap-vcpkg.sh)
else
  echo "[✔] vcpkg already exists."
fi

# Add an explicit update step for vcpkg to ensure port lists are current
echo "[🔄] Updating vcpkg port list..."
(cd "$VCPKG_ROOT_DIR" && ./vcpkg update)

echo "[📦] Installing OpenCascade and its dependencies via vcpkg..."
# Run vcpkg install from the vcpkg directory in the repository root
(cd "$VCPKG_ROOT_DIR" && ./vcpkg install "$OCC_VCPKG_PORT":"$VCPKG_TRIPLET")

# --- Step 2: Copy Dependencies to the Runtime Folder ---
# This step now focuses ONLY on copying the *dependencies* from vcpkg's installed location.
# The main wrapper (atlas_occ.so) is assumed to already be in RUNTIME_DIR.
echo "==============================="
echo " Copying .so dependencies into runtime "
echo "==============================="

# Ensure runtime directory exists
mkdir -p "$RUNTIME_DIR"

# Verify that the pre-compiled wrapper exists in the RUNTIME_DIR itself
if [ ! -f "${RUNTIME_DIR}/${WRAPPER_NAME}" ]; then
    echo "❌ Pre-compiled wrapper (${RUNTIME_DIR}/${WRAPPER_NAME}) not found."
    echo "Please ensure your 'atlas_occ.so' is already placed in the '${RUNTIME_DIR}' directory before running this script."
    exit 1
fi

echo "📋 Found pre-compiled wrapper ($WRAPPER_NAME) in $RUNTIME_DIR/."

# Find the exact installed directory for opencascade-occt to copy files from.
# This is more reliable than guessing or using a hardcoded path.
# We're looking for a known OpenCASCADE library like libTKernel.so.7.9
VCPKG_INSTALLED_LIB_DIR=$(find "$VCPKG_ROOT_DIR/installed/$VCPKG_TRIPLET/lib" -type f -name 'libTKernel.so*' -exec dirname {} \; | head -n 1)

if [ -z "$VCPKG_INSTALLED_LIB_DIR" ]; then
    echo "⚠️  Couldn't locate vcpkg installed OCC .so files. Skipping dependency copy for OCC libraries (this might lead to runtime issues)."
else
    echo "🔍 Found vcpkg installed OCC .so files in $VCPKG_INSTALLED_LIB_DIR"

    # Copy all libTK*.so* files (direct OpenCASCADE libraries)
    for sofile in "$VCPKG_INSTALLED_LIB_DIR"/libTK*.so*; do
        filename=$(basename "$sofile")
        dest="${RUNTIME_DIR}/$filename"
        if [ ! -f "$dest" ]; then
            echo "→ Copying $filename"
            cp -f "$sofile" "$dest"
        else
            echo "✓ $filename already exists in runtime folder, skipping copy"
        fi
    done

    # Get additional non-TK dependencies from the *existing* wrapper using ldd
    # We now use the wrapper directly from RUNTIME_DIR for ldd inspection.
    # Filter for paths coming from the vcpkg installed directory (but not TK* files, already copied)
    echo "🔎 Identifying and copying other non-TK dependencies from vcpkg installation (e.g., freetype, fontconfig)..."
    ldd "${RUNTIME_DIR}/${WRAPPER_NAME}" | awk '/=>/ {print $3}' | while read -r lib_path; do
        # Check if the path contains the vcpkg installed lib directory AND it's not an OpenCASCADE TK library
        if [[ "$lib_path" == *"$VCPKG_ROOT_DIR/installed/$VCPKG_TRIPLET/lib"* && ! "$(basename "$lib_path")" =~ ^libTK ]]; then
            lib_name=$(basename "$lib_path")
            dest="${RUNTIME_DIR}/$lib_name"
            if [ ! -f "$dest" ]; then
                echo "→ Copying $lib_name"
                cp -f "$lib_path" "$dest"
            else
                echo "✓ $lib_name already exists in runtime folder, skipping copy"
            fi
        fi
    done
fi

# --- Step 3: Patch RPATH for the Wrapper and its Copied Dependencies ---
echo "==============================="
echo " 🔗 Setting RPATH for runtime libraries "
echo "==============================="

PATHEL_TOOL="patchelf"
if ! command_exists "$PATHEL_TOOL"; then
    echo "❌ patchelf is not installed. Please install it first:"
    echo "   - On Ubuntu/Debian: sudo apt-get install patchelf"
    echo "   - On Fedora/RHEL: sudo dnf install patchelf"
    echo "Then run this script again."
    exit 1
fi

# Patch the main wrapper (`atlas_occ.so`) to look in its own directory
echo "Patching main wrapper: $WRAPPER_NAME"
"$PATHEL_TOOL" --set-rpath '$ORIGIN' "$RUNTIME_DIR/$WRAPPER_NAME"

# Patch all copied `.so` files (OpenCASCADE and other vcpkg libraries) in the runtime directory.
# This ensures that these libraries also look in $ORIGIN for their own sub-dependencies.
echo "Patching all copied libraries in $RUNTIME_DIR/ to use \$ORIGIN RPATH..."
for sofile in "$RUNTIME_DIR"/*.so*; do
    # Ensure it's a regular file and not a symlink, and that it can be patched.
    # Also, check if it already has $ORIGIN in its RPATH to avoid redundant patching.
    if [ -f "$sofile" -a ! -L "$sofile" ]; then # -a for AND, -L for symlink
        # Check if '$ORIGIN' is already in the RPATH, or if the RPATH is already empty (no dependencies)
        if ! ldd "$sofile" 2>&1 | grep -q 'RPATH.*\$ORIGIN'; then
            echo "  - Patching $(basename "$sofile")"
            "$PATHEL_TOOL" --set-rpath '$ORIGIN' "$sofile"
        else
            echo "  - $(basename "$sofile") already patched with \$ORIGIN or has no dynamic dependencies."
        fi
    fi
done

echo "✅ All setup, copy, and RPATH patching complete! "
echo "The wrapper and its dependencies are now in $RUNTIME_DIR/ and ready to use."
echo "You can now safely import 'atlas_occ' from your Python program."
