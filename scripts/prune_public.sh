#!/usr/bin/env bash
set -euo pipefail

# Prune dev-only assets from public branch to prepare lean distribution
# Run this after merging main into public

echo "🔍 Checking current branch..."
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
if [ "$BRANCH" != "public" ]; then
    echo "⚠️  Warning: Not on 'public' branch (current: $BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted"
        exit 1
    fi
fi

echo "🗑️  Removing dev artifacts..."

# BMAD and AI agent directories (CRITICAL - internal dev workflows)
git rm -rf .bmad-core .claude .gemini .cursor .trae .ai 2>/dev/null || true

# Internal documentation (keep only public-facing docs)
git rm -rf docs/prd docs/architecture docs/stories docs/project docs/qa 2>/dev/null || true
git rm -f docs/publish-plan.md docs/brief.md docs/ux-enhancements-specification.md 2>/dev/null || true
git rm -f zotero-rag-prd.md 2>/dev/null || true

# Dev scripts and profiling tools
git rm -rf scripts/benchmarking 2>/dev/null || true
git rm -f scripts/tune_pdfium2.py \
         scripts/test_parallel_extraction.py \
         scripts/verify_layout_mode.py \
         scripts/verify_settings.py \
         scripts/profile_indexing.py 2>/dev/null || true

# Test artifacts (keep core test suite, remove UI tests and large files)
git rm -rf tests/ui 2>/dev/null || true
git rm -f tests/test.pdf profile.out 2>/dev/null || true

# IDE and personal configs
git rm -rf .vscode .idea 2>/dev/null || true
git rm -f .DS_Store 2>/dev/null || true

# Dev-only configuration files
git rm -f opencode.jsonc 2>/dev/null || true
git rm -f AGENTS.md 2>/dev/null || true

# GitHub workflows (optional - uncomment to remove, or keep for CI/CD)
# git rm -rf .github 2>/dev/null || true

# Build artifacts and caches
git rm -rf build dist __queuestorage__ 2>/dev/null || true
git rm -rf *.egg-info .pytest_cache .mypy_cache 2>/dev/null || true
find . -type d -name __pycache__ -exec git rm -rf {} + 2>/dev/null || true

# Replace dev CONTRIBUTING with public version
if [ -f CONTRIBUTING.public.md ]; then
    git mv CONTRIBUTING.public.md CONTRIBUTING.md 2>/dev/null || true
fi

echo ""
echo "✅ Pruning complete!"
echo ""
echo "📊 Summary of changes:"
git status --short | head -20
echo ""
echo "📝 Next steps:"
echo "   1. Review changes: git status"
echo "   2. Verify no secrets: git log --all --full-history -- '*settings.json' '*api*key*'"
echo "   3. Commit: git commit -m 'Prepare public branch for release'"
echo "   4. Push: git push origin public"
