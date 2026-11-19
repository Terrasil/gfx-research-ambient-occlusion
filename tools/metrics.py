import numpy as np

def masks(pos, normal, ref_diag):
    ids = pos[...,3]
    edge = np.zeros(ids.shape, bool)
    for axis in (0,1):
        lower = ids[:-1] if axis == 0 else ids[:,:-1]
        upper = ids[1:] if axis == 0 else ids[:,1:]
        diff = (lower != upper) & ((lower >= 2) | (upper >= 2))
        if axis == 0:
            edge[:-1] |= diff
            edge[1:] |= diff
        else:
            edge[:,:-1] |= diff
            edge[:,1:] |= diff
    h,w = ids.shape
    y,x = np.ogrid[:h,:w]
    border = (x+.5 < .05*w) | (x+.5 > .95*w) | (y+.5 < .05*h) | (y+.5 > .95*h)
    return dict(valid=ids>0, edge=edge & (ids>0), contact=(normal[...,3]>.5), border=border & (ids>0))

def summarize(signal, diag, reference, region, refdiag):
    delta = signal-reference
    valid = region["valid"]
    result = dict(rmse=float(np.sqrt(np.mean(delta[valid]**2))), bias=float(delta[valid].mean()),
                  probes_per_pixel=float(diag[...,1][valid].mean()), support_pairs=float(diag[...,2][valid].mean()))
    for name, mask in region.items():
        result[name+"_pixels"] = int(mask.sum())
        result[name+"_overdark"] = float(np.maximum(-delta[mask],0).mean()) if mask.any() else None
        result[name+"_mae"] = float(np.abs(delta[mask]).mean()) if mask.any() else None
    return result

def pixel_error(signal, reference):
    return np.abs(signal-reference)

def reference_check(reference, region, shifts, refdiag, scene):
    if not region["valid"].any(): raise ValueError("No AO receivers")
    if reference.min()<0 or reference.max()>1: raise ValueError("Invalid reference accessibility")
    if scene==4 and not np.allclose(reference[region["valid"]],1,atol=1e-6):
        raise ValueError("Isolated-plane reference failed")
    v = region["valid"]
    return {"reference_split_rmse":float(np.sqrt(np.mean((shifts[0][v]-shifts[1][v])**2)))}

def method_check(signal, diag, reference, region, scene):
    if signal.min() < -1e-6 or signal.max() > 1.000001: raise ValueError("AO outside unit range")
    if scene==4 and not np.allclose(signal[region["valid"]],1,atol=1e-5):
        raise ValueError("Isolated-plane method failed")

def region_image(region):
    return np.stack([region[k] for k in ("edge","contact","border")],axis=-1).astype("uint8")*255
