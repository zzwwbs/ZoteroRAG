
import time
import tracemalloc
import logging
from pathlib import Path
import statistics

# Library imports
import pypdf
import pypdfium2
from pdfminer.high_level import extract_text as pdfminer_extract

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def benchmark_pypdf(path: Path) -> str:
    text = ""
    reader = pypdf.PdfReader(path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def benchmark_pdfminer(path: Path) -> str:
    return pdfminer_extract(path)

def benchmark_pypdfium2(path: Path) -> str:
    text = ""
    pdf = pypdfium2.PdfDocument(path)
    for page in pdf:
        textpage = page.get_textpage()
        text += textpage.get_text_range()
        textpage.close()
        page.close()
    pdf.close()
    return text

def run_benchmark(name, func, path, iterations=5):
    times = []
    peak_memories = []
    text_len = 0
    
    # Warmup
    try:
        func(path)
    except Exception as e:
        logger.error(f"{name} failed: {e}")
        return None

    for _ in range(iterations):
        tracemalloc.start()
        start_time = time.perf_counter()
        
        try:
            text = func(path)
            text_len = len(text)
        except Exception as e:
            logger.error(f"{name} failed during run: {e}")
            tracemalloc.stop()
            return None
            
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        times.append(end_time - start_time)
        peak_memories.append(peak / (1024 * 1024)) # MB

    avg_time = statistics.mean(times)
    avg_mem = statistics.mean(peak_memories)
    
    return {
        "name": name,
        "time": avg_time,
        "memory": avg_mem,
        "text_len": text_len
    }

def main():
    pdf_path = Path("tests/test.pdf")
    if not pdf_path.exists():
        logger.error(f"Test file not found: {pdf_path}")
        return

    logger.info(f"Benchmarking with {pdf_path} (5 iterations)")
    logger.info("-" * 80)
    logger.info(f"{'Library':<25} | {'Time (s)':<10} | {'Memory (MB)':<12} | {'Text Len':<10}")
    logger.info("-" * 80)

    candidates = [
        ("pypdf", benchmark_pypdf),
        ("pdfminer.six", benchmark_pdfminer),
        ("pypdfium2", benchmark_pypdfium2),
    ]

    results = []
    for name, func in candidates:
        res = run_benchmark(name, func, pdf_path)
        if res:
            results.append(res)
            logger.info(f"{res['name']:<25} | {res['time']:<10.4f} | {res['memory']:<12.2f} | {res['text_len']:<10}")

    logger.info("-" * 80)

if __name__ == "__main__":
    main()
