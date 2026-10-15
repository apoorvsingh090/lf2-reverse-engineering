# Little Fighter 2 — Reverse Engineering Notes

Target: **Little Fighter 2 v2.0a (11 Jul 2009)**, Marti Wong / Starsky Wong,
installed at `C:\Program Files (x86)\LittleFighter` (690 files, ~46 MB).
Analysis date: 2026-10-15. Status: **triaged and mapped, not fully reversed**
(~3 of 513 functions decompiled; game logic, netcode, `.lfr` codec remain open).

Toolchain: [REA](https://github.com/morluto/rea) (`rea-agents@6.5.0`) +
Ghidra 12.1.4 + Temurin JDK 21 on Windows x64 (experimental Windows P0).

## 1. Binary identification

`lf2.exe`: 3,424,256 bytes, SHA256
`12dfa00f6b767508612550e9ab27ab74b4201ff4cb9ff31d068925924eab8fc5`,
PE32 x86, image base `0x400000`, 4 sections (`.text/.rdata/.data/.rsrc`),
GUI subsystem, VS2005 + MFC 8.0.50727.762, no version info, no CLI metadata
(native, not .NET — see `evidence/managed-artifact.json`).

Imports: `DDRAW` (`DirectDrawCreate`), `DSOUND`, `WINMM` (`timeGetTime`),
`WSOCK32` (network VS play), `WININET` (`InternetOpenUrlA` — ads/updates),
`COMDLG32/SHELL32/ole32`. Embedded URLs point at `littlefighter.com` /
`lf2.net` (`/_ad/ad%s.bmp`, `/record`, `/challenge`).

## 2. Ghidra findings (see `evidence/ghidra/`)

* `analyze`: 6 segments, **513 procedures, 750 strings** (`01-overview.json`,
  snapshot `lf2-ghidra-snapshot.json`).
* `entry @0x445560`: `___security_init_cookie(); ___tmainCRTStartup();`
  (`03-search-entry.json`, `08-function-entry-0x4103f8.json` pattern).
* `___tmainCRTStartup` (VS2008): CRT init → WinMain **`FUN_0043cf40`**
  (`06-decompile-tmainCRTStartup.json`).
* `FUN_0043cf40 @0x43cf40` (`07-decompile-winmain.json`): `srand(timeGetTime)`,
  `CoInitialize`, init chain `0043bec0/c4a0/c780/cc60`, DirectSound init,
  preload of `m_join/m_ok/m_cancel/m_pass/m_end.wav`, then a
  `PeekMessage`/`GetMessage` loop with `timeGetTime` pacing (3 ms / 33 ms
  branches) ticking `FUN_0043e9a0`.
* DC data parser: `<frame>` strings at `0x4480d0`/`0x4485e0`
  (`04-search-frame.json`), referenced from `0x4103f8`/`0x410408`
  (`05-xrefs-frame-string.json`) inside **`FUN_0040ef70`** (~13 KB,
  `0x40ef70–0x4122e9`).
* `DirectDrawCreate` / `DirectDraw Init FAILED` at `0x44bb66`/`0x449f30`
  (`02-search-directdraw.json`).
* PE resources: 67 entries — `MENU_BACK1–13`, `MENU_CLIP*`, `BATTLEMODE`,
  `CHARMENU`, icon group (`evidence/pe-resources.json`).

## 3. Data files (see `evidence/decoded/`, `tools/decode_lf2_dat.py`)

`data/*.dat` and `bg/**/bg.dat` are encrypted: 123-byte header + repeating
Caesar key `odBearBecauseHeIsVeryGoodSiuHungIsAGo` (byte `wrapping_sub`).
`data/data.txt` is the plaintext object registry (`id/type/file`).

* `decoded/davis.txt` — fighter definition: sprite sheets, speeds, jump/dash
  physics, `<frame>` blocks with `pic/state/wait/next/dvx/dvy/dvz`,
  `bdy` hitboxes, `wpoint` weapon binds.
* `decoded/stage.txt` — Survival stage: phase bounds, enemy `id/hp/times/ratio`,
  `<boss>`/`<soldier>` waves, `bgm\*.wma` cues.
* `decoded/bg-template1.txt` — parallax layers (`width/x/y/transparency`).
* `file-inventory.txt` — all 690 installed files with sizes.

## 4. Assets / misc

* `sprite/sys/`: per-character `_*0/1/2.bmp + _f/_s.bmp` plus pre-rendered
  `*_mirror.bmp` (GeForce 9800 DirectDraw-mirror fix, cf. `readme.txt`).
* `bg/sys/{bc,cuhk,ft,gw,hkc,lf,qi,sp,thv}/` + `bg/template/{1,2,3}/`;
  `bgm/8×*.wma`; `data/001–102.wav` + `m_*.wav` UI sounds.
* `recording/`: 10 demo `.lfr` replays (proprietary binary, version- and
  data-file-checked) + `lfr_summary_generator.exe` (VC80 tool emitting
  `lfr_summary.csv` with P1–P8 kill/attack/hp/mp stats).

## 5. Reproduce

```bash
# decode a data file
python tools/decode_lf2_dat.py decode "C:\Program Files (x86)\LittleFighter\data\davis.dat" davis.txt

# REA (needs GHIDRA_INSTALL_DIR + JDK 21)
export GHIDRA_INSTALL_DIR=/absolute/path/to/ghidra_12.1.4_PUBLIC
rea analyze  "C:\Program Files (x86)\LittleFighter\lf2.exe" --provider ghidra --json
rea decompile "C:\Program Files (x86)\LittleFighter\lf2.exe" 0x43cf40 --provider ghidra --json
```

Pseudocode is Ghidra decompiler output, not original source. For lawful
research / interoperability on your own copy only.
