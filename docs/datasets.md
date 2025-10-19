# Dataset Notes

The project expects a curated slice of the DocVQA dataset. Because the raw dataset is large and governed by licensing terms, do not commit it to the repository.

1. Download the official DocVQA data from the competition or the original hosting provider.
2. Extract the relevant split to a local folder (e.g. `~/data/docvqa/raw`).
3. Use `scripts/prepare_dataset.py` to copy a manageable subset into your workspace:
   ```bash
   python scripts/prepare_dataset.py --source ~/data/docvqa/raw --destination assets/docvqa_subset --limit 200
   ```
4. (Optional) Create a `manifest.jsonl` file alongside the documents with entries like:
   ```json
   {"id": "invoice-001", "document_path": "invoice-001.pdf", "questions": ["What is the total due?"], "metadata": {"split": "dev"}}
   ```

Update your configuration to point `DOCVQA_DATASET_PATH` (or the config file) at the prepared subset directory.
