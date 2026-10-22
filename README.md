# Prepared legacy PHP source

This branch has two commits: the distribution baseline before the community adaptation, then the CVE-2026-109618/CVE-2026-109619 changes and corresponding VM, quilt and package-version records.

Review the isolated change with `git diff HEAD^ HEAD -- Zend main ext debian`. Original PHP documentation is retained as `README.upstream.md`; its license remains `LICENSE`. Quilt before-images/state are preserved in `.pc/` and marked generated in GitHub's diff view.

Build in the matching Ubuntu 16.04 amd64 dependency environment:

```sh
dpkg-checkbuilddeps
DEB_BUILD_OPTIONS=parallel=2 dpkg-buildpackage -b -us -uc -j2
```

The source already has its quilt series applied. Packages land in the parent directory. `debian/changelog` identifies this branch's package revision and `build-records/packages.tsv` records its builder. For another fix, import the patch into quilt, update the package revision, regenerate VM headers with matching PHP if needed, and compile in that environment.

See the [main README](https://github.com/jacmkno/legacy-security-backports-for-php/blob/main/README.md) for dependencies, verification and remaining gaps. [Provenance and checksums](https://github.com/jacmkno/legacy-security-backports-for-php/blob/main/PROVENANCE.md) are maintained on `main`.
