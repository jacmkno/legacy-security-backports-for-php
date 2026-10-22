# Legacy PHP security backports

Prepared PHP 7.0/7.2 source and build records for maintaining existing Ubuntu Xenial installations. The packages were deployed successfully in observed production checks on 21 October 2026.

## Contents

- [Source branches](#source-branches)
- [Compilation](#compilation)
- [Verification](#verification)
- [Provenance and licenses](#provenance-and-licenses)

## Source branches

Each branch has exactly two commits and an independent root history: **distribution baseline**, then **security adaptation**. The baseline includes upstream source and the distribution's pre-existing fixes, so those historical changes are distinguishable from the new adaptation.

| Branch | Baseline | Patched package |
|---|---|---|
| [php-7.0-ubuntu16.04](https://github.com/jacmkno/legacy-security-backports-for-php/tree/php-7.0-ubuntu16.04) | `7.0.33-0ubuntu0.16.04.16` | `7.0.33-0ubuntu0.16.04.16+community1` |
| [php-7.0-sury-xenial](https://github.com/jacmkno/legacy-security-backports-for-php/tree/php-7.0-sury-xenial) | `7.0.33-37` distribution recipe | `7.0.33-37+ubuntu16.04.1+deb.sury.org+1+community2` |
| [php-7.2-sury-xenial](https://github.com/jacmkno/legacy-security-backports-for-php/tree/php-7.2-sury-xenial) | `7.2.34-8` distribution recipe | `7.2.34-8+ubuntu16.04.1+deb.sury.org+1+community2` |

The second commit isolates CVE-2026-109618/CVE-2026-109619 changes, generated Zend VM headers, quilt records and the package revision. Review it with `git diff HEAD^ HEAD -- Zend main ext debian`. Quilt before-images/state are preserved in `.pc/`; GitHub marks these and generated VM headers as generated. PHP's original README is retained as `README.upstream.md`.

Source snapshots were read from completed build directories. Original quilt before-images and changelogs establish the pre-adaptation baselines. Compiler output, staged packages, temporary test results and private deployment records are excluded.

## Compilation

Builds used Linux amd64 Ubuntu 16.04 containers, two CPUs and approximately 1536 MB RAM per build. The recorded base was:

```text
ubuntu:16.04@sha256:1f1a2d56de1d604801a9671f301190704c25d604a416f59e03c04f5c6ffee0d6
```

Builder inventories are in [build-records](build-records/); each source branch includes its corresponding `build-records/packages.tsv`.

- Ubuntu 7.0 used Xenial libraries, debhelper 9, dh-autoreconf 11 and OpenSSL 1.0.2g.
- Sury used debhelper `10.2.2ubuntu1~ubuntu16.04.1`, dh-autoreconf `12~ubuntu16.04.1`, libzip 1.7.3, libsodium 1.0.16, tidy 5.6.0 and OpenSSL 1.1.1g development inputs. ICU 65.1, PCRE 8.41 and Argon2 2019 supplied the final aligned builds.
- Historical dependency recipes were built with `dpkg-buildpackage`; ICU used `-B`, the others `-b`. Mandoc was used while building libzip. [PROVENANCE.md](PROVENANCE.md) records source versions, publications and checksums.
- OpenSSL dependency certificate fixtures required a process-scoped historical wall clock for that dependency's tests. Its legacy libfaketime monotonic override was ineffective. PHP compilation and production used the real clock.

Inside the matching dependency environment:

```sh
git clone --single-branch --branch php-7.2-sury-xenial \
  https://github.com/jacmkno/legacy-security-backports-for-php.git php-source
cd php-source
dpkg-checkbuilddeps
DEB_BUILD_OPTIONS=parallel=2 dpkg-buildpackage -b -us -uc -j2
```

Choose the corresponding source branch for PHP 7.0. The prepared source already has its quilt series applied and VM headers generated. DEBs and `.changes` land in the parent directory. Historical dependency availability remains necessary; a fresh end-to-end builder reconstruction or byte-identical package reproduction has not been demonstrated.

For the next fix, create a work branch from the matching distribution/version branch, import the patch into the quilt series, update `debian/changelog`, and rebuild in the recorded environment. If VM generator inputs changed, regenerate its VM headers with a matching-branch PHP CLI and include them in the patch. Retain previous installed packages/configuration for rollback and verify the actual serving runtime after its service transition.

## Verification

Production observations covered Ubuntu 16.04 amd64 with Apache 2.4 prefork/mod_php plus PHP 7.0 FPM, and event/proxy_fcgi with PHP 7.2 and additional PHP 7.0 FPM pools. Checked HTTP paths operated normally following the final deployments; configuration, extensions and aligned ICU 65.1 were retained. These are bounded deployment observations, not a long-term workload guarantee.

The 11 focused CLI/FPM probes cover OOM termination, normal VM/input behavior, session/upload handling and multipart retention. Both installed Sury branches passed all 11; the Ubuntu candidate passed the suite in prior installed-runtime verification. Multipart retention had negative controls. Dependency/configuration checks, rollback and application smoke checks were exercised.

Inherited complete PHP suites ran during the original builds and were **not clean**:

| Build | Tests | Passed | Skipped | Failed | Expected failures | Warnings |
|---|---:|---:|---:|---:|---:|---:|
| Ubuntu 7.0 community1 | 14,971 | 12,339 | 2,494 | 94 | 38 | 6 |
| Aligned Sury 7.0 community2 | 14,983 | 12,114 | 2,484 | 341 | 38 | 6 |
| Aligned Sury 7.2 community2 | 16,012 | 12,854 | 2,818 | 304 | 35 | 1 |

Many earlier failures reproduced on original runtimes or involved expired fixtures/environment differences. Every final aligned failure has not been classified. Recipe exit zero is not full-suite approval because inherited test commands can mask failures through `tee`.

Additional proposed work remains incomplete: clean public-repository rebuild/reproducibility; exhaustive failure/skip classification; interrupted non-OOM request cleanup followed by an early FPM diagnostic in the same worker with a meaningful control; synthetic arithmetic/huge-size/concatenation boundary probes; comprehensive application workflows, load testing and extended production observation. Earlier delegated attempts at additional security probes were restricted by the execution platform.

No PHP tests or recompilation were run for publication or the history rewrite. Publication checks concern source provenance, Git diffs and removal of deployment-specific information.

## Provenance and licenses

[PROVENANCE.md](PROVENANCE.md) records archive hashes, signing-key references and dependency publications. The original legacy patch credits Arnaud Le Blanc and Ilija Tovilo. PHP/Zend and distribution licenses remain with the source; new maintenance documentation/scripts use the main-branch MIT license where identified.

This product includes PHP software, freely available from <http://www.php.net/software/>, and the Zend Engine, freely available at <http://www.zend.com>.
