#!/usr/bin/env python3
# Author: Patrice Vigier (MIT License)
# Reorder KiCad 6/7/8/9 schematic symbol properties across .kicad_sch files
# by line-level manipulation of `(property "Name" "Value" ...)` within `(symbol ...)` blocks.

#Run in powershell or command window
# Dry run exemple
# python3 D:\KiCAD\Scripts\reorder_symbol_fields_schematics.py "D:\KiCAD\Projets\MIDI-VLR\VLR-08-2025" --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" --unlisted after --dry-run

# Hard run and create a .bak
# python3 D:\KiCAD\Scripts\reorder_symbol_fields_schematics.py "C:\Projets\MonProjet" `
  # --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" `
  # --unlisted after

# If only one file to modify
# python3 D:\KiCAD\Scripts\reorder_symbol_fields_schematics.py "C:\Projets\MonProjet\schema1.kicad_sch" --order "MPN,LCSC"


import argparse, re
from pathlib import Path

RE_SYM_START   = re.compile(r'^\s*\(symbol\b')
RE_PROP_START  = re.compile(r'^\s*\(property\s+"([^"]+)"\s+"([^"]*)"', re.UNICODE)
RE_OPEN        = re.compile(r'\(')
RE_CLOSE       = re.compile(r'\)')

def norm(s): return (s or "").strip().lower()

def find_block_end(lines, start):
    depth = 0
    i = start
    while i < len(lines):
        depth += len(RE_OPEN.findall(lines[i]))
        depth -= len(RE_CLOSE.findall(lines[i]))
        if depth == 0:
            return i
        i += 1
    return len(lines) - 1

def find_symbol_bounds(lines):
    i = 0
    out = []
    while i < len(lines):
        if RE_SYM_START.match(lines[i]):
            j = find_block_end(lines, i)
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out

def extract_properties(lines, s0, s1):
    """Returns: props=[{name,start,end,text}], first_idx or None"""
    i = s0
    props = []
    first_idx = None
    while i <= s1:
        m = RE_PROP_START.match(lines[i])
        if m:
            end = find_block_end(lines, i)
            props.append({
                "name": m.group(1),
                "start": i,
                "end": end,
                "text": lines[i:end+1],
            })
            if first_idx is None:
                first_idx = i
            i = end + 1
        else:
            i += 1
    return props, first_idx

def reorder(props, wanted, unlisted_where):
    by = {norm(p["name"]): p for p in props}
    listed = []
    for w in wanted:
        p = by.get(norm(w))
        if p:
            listed.append((p["name"], p["text"]))
    listed_set = {norm(n) for n,_ in listed}
    rest = [(p["name"], p["text"]) for p in props if norm(p["name"]) not in listed_set]
    return (rest + listed) if unlisted_where == "before" else (listed + rest)

def process_file(path: Path, wanted, unlisted="after", verbose=False, dry=False):
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines(keepends=True)
    changed_any = False

    # Iterate through each symbol independently
    for (s0, s1) in find_symbol_bounds(lines):
        # 1) extract all properties
        props, first_idx = extract_properties(lines, s0, s1)
        if not props or first_idx is None:
            continue

        before = [p["name"] for p in props]
        ordered = reorder(props, wanted, unlisted)
        after = [n for n,_ in ordered]
        if [norm(x) for x in before] == [norm(x) for x in after]:
            continue  # nothing to do

        # 2) remove all property blocks from the symbol (starting from the end)
        for p in sorted(props, key=lambda x: x["start"], reverse=True):
            del lines[p["start"]:p["end"]+1]

        # 3) reinsert the reordered properties into the location of the first property block
        insert_at = first_idx
        for _, block in ordered:
            lines[insert_at:insert_at] = block
            insert_at += len(block)

        changed_any = True
        if verbose:
            print(f"  {path.name}: BEFORE={before}  AFTER={after}")

    if changed_any and not dry:
        bak = path.with_suffix(path.suffix + ".bak")
        try: bak.unlink()
        except: pass
        path.rename(bak)
        path.write_text("".join(lines), encoding="utf-8")

    return changed_any

def main():
    ap = argparse.ArgumentParser(description="Reorder multi-line symbol properties in KiCad schematics safely.")
    ap.add_argument("target")
    ap.add_argument("--order", required=True, help='Ex: "MPN,LCSC,MANUFACTURER,Datasheet,Note"')
    ap.add_argument("--unlisted", choices=["before","after"], default="after")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    wanted = [s.strip() for s in args.order.split(",") if s.strip()]
    tgt = Path(args.target)

    if tgt.is_file():
        ch = process_file(tgt, wanted, args.unlisted, args.verbose, args.dry_run)
        print(f"{tgt}: {'modified' if ch else 'no change'}")
    else:
        total = changed = 0
        for sch in tgt.rglob("*.kicad_sch"):
            total += 1
            if process_file(sch, wanted, args.unlisted, args.verbose, args.dry_run):
                changed += 1
        print(f"\nCompleted. Files scanned.: {total}, modified files: {changed}.")
        if changed and not args.dry_run:
            print(".bak backups have been created.")

if __name__ == "__main__":
    main()
