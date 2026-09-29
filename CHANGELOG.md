# Changelog

Release history is managed by Release Please and published in GitHub Releases.
## [2.7.0](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.6.0...v2.7.0) (2026-09-29)


### Features

* **ai:** default to OpenRouter GPT-6 Luna ([eaff504](https://github.com/EvickaStudio/Moodle-Mate/commit/eaff504472ae4489796703ced32caa9f3ce720be))
* **ai:** use OpenRouter GPT-6 Luna by default ([1da790b](https://github.com/EvickaStudio/Moodle-Mate/commit/1da790b7ddd47301c1942d9d60d5e4e80f7ddd95))
* **web:** redesign dashboard with split inbox ([6589964](https://github.com/EvickaStudio/Moodle-Mate/commit/65899644afbd572d01a223f588fbc8803900ace9))


### Bug Fixes

* **ai:** initialize custom endpoint authentication correctly ([#128](https://github.com/EvickaStudio/Moodle-Mate/issues/128)) ([84a9644](https://github.com/EvickaStudio/Moodle-Mate/commit/84a9644a999ba4a1133881ce8729828cdba5f603))
* **ai:** use supported GPT-5 completion parameters ([#127](https://github.com/EvickaStudio/Moodle-Mate/issues/127)) ([d290a29](https://github.com/EvickaStudio/Moodle-Mate/commit/d290a29f392fba70ce0d62faa81cdc5ff710c570))
* **build:** avoid duplicate wheel assets ([fbe0f2e](https://github.com/EvickaStudio/Moodle-Mate/commit/fbe0f2e4fd32a1db83fd7f2acc03b4791103bd1b))
* **build:** avoid duplicate wheel assets ([f37a50c](https://github.com/EvickaStudio/Moodle-Mate/commit/f37a50c37b2340b01b21d842527a4fe4dcc531f0))
* **config:** apply dashboard changes to active components ([#125](https://github.com/EvickaStudio/Moodle-Mate/issues/125)) ([3491a4e](https://github.com/EvickaStudio/Moodle-Mate/commit/3491a4ecd852252a07589f9a75a3ff73370faa8d))
* **deps:** export hashed development requirements from lockfile ([#131](https://github.com/EvickaStudio/Moodle-Mate/issues/131)) ([d1c8e16](https://github.com/EvickaStudio/Moodle-Mate/commit/d1c8e16ef6e5bcbd8992fca6ab74c720ce6115b4))
* **docker:** expose the authenticated dashboard on host localhost ([#130](https://github.com/EvickaStudio/Moodle-Mate/issues/130)) ([3976259](https://github.com/EvickaStudio/Moodle-Mate/commit/39762594a9fffbc6b48b95fa51b4f699ae9ea685))
* **health:** acknowledge alerts only after successful delivery ([#129](https://github.com/EvickaStudio/Moodle-Mate/issues/129)) ([aa0f589](https://github.com/EvickaStudio/Moodle-Mate/commit/aa0f58927dc0fc9a7f0c7473c1275371d22fa8ff))
* **logging:** keep console colors out of file records ([#138](https://github.com/EvickaStudio/Moodle-Mate/issues/138)) ([f4b15be](https://github.com/EvickaStudio/Moodle-Mate/commit/f4b15be516615365bafed037b7247416c82ba140))
* **markdown:** deliver complex HTML with a safe text fallback ([#124](https://github.com/EvickaStudio/Moodle-Mate/issues/124)) ([48df6e6](https://github.com/EvickaStudio/Moodle-Mate/commit/48df6e6ff42a1bf1af1b6c33c563e0eef8766098))
* **moodle:** deliver initial notifications oldest first ([fc0da39](https://github.com/EvickaStudio/Moodle-Mate/commit/fc0da39a14996bb72fef99d79bc7104aefb00edd))
* **moodle:** deliver initial notifications oldest first ([2a9370d](https://github.com/EvickaStudio/Moodle-Mate/commit/2a9370dd493f4f6478a221b70ea1304422b06f5d))
* **moodle:** keep credentials out of request diagnostics ([#123](https://github.com/EvickaStudio/Moodle-Mate/issues/123)) ([7764924](https://github.com/EvickaStudio/Moodle-Mate/commit/77649242c093927a16baa7192d04ced81bdbf2eb))
* **moodle:** propagate failed notification polls ([0d36df5](https://github.com/EvickaStudio/Moodle-Mate/commit/0d36df5a2f3f7218207b8c8215ed6198c85f4e62))
* **moodle:** propagate failed notification polls ([3834dce](https://github.com/EvickaStudio/Moodle-Mate/commit/3834dcea4823ff9ff1d0d3164538cc10d3846d7f))
* **moodle:** retain notification metadata for filters and history ([#126](https://github.com/EvickaStudio/Moodle-Mate/issues/126)) ([f466836](https://github.com/EvickaStudio/Moodle-Mate/commit/f466836c8a3a4926d68795274eaf7dd2de78d14b))
* **notifications:** preserve initial retry window across restarts ([#137](https://github.com/EvickaStudio/Moodle-Mate/issues/137)) ([7c4907b](https://github.com/EvickaStudio/Moodle-Mate/commit/7c4907bf16cdec5b0586b31c2c0ff91e1971f661))
* **notifications:** retry incomplete provider delivery ([38def46](https://github.com/EvickaStudio/Moodle-Mate/commit/38def46ac5482256c10c68da927cedd2219257f3))
* **notifications:** retry incomplete provider delivery ([e0d76df](https://github.com/EvickaStudio/Moodle-Mate/commit/e0d76df088606a3e4a836fbf9686f612489e0f1a))
* **runtime:** honor prepared session and log paths ([#132](https://github.com/EvickaStudio/Moodle-Mate/issues/132)) ([da06c67](https://github.com/EvickaStudio/Moodle-Mate/commit/da06c6732872b73617b8c2fb5e8dcfd9f6289024))
* **startup:** defer Moodle login until polling begins ([#136](https://github.com/EvickaStudio/Moodle-Mate/issues/136)) ([61599c8](https://github.com/EvickaStudio/Moodle-Mate/commit/61599c88214a3f58c866e9b57d6c948adbf6952b))
* **web:** escape quotes in dashboard Markdown links ([#121](https://github.com/EvickaStudio/Moodle-Mate/issues/121)) ([8c13f18](https://github.com/EvickaStudio/Moodle-Mate/commit/8c13f18e105f2f3495024ae63b83fcc7bdcc1fbb))
* **web:** redact and freeze session encryption key ([#134](https://github.com/EvickaStudio/Moodle-Mate/issues/134)) ([e81450f](https://github.com/EvickaStudio/Moodle-Mate/commit/e81450f77ff227f3373fed92e4e8990f2df9942b))


### Refactoring

* remove redundant type conversions ([9f1a160](https://github.com/EvickaStudio/Moodle-Mate/commit/9f1a1602b0e1cc2db2e1fcfb556778d61a69d011))
* remove redundant type conversions ([5102557](https://github.com/EvickaStudio/Moodle-Mate/commit/5102557d7d49ebdd63e4b5434bfc70cb9f1e67a0))


### Documentation

* **config:** clarify native and Docker runtime paths ([#133](https://github.com/EvickaStudio/Moodle-Mate/issues/133)) ([bb86ab1](https://github.com/EvickaStudio/Moodle-Mate/commit/bb86ab122533a6f3329c44b2d9e3dc9344f7c22e))
* **readme:** refresh preview screenshots ([309753e](https://github.com/EvickaStudio/Moodle-Mate/commit/309753e102a2ac69c757bc89e209574931aa2749))
* **readme:** refresh screenshots ([9e6f010](https://github.com/EvickaStudio/Moodle-Mate/commit/9e6f010232d6ce3809107c4e99c69a10ac99e22b))
* update provider and module examples to current APIs ([#135](https://github.com/EvickaStudio/Moodle-Mate/issues/135)) ([bebbb72](https://github.com/EvickaStudio/Moodle-Mate/commit/bebbb72d4a2d3513cfecd1bb5e11f7988f79bfb6))

## [2.6.0](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.5.1...v2.6.0) (2026-08-19)


### Features

* **web:** redesign dashboard and login experience ([a58c312](https://github.com/EvickaStudio/Moodle-Mate/commit/a58c312dde35ab6a30803970cd33bbbbf98959db))


### Bug Fixes

* address review comments on server shutdown, web UI, and OpenAI client ([2b77edf](https://github.com/EvickaStudio/Moodle-Mate/commit/2b77edf0eb71dee326fc35db90e7cf882cc45e12))

## [2.5.1](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.5.0...v2.5.1) (2026-07-11)


### Bug Fixes

* **docker:** keep secrets and state outside images ([b79be76](https://github.com/EvickaStudio/Moodle-Mate/commit/b79be76ac79d80c44525957c86531342cee1f2a9))
* **logo:** replace logo.svg with icon.svg in login template ([e9289e1](https://github.com/EvickaStudio/Moodle-Mate/commit/e9289e18f831cea520ebe10e5d6300249421cd5c))
* **reliability:** harden unattended server operation ([27db6d8](https://github.com/EvickaStudio/Moodle-Mate/commit/27db6d800d8b45a9dce73c262021f7bfb28270c2))

## [2.5.0](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.4.0...v2.5.0) (2026-05-07)


### Features

* **markdown:** enhance pseudo-list handling and improve bold marker cleanup ([ee6a621](https://github.com/EvickaStudio/Moodle-Mate/commit/ee6a62199cae7f60824ee3c43274f1ebb2d5cbba))
* **type-checking:** integrate Pyrefly for static type checking and update documentation ([8800873](https://github.com/EvickaStudio/Moodle-Mate/commit/8800873357ea981e1aca30d052e6277d2ec79437))


### Bug Fixes

* **markdown:** compact notification list spacing and cleanup ([55e5449](https://github.com/EvickaStudio/Moodle-Mate/commit/55e54490919746bfe1292500ade75d9a9c9e3481))
* **markdown:** compact notification list spacing and cleanup ([0133bb3](https://github.com/EvickaStudio/Moodle-Mate/commit/0133bb3b8d3e0275adb485f021eb22d320e64e9b))

## [2.4.0](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.3.0...v2.4.0) (2026-02-23)


### Features

* **moodle:** process newest notifications as ordered batches ([ad05637](https://github.com/EvickaStudio/Moodle-Mate/commit/ad05637ef3fcedbb059fe049c0f0207f9eaa22ea))


### Bug Fixes

* **moodle:** harden site info parsing and pass pyright ([48064e4](https://github.com/EvickaStudio/Moodle-Mate/commit/48064e44fc0edaf8a7d3051a71ad8d09d51ba4cc))

## [2.3.0](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.2.4...v2.3.0) (2026-02-09)


### Features

* **make:** add sync-dev upgrade and export workflow ([7486757](https://github.com/EvickaStudio/Moodle-Mate/commit/7486757fc6c0941d4a462c6e095ae12b5bcaeeaa))


### Bug Fixes

* **deps:** pin zipp to patched version ([c7f2d27](https://github.com/EvickaStudio/Moodle-Mate/commit/c7f2d275bb3cb1a78577c6066a2eeea7d70c0eff))


### Documentation

* **release:** add changelog conflict prevention sync steps ([91bef0e](https://github.com/EvickaStudio/Moodle-Mate/commit/91bef0ed02aefea162e5c134d1f5c7c018abbfc7))

## [2.2.4](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.2.3...v2.2.4) (2026-02-07)


### Documentation

* **agents:** enforce make-based commit and release branch flow ([c7e38fc](https://github.com/EvickaStudio/Moodle-Mate/commit/c7e38fc419d7d87e196e79641f220f316b150277))
* **core:** update inline docs and remove legacy ai guide ([3c2bb83](https://github.com/EvickaStudio/Moodle-Mate/commit/3c2bb830ac4298e8769d950aa68a639b4d1d7751))
* **readme:** refresh setup and usage wording ([5260cdf](https://github.com/EvickaStudio/Moodle-Mate/commit/5260cdf15d2e4d2fc84356d073bcaeb202252183))
* **release:** switch verification commands to gh cli ([efca14a](https://github.com/EvickaStudio/Moodle-Mate/commit/efca14a85bc9a13b8dd04f00435f435d268f7889))

## [2.2.3](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.2.2...v2.2.3) (2026-02-07)


### Bug Fixes

* **security:** pin patched filelock and virtualenv in dev deps ([16c4b30](https://github.com/EvickaStudio/Moodle-Mate/commit/16c4b305583d1d4fe0a0be740c74f43ab0d20c68))


### Documentation

* **release:** add agent-ready release runbook ([662ab10](https://github.com/EvickaStudio/Moodle-Mate/commit/662ab1016705b96a5c080c1b5ff33b2f188e3633))

## [2.2.2](https://github.com/EvickaStudio/Moodle-Mate/compare/v2.2.1...v2.2.2) (2026-02-07)


### Bug Fixes

* **metadata:** correct grammar in project descriptions ([d85a860](https://github.com/EvickaStudio/Moodle-Mate/commit/d85a860a375ed625ebef552a68cde7419dffc6d1))
