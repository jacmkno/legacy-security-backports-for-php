# Source provenance

The security scope is [USN-8948-2](https://ubuntu.com/security/notices/USN-8948-2), covering CVE-2026-109618 and CVE-2026-109619. Upstream's [security announcement](https://www.php.net/archive/2026.php) links the original advisory and legacy source backports.

## Canonical PHP 7.2 patch

Source package: `php7.2_7.2.24-0ubuntu0.18.04.17+esm14`.

| Artifact | SHA-256 |
|---|---|
| `php7.2_7.2.24-0ubuntu0.18.04.17+esm14.debian.tar.xz` | `d9fa6758d7bfd4ac5140f28300f35c7fa125198b53d81faac36a6f4f7b44392b` |
| `php7.2_7.2.24-0ubuntu0.18.04.17+esm14.dsc` | `2478122102155f7357b948e5b77b83f6f6d2b5111b2257f3134ac00cf03055e1` |
| Extracted `debian/patches/CVE-2026-109618_109619.patch` | `cac3e90484a4293597979442412abfa895189beef71a37037acfa5824c5d284c` |

Both archive checksums were checked against the `Checksums-Sha256` section of Canonical's Bionic ESM Infra source index. The compressed source index checksum matched its signed `InRelease`; `gpgv` verified that release using the Ubuntu ESM signing key, fingerprint `56F7650A24C9E9ECF87C4D8D4067E40313CB4B13`.

The patch preserves attribution to Arnaud Le Blanc and Ilija Tovilo. Its legacy strategy terminates immediately on memory exhaustion and disables session upload-progress handling, alongside request-state cleanup and parser/allocation hardening. Regression tests must account for these explicit behavior changes.

## Upstream release sources

Hashes are from PHP's HTTPS release metadata API (`https://www.php.net/releases/index.php?json&version=VERSION`).

| Source | SHA-256 |
|---|---|
| `https://museum.php.net/php7/php-7.2.34.tar.xz` | `409e11bc6a2c18707dfc44bc61c820ddfd81e17481470f3405ee7822d8379903` |
| `https://museum.php.net/php7/php-7.0.33.tar.xz` | `ab8c5be6e32b1f8d032909dedaaaa4bbb1a209e519abb01a52ce3914f9a13d96` |

## Packaging references

Historical Debian PHP packaging tags `debian/7.2.34-8` and `debian/7.0.33-37` are available from the [Debian PHP team repository](https://salsa.debian.org/php-team/php). Their Ubuntu PPA publication history confirms the corresponding Xenial package versions; the PPA source-file API returned no retained downloads for those PHP publications during this work. These recipes supplied the deployed Sury community builds; the source branches preserve their prepared trees. Current deployment environments and verification limits are summarized in [README.md](README.md).

## Distribution archive digests

SHA-256 values of the packaging archives retained during the original builds:

| Archive | SHA-256 |
|---|---|
| Ubuntu PHP 7.0 `.16` Debian archive | `a0a25ceec019a56252b3f6ee89593f31a3d0eed5e0518ff9d975fbaceccc1c1d` |
| Sury/Debian `7.0.33-37` packaging tag archive | `3bd1b5b87c1140093838ccefc63b10da57d7a1e583c8e078985a29ac5d4913cb` |
| Sury/Debian `7.2.34-8` packaging tag archive | `4d48656c8f569cd7940684f16dde1ffaf5caaf11fd6d2c5d8a87398629137d77` |

Source branch baseline commits preserve prepared distribution source before the community adaptation; second commits isolate that adaptation. Upstream release hashes above identify the pristine release inputs before distribution patches.

## Historical Xenial build dependencies

Launchpad's `sourceFileUrls` API retains the following exact dependency source packages. Their upstream and Debian archives were downloaded over HTTPS and matched every SHA-256 entry in the corresponding DSC. `gpgv` verified the DSC signatures using fingerprint `6A1AAD7AE5B401C6E259A7B257067BAA1314C7FC`, independently matched against the maintainer's [Launchpad key registry](https://api.launchpad.net/1.0/~ondrej/gpg_keys). Verification and remaining gaps are summarized in [README.md](README.md#verification).

| Source publication | DSC SHA-256 |
|---|---|
| [libzip 1.7.3-1+ubuntu16.04.1+deb.sury.org+2](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/11657548) | `863b19c45e219ac2bbbfc1ac4fb4699418cba1ef7612c9713b50728f23b2c2e5` |
| [libsodium 1.0.16-2+ubuntu16.04.1+deb.sury.org+3](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/8704352) | `7d32a4a741dd0a054b7a59bf4a899275aa21baff40f1c9dfadeb0f40e4b1213f` |
| [argon2 0~20161029-1+ubuntu16.04.1+deb.sury.org+1](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/8204643) | `659a0f011b401119f7bae332509bc3feccd18f72e55d86cb1510fe374ad5bb2b` |
| [OpenSSL 1.1.1g-1+ubuntu16.04.1+deb.sury.org+1](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/11198945) | `d6265dcb29b4a07978bdc1b0db669b57edf9ca9aa02ee52fd83a92a0df8e8398` |
| [tidy-html5 2:5.6.0-6+ubuntu16.04.1+deb.sury.org+2](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/9577589) | `d1b4361e380e8dd8b80529e732062760f1ea5b8bffb6e5b4a909f1163dadec0c` |
| [ICU 65.1-1+ubuntu16.04.1+deb.sury.org+1](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/11013374) | `bbe24500fe2f7f409c8d546592315669d55267bbd4a02fa719012923c2cd71f0` |
| [Argon2 0~20190702-0.1+ubuntu16.04.1+deb.sury.org+1](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/11657530) | `c87f3661d1aff057d18abef381f12ba89a2bb8eb588a73702e9d9c30340f8882` |
| [PCRE 2:8.41-4+ubuntu16.04.1+deb.sury.org+1](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/8767533) | `183bf67f24bce256c011f4278059fc620f24e57bd9d7cc87673d9af4f85f948f` |

The OpenSSL and tidy archives also match their DSC SHA-256 entries and have valid signatures from the same Sury key. OpenSSL 1.1.1g matches the development package listed in the [original PHP 7.2.34 Xenial build](https://launchpad.net/~ondrej/+archive/ubuntu/php/+build/20228588). It is a build dependency; deployment validation must check the resulting PHP binaries against the destination's existing libraries.

The [OpenSSL 1.1.1c Sury publication](https://api.launchpad.net/1.0/~ondrej/+archive/ubuntu/php/+sourcepub/10187660) returned no retained sources. A Debian snapshot candidate was authenticated but requires newer packaging tools; the retained Xenial 1.1.1g recipe supplies the historical build route instead.

ICU 65 was recovered from a publication marked `Deleted`; its `sourceFileUrls` still provides the original source, Debian archive and DSC. The DSC signature verified with the same Sury fingerprint, and both archives matched its signed SHA-256 section. This exact Xenial recipe requires debhelper 9 rather than the Debian snapshot recipe's debhelper 11. Its build supplies a route to align the candidate `intl` extension with the original runtime's ICU version; build and integration approval remain separate checks.
