# Build with: python -m PyInstaller bench_app/SONIC_Bench.spec --noconfirm
from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

root = Path(SPECPATH).parent
a = Analysis([str(root / 'bench_app/desktop.py')], pathex=[str(root)],
    binaries=collect_dynamic_libs('_sounddevice_data'),
    datas=[(str(root / 'bench_app/ui'), 'bench_app/ui')]
        + [(str(root / 'bench_app/engine.py'), 'bench_app')]
        + [(str(root / 'latency' / name), 'latency')
           for name in ('stimulus.py', 'analysis.py', 'transport.py')]
        + collect_data_files('_sounddevice_data'),
    hiddenimports=['sounddevice', '_sounddevice_data'], hookspath=[], hooksconfig={},
    runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='SONIC Bench',
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False, disable_windowed_traceback=False)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='SONIC Bench')
if sys.platform == 'darwin':
    app = BUNDLE(coll, name='SONIC Bench.app', bundle_identifier='org.rice.sonicbench',
        info_plist={'NSMicrophoneUsageDescription': 'Record the selected microphone to measure sound delivery delay.',
                    'NSHighResolutionCapable': True})
