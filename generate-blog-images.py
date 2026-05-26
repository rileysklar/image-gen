"""
Batch image generator for the riley-portfolio blog (OpenAI gpt-image-1).

Reads every Markdown file in riley-portfolio/src/content/blog/, builds a
topic-tailored prompt in the site's pastel-reskin style, generates a
1536x1024 header image per entry, compresses it to WebP via Pillow, saves
to public/assets/blog/<slug>.webp, and rewrites the entry's frontmatter
`img:` field to point at the new file.

Run `python3 generate-blog-images.py` for a dry run (prompts only, no API
calls, no file writes). Run with `--go` to actually generate and rewire.
Add `--only <slug>` to limit to one entry.
"""

import argparse
import base64
import io
import os
import re
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

load_dotenv()

PORTFOLIO = Path("/Users/rileysklar/Code/riley-portfolio")
BLOG_DIR = PORTFOLIO / "src/content/blog"
IMG_OUT_DIR = PORTFOLIO / "public/assets/blog"

STYLE_PREAMBLE = (
    "Editorial blog header illustration in a soft pastel palette of sage "
    "green, dusty rose, lavender, and warm clay. Minimal, abstract, "
    "geometric composition with gentle gradients, flat shapes, and subtle "
    "paper grain. Wide cinematic 16:9 composition with generous negative "
    "space. No text, no logos, no human figures, no UI screenshots."
)

# Per-slug subject lines. Slug = filename without .md.
SUBJECTS = {
    "costa-rica-to-code": (
        "Soft tropical motifs — gentle palm silhouettes and a low horizon "
        "line — transitioning into terminal-window panels and code-bracket "
        "glyphs, connected by a single flowing curved path."
    ),
    "framework-integration": (
        "Two large pastel rounded rectangles interlocking like puzzle "
        "pieces, with delicate connection nodes and thin lines suggesting "
        "two technical systems clicking into one."
    ),
    "mastering-react": (
        "Concentric orbiting rings around a soft central node, with smaller "
        "satellite nodes on the rings — an atom-like composition suggesting "
        "a component tree without any literal logos."
    ),
    "rip-noaa": (
        "A pastel weather-radar sweep dissolving into negative space, "
        "isobar lines fading at the edges — a quiet sense of disappearing "
        "public infrastructure."
    ),
    "software-developer-journey": (
        "A winding pastel path threading upward through abstract layered "
        "terrain, with small geometric beacons marking milestones along "
        "the way."
    ),
    "versatile-developer": (
        "A stylized pen-nib and a stylized gear overlapping into a single "
        "merged silhouette, balanced against a wash of pastel color — "
        "designer and engineer as one shape."
    ),
    "gpt-image-1-batch-script": (
        "A soft pastel 2x3 grid of six abstract rectangular tiles in "
        "different gentle hues — sage, dusty rose, lavender, clay, lilac, "
        "warm peach — connected by thin delicate curving lines that "
        "converge from a single small node, suggesting one source "
        "producing many outputs in a batch."
    ),
}


def parse_frontmatter(text):
    """Return (frontmatter_dict, body, raw_yaml_str) or raise ValueError."""
    if not text.startswith("---"):
        raise ValueError("missing frontmatter")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("malformed frontmatter")
    raw_yaml = match.group(1)
    body = match.group(2)
    data = yaml.safe_load(raw_yaml)
    return data, body, raw_yaml


def build_prompt(slug, frontmatter):
    subject = SUBJECTS.get(slug)
    if not subject:
        # Fallback: derive from description.
        subject = (
            f"An abstract editorial composition evoking: "
            f"{frontmatter.get('description', frontmatter.get('title', slug))}"
        )
    return f"{STYLE_PREAMBLE} Subject: {subject}"


def rewrite_img_field(md_path, new_img_path):
    """Rewrite the `img:` field in a Markdown file's frontmatter."""
    text = md_path.read_text()
    new = re.sub(
        r"^(img:\s*).*$",
        rf"\1{new_img_path}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    md_path.write_text(new)


def save_b64_as_webp_and_jpg(b64_str, webp_dest, quality=85):
    """Decode base64 PNG bytes and write both a WebP (page visual, ~10x smaller
    than the source PNG) and a JPEG sibling (for OG/Twitter unfurls — those
    scrapers reject WebP)."""
    raw = base64.b64decode(b64_str)
    with Image.open(io.BytesIO(raw)) as im:
        im.save(webp_dest, "WEBP", quality=quality, method=6)
        jpg_dest = webp_dest.with_suffix(".jpg")
        im.convert("RGB").save(
            jpg_dest, "JPEG", quality=quality, optimize=True, progressive=True
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--go",
        action="store_true",
        help="Actually call the API and write files. Default is dry-run.",
    )
    parser.add_argument(
        "--only",
        help="Only process this slug (filename without .md).",
    )
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if args.go and not api_key:
        print("ERROR: OPENAI_API_KEY not set in environment / .env")
        sys.exit(1)
    client = OpenAI(api_key=api_key) if args.go else None

    md_files = sorted(BLOG_DIR.glob("*.md"))
    if args.only:
        md_files = [p for p in md_files if p.stem == args.only]
        if not md_files:
            print(f"No entry found with slug '{args.only}'")
            sys.exit(1)

    if args.go:
        IMG_OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"{'GENERATE' if args.go else 'DRY-RUN'}: {len(md_files)} entries\n")

    successes = 0
    for md in md_files:
        slug = md.stem
        try:
            data, _, _ = parse_frontmatter(md.read_text())
        except ValueError as exc:
            print(f"SKIP {slug}: {exc}")
            continue

        prompt = build_prompt(slug, data)
        print(f"--- {slug} ---")
        print(f"  title : {data.get('title','')[:80]}")
        print(f"  prompt: {prompt}")

        if not args.go:
            print()
            continue

        try:
            resp = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                n=1,
                size="1536x1024",
                quality="high",
            )
            b64 = resp.data[0].b64_json
            out_path = IMG_OUT_DIR / f"{slug}.webp"
            save_b64_as_webp_and_jpg(b64, out_path)
            rel = f"/assets/blog/{slug}.webp"
            rewrite_img_field(md, rel)
            print(f"  -> saved {out_path}")
            print(f"  -> frontmatter img: {rel}\n")
            successes += 1
        except Exception as exc:
            print(f"  !! FAILED: {exc}\n")

    if args.go:
        print(f"\nDone. {successes}/{len(md_files)} succeeded.")
        # gpt-image-1 high-quality landscape ~ $0.17 / image (token-priced).
        print(f"Estimated cost: ~${successes * 0.17:.2f}")
    else:
        print("Dry-run complete. Re-run with --go to actually generate.")


if __name__ == "__main__":
    main()
