# 0001-use-llm-vision-instead-of-ocr-pipeline

We skip a traditional OCR step (Tesseract, Google Vision, etc.) and send document images directly to GPT-4o for structured field extraction. The model reads the image and returns JSON in a single API call, combining OCR and structuring into one step.

This trades per-document cost (~$0.005) for dramatically simpler architecture: no OCR library, no preprocessing pipeline, no language detection, no post-OCR cleanup. For a 2-3 day demo with 3-10 documents, the cost is negligible. If this went to production at scale (thousands of docs/day), we'd revisit a dedicated OCR pipeline for cost efficiency.
