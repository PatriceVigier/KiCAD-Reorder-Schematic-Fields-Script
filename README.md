# 🧭 KiCad – Reorder Schematic Fields (single file **or** whole folder)

Reorders multi-line `(property "Name" "Value" …)` blocks inside `(symbol …)` blocks in KiCad `.kicad_sch` files.
Use it to standardize field display order (e.g., `MPN, LCSC, MANUFACTURER, Datasheet, Note`) across **one file** or **all schematics in a folder (recursively)**.

* **Scope:** one file you specify **or** all `.kicad_sch` under a directory.
* **Safety:** creates a `.bak` backup next to each modified file (unless `--dry-run`).
* **Compatibility:** KiCad 6/7/8/9 S-expression schematics (tested with KiCad 9).
* **Non-destructive:** does **not** change values, only the **order** of property blocks.

---

## ✨ What it does

* Locates each `(symbol …)` block.
* Collects every multi-line `(property "Name" "Value" …)` block inside the symbol.
* Reorders those property blocks to match your `--order` list (case-insensitive match for ordering).
* Keeps **unlisted** properties and places them either **before** or **after** your list (`--unlisted`).
* Leaves everything else (pins, graphics, Reference/Value positions, etc.) untouched.

> KiCad UI always shows **Reference** and **Value** first; their placement is not controlled by this tool.

---

## 📥 Installation

1. Save the script as `reorder_symbol_fields_schematics.py` anywhere you like (e.g. `C:\KiCAD\Scripts\`).
2. Ensure **Python 3.8+** is installed and available on your PATH.

---

## ▶️ Usage

### Reorder a **single file**

```bash
python3 reorder_symbol_fields_schematics.py "C:\Projects\MyProj\main.kicad_sch" --order "Field_A,Field_Z,Field_E,Field_W" --unlisted after
```
Note: Change "--order "Field_A,Field_Z,Field_E,Field_W"" as per your needs, all name are separated by a comma

### Reorder **all schematics in a folder (recursively)** 
⚠️ Warning: If you have backups of your project inside sub-directories,  
they will also be processed and modified by this script.  
To avoid unwanted changes, point the script only to the exact project folder  
or directly to the `.kicad_sch` file you want to modify.

```bash
python3 reorder_symbol_fields_schematics.py "C:\Projects\MyProj" --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" --unlisted after
```
Note: Change --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" as per your needs, all name are separated by a comma

### Dry run (no file is written, no .bak created)

```bash
python3 reorder_symbol_fields_schematics.py "D:\KiCAD\Projets\MIDI-VLR\VLR-08-2025" --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" --unlisted after --dry-run
```

### Show details per changed symbol

```bash
python3 reorder_symbol_fields_schematics.py "C:\Projects\MyProj\main.kicad_sch" --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" --unlisted before --verbose
```
Note: Change --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" as per your needs, all name are separated by a comma
#### Windows PowerShell examples to change the ENTIRE folder and subfolders containing a PCB file

```powershell
python "C:\ThePathWhereIsTheScript\Scripts\reorder_symbol_fields_schematics.py" `
  "C:\KiCAD\Projects\MyProject" `
  --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" `
  --unlisted after `
  --dry-run
```

#### Windows CMD examples

```cmd
python C:\ThePathWhereIsTheScript\Scripts\reorder_symbol_fields_schematics.py ^
  "C:\KiCAD\Projects\MyProject" ^
  --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" ^
  --unlisted after ^
  --dry-run
```

#### macOS / Linux examples

```bash
python3 ~/KiCAD/Scripts/reorder_symbol_fields_schematics.py \
  "~/KiCAD/Projects/MyProj/MyProj.kicad_sch" \
  --order "MPN,LCSC,MANUFACTURER,Datasheet,Note" \
  --unlisted after \
  --verbose
```

---

## 🔧 Arguments

* `target`
  Path to a **.kicad\_sch file** (single-file mode) **or** a **directory** (recursive mode).

* `--order "A,B,C,..."` **(required)**
  Comma-separated list defining the desired order (field names as they appear in your symbols).
  Ordering comparison is **case-insensitive**; output preserves original casing.

* `--unlisted {before|after}` *(default: `after`)*
  Where to place properties **not** listed in `--order`.

* `--verbose`
  Prints BEFORE → AFTER property-name lists per symbol that changed.

* `--dry-run`
  Simulate; no files are written and no `.bak` backups are created.

---

## 🔒 Safety & Backups

* For every **modified** file (when not in `--dry-run`), the script:

  1. Renames the original to `file.kicad_sch.bak`,
  2. Writes the reordered content to `file.kicad_sch`.

---

## ✅ Recommended workflow

1. **Close** the schematic in KiCad (avoid overwriting while open).
2. **Backup your project on a different folder (not in a subfolder)**
3. Run a **`--dry-run`** to preview the changes.
4. Run the command without `--dry-run` to apply.
5. Reopen in KiCad and verify the order in the Symbol Properties panel.

---

## 🧩 Notes & Limitations

* Field names must match what exists in the file (e.g., `MANUFACTURER` ≠ `Manufacturer`).
* The script targets **multi-line** `(property …)` blocks (the standard output KiCad writes).
* Only **property order** is changed; positions, visibility, and values are left as they are.
* Single-file vs folder behavior is determined automatically from the `target` path.

---

## 🩺 Troubleshooting

**“no change” but I expected modifications**

* Check exact field names (spelling & spacing).
* Use `--verbose` to see the BEFORE/AFTER per symbol.
* Confirm the symbols actually contain those fields.

**KiCad refuses to open the file**

* Restore the `.bak` beside the schematic.
* Share the error line/column and a small excerpt; we can refine the parser.

---

## 📜 License

MIT.

---
