"""Static guardrails for the newly added rotational-support AO ablation."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
config=json.loads((root/'study.json').read_text())
assert config['methods'][:6] == ['slab-thin','slab-mid','slab-thick','local-support','horizon','pooled-support']
assert config['methods'][6] == 'rotational-support'
shader=(root/'shaders/effect.frag').read_text()
assert 'if(uMethod==6)' in shader and 'd0=neighborSupport' in shader
assert 'uMethod==3 || uMethod==5 || uMethod==6' in shader
print('AO rotational-support contract: PASS')
