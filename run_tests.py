#!/usr/bin/env python3
"""
Script de lancement des tests automatisés pour MagikSwipe Backend API.

Usage:
    python run_tests.py                    # Tous les tests
    python run_tests.py --universes       # Tests univers seulement
    python run_tests.py --music           # Tests musique seulement
    python run_tests.py --assets          # Tests assets seulement
    python run_tests.py --generation      # Tests génération (avec mocks)
    python run_tests.py --jobs-sync       # Tests jobs et sync
"""

import subprocess
import sys
import argparse


def run_tests(test_pattern=None, verbose=True):
    """Lance les tests avec pytest."""

    cmd = [sys.executable, "-m", "pytest"]

    if test_pattern:
        if test_pattern == "universes":
            cmd.append("tests/test_universes.py")
        elif test_pattern == "music":
            cmd.append("tests/test_music_prompts.py")
        elif test_pattern == "assets":
            cmd.append("tests/test_assets.py")
        elif test_pattern == "generation":
            cmd.append("tests/test_generation.py")
        elif test_pattern == "jobs-sync":
            cmd.append("tests/test_jobs_sync.py")
    else:
        cmd.append("tests/")

    if verbose:
        cmd.append("-v")

    cmd.extend(["--tb=short", "--color=yes"])

    print(f"🚀 Lancement des tests: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(" ".join(cmd), shell=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest n'est pas installé. Installez-le avec:")
        print("   pip install pytest httpx pytest-asyncio pytest-cov")
        return False


def main():
    parser = argparse.ArgumentParser(description="Lance les tests automatisés")
    parser.add_argument(
        "--universes",
        action="store_const",
        const="universes",
        help="Tests univers seulement"
    )
    parser.add_argument(
        "--music",
        action="store_const",
        const="music",
        help="Tests musique seulement"
    )
    parser.add_argument(
        "--assets",
        action="store_const",
        const="assets",
        help="Tests assets seulement"
    )
    parser.add_argument(
        "--generation",
        action="store_const",
        const="generation",
        help="Tests génération seulement"
    )
    parser.add_argument(
        "--jobs-sync",
        action="store_const",
        const="jobs-sync",
        help="Tests jobs et sync seulement"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Mode silencieux"
    )

    args = parser.parse_args()

    # Déterminer le pattern de test
    test_pattern = None
    if args.universes:
        test_pattern = "universes"
    elif args.music:
        test_pattern = "music"
    elif args.assets:
        test_pattern = "assets"
    elif args.generation:
        test_pattern = "generation"
    elif args.jobs_sync:
        test_pattern = "jobs-sync"

    # Lancer les tests
    success = run_tests(test_pattern, not args.quiet)

    if success:
        print("\n✅ Tous les tests sont passés !")
        sys.exit(0)
    else:
        print("\n❌ Certains tests ont échoué.")
        sys.exit(1)


if __name__ == "__main__":
    main()