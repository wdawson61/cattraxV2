# firmware

Zephyr via the **nRF Connect SDK (NCS)**, built as a *freestanding application*: the SDK is
installed once outside this repo (by nRF Connect for VS Code, e.g. under `~/ncs/<version>`), and
this folder holds only the application and the board definition. No Zephyr or west workspace
lives in the repo.

## Planned layout

```
firmware/
├── CMakeLists.txt  prj.conf  Kconfig     application
├── src/
├── sysbuild/  sysbuild.conf              MCUboot etc., when needed
├── boards/wdawson/cattrax/               custom board; Zephyr finds <app>/boards automatically
│   ├── board.yml
│   ├── cattrax_nrf54l10_cpuapp.dts  cattrax_nrf54l10_cpuapp-pinctrl.dtsi
│   ├── Kconfig.cattrax  Kconfig.defconfig  cattrax_nrf54l10_cpuapp_defconfig
│   └── board.cmake
├── drivers/  dts/bindings/               only if a part has no in-tree driver (e.g. TMAG3001)
└── tests/
```

Board revisions (`cattrax@1`, `@2`) cover respins rather than new board names.

## Setup (once per machine)

1. Install VS Code and the **nRF Connect for VS Code** extension pack.
2. In the extension: install a toolchain and the current NCS release. Record the version here
   and in CI.
3. Open `firmware/` as an application; build for `cattrax/nrf54l10/cpuapp` (or, before the board
   exists, `nrf54l15dk/nrf54l10/cpuapp`).

## To check when starting

- That the chosen NCS release includes Zephyr's LoRaWAN stack (loramac-node) for the SX1262.
- Driver status: nPM1300 (charger, bucks, GPIO), LIS2DW12, u-blox M10 over I2C, TMAG3001.
- Pin assignments come from `electrical/board/connections_nrf54l10.csv`.

NCS version: _not yet pinned_
