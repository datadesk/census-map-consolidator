# census-consolidator

Combine Census blocks into new shapes.

### Installation

```bash
$ pipenv install census-consolidator
```

### Python usage

Pass your list of Census block GEOIDs into our class. Consolidate them. Write to disk.

```python
>>> your_block_list = ["060371976001008", "060371976001009"]
>>> from census_consolidator import BlockConsolidator
>>> c = BlockConsolidator(*your_block_list)
>>> c.consolidate()
>>> c.write("./your-new-shape.geojson")
```

### Shell usage

Create a text file with one Census block GEOID per row. Pipe in it. Pipe it out.

```bash
cat your-blocks.txt | census-consolidator > your-shape.geojson
```
