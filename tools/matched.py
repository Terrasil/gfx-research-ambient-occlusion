"""Compare candidates and controls on identical views, resolutions and timing blocks."""
from collections import defaultdict
from statistics import mean, median

from report import table


def comparison_key(row):
    return tuple(row[k] for k in ("scene", "view", "parameter", "width", "height", "budget", "method"))


def operating_points(quality, timing, primary, scenes):
    images = {comparison_key(row): row for row in quality}
    blocks = defaultdict(list)
    for row in timing:
        key = comparison_key(row)
        if key in images:
            blocks[(key, row["block"])].append(int(row["gpu_ns"]) / 1e6)
    block_times = defaultdict(list)
    for (key, _), values in blocks.items():
        block_times[key].append(median(values))
    points = []
    for key, times in sorted(block_times.items()):
        row = images[key]
        if row[primary] == "":
            continue
        scene, view, parameter, width, height, budget, method = key
        points.append(dict(scene=scene, view=view, parameter=parameter, width=width, height=height,
                           split="calibration" if scene in scenes else "held-out",
                           method=method, budget=int(budget), gpu_ms=median(times),
                           loss=float(row[primary]), timing_blocks=len(times)))
    return points


def pareto(points):
    out = []
    for point in sorted(points, key=lambda row: (row["gpu_ms"], row["loss"])):
        if not out or point["loss"] < out[-1]["loss"]:
            out.append(point)
    return out


def write_comparisons(folder, quality, timing, study, profile):
    ao = study["kind"] == "ao"
    metric = "edge_mae" if ao else "rgb_rmse"
    controls = study["study_controls"]
    calibration = study["calibration_scenes"]
    points = operating_points(quality, timing, metric, calibration)
    table(folder/"quality_cost.csv", points)
    held_out = defaultdict(list)
    for point in points:
        if point["split"] == "held-out":
            held_out[point["scene"]].append(point)
    if not held_out and profile == "smoke":
        return
    if not held_out:
        raise ValueError("No held-out quality/timing pairs at matching resolutions")

    tuned = {}
    if ao:
        fit = defaultdict(dict)
        for point in points:
            if point["split"] == "calibration" and point["method"] in controls:
                fit[(point["budget"], point["method"])][point["scene"]] = point["loss"]
        rows = [dict(budget=budget, method=method, calibration_loss=mean(values.values()))
                for (budget, method), values in fit.items() if set(values) == set(calibration)]
        for row in sorted(rows, key=lambda row: (row["calibration_loss"], row["method"])):
            tuned.setdefault(row["budget"], row["method"])
        for row in rows:
            row["selected"] = row["method"] == tuned[row["budget"]]
        table(folder/"calibrated_slabs.csv", rows)

    comparisons = []
    frontier = []
    for scene, values in sorted(held_out.items()):
        frontier.extend(pareto(values))
        if ao:
            baseline = [p for p in values if p["method"] in (tuned[p["budget"]], "horizon")]
        else:
            baseline = [p for p in values if p["method"] in controls]
        for point in values:
            if point["method"] not in study["study_candidates"]:
                continue
            comparable = [p for p in baseline if p["gpu_ms"] <= point["gpu_ms"]]
            best = min(comparable, key=lambda p: (p["loss"], p["gpu_ms"]), default=None)
            comparisons.append(dict(scene=scene, metric=metric, candidate=point["method"],
                                    budget=point["budget"], gpu_ms=point["gpu_ms"], loss=point["loss"],
                                    control=best["method"] if best else None,
                                    control_budget=best["budget"] if best else None,
                                    control_gpu_ms=best["gpu_ms"] if best else None,
                                    control_loss=best["loss"] if best else None,
                                    loss_delta=point["loss"]-best["loss"] if best else None))
    table(folder/"held_out_pareto.csv", frontier)
    table(folder/"held_out_matched_cost.csv", comparisons)
