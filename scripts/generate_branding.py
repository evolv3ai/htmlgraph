#!/usr/bin/env python3
"""
Generate HtmlGraph branding assets using Gemini image generation.

Requirements:
    pip install google-genai

Usage:
    source .env && python scripts/generate_branding.py
"""

import mimetypes
import os
from pathlib import Path

from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    """Save binary data to file."""
    # Ensure directory exists
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)

    with open(file_name, "wb") as f:
        f.write(data)
    print(f"✓ File saved to: {file_name}")


def generate_image(client, model, prompt, file_base_name):
    """Generate image from prompt and save to file."""
    print(f"\n🎨 Generating: {file_base_name}")
    print(f"   Prompt: {prompt[:80]}...")

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    tools = [
        types.Tool(googleSearch=types.GoogleSearch()),
    ]

    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(
            image_size="1K",
        ),
        tools=tools,
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue

        if (chunk.candidates[0].content.parts[0].inline_data and
            chunk.candidates[0].content.parts[0].inline_data.data):

            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)

            file_name = f"{file_base_name}{file_extension}"
            save_binary_file(file_name, data_buffer)
            file_index += 1
        else:
            if chunk.text:
                print(f"   {chunk.text}")


def generate_all_assets():
    """Generate all HtmlGraph branding assets."""
    # Initialize client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment")
        print("   Run: source .env")
        return

    client = genai.Client(api_key=api_key)
    model = "gemini-3-pro-image-preview"

    # Create assets directory
    assets_dir = Path("docs/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🌟 HtmlGraph Branding Asset Generator")
    print("=" * 70)

    # Asset definitions with prompts
    assets = [
        {
            "name": "main_logo",
            "file": "docs/assets/logo",
            "prompt": """Create a modern, minimalist logo for "HtmlGraph" - a graph database built on HTML.

Design requirements:
- Style: Terminal chic, technical, developer-focused
- Color: Electric lime green (#CDFF00) on deep charcoal/black background
- Elements: Incorporate HTML tag brackets < > with graph nodes/edges
- Typography: Monospace font, clean and bold
- Format: Square icon suitable for favicons and documentation
- Aesthetic: Matrix-style, cyberpunk, minimal but distinctive

The logo should convey:
- Web standards (HTML)
- Graph database (connected nodes)
- Developer tool (technical, clean)
- "HTML is All You Need" philosophy

Make it iconic and memorable with strong geometric shapes."""
        },
        {
            "name": "favicon",
            "file": "docs/assets/favicon",
            "prompt": """Create a small, simple favicon icon for "HtmlGraph".

Design requirements:
- Size: Optimized for 32x32 pixels (simple, bold shapes)
- Color: Electric lime (#CDFF00) symbol on black/dark charcoal background
- Symbol: Stylized HTML angle brackets < > forming a graph node
- Style: Minimal, high contrast, instantly recognizable at small sizes
- Format: Clean edges, no gradients, flat design

The icon should be simple enough to recognize at favicon size (16x16 to 32x32 pixels) while still being distinctive."""
        },
        {
            "name": "graph_illustration",
            "file": "docs/assets/graph-hero",
            "prompt": """Create an abstract illustration of a graph database for HtmlGraph documentation hero section.

Design requirements:
- Style: Abstract, technical, modern
- Color scheme: Electric lime (#CDFF00) lines/nodes on deep charcoal (#151518) background
- Elements: Network of connected nodes with HTML tag motifs
- Composition: Geometric graph structure with flowing connections
- Aesthetic: Terminal/matrix style with glowing effects
- Format: Horizontal banner suitable for hero section

Show a beautiful graph structure with:
- Glowing lime nodes (circles)
- Flowing lime connections (edges)
- HTML elements (< >, code snippets) subtly integrated
- Sense of data flow and interconnection
- Clean, modern, developer-focused aesthetic"""
        },
        {
            "name": "touch_icon",
            "file": "docs/assets/apple-touch-icon",
            "prompt": """Create an Apple touch icon for HtmlGraph (used on iOS home screens).

Design requirements:
- Size: Square, suitable for iOS/Android home screens (180x180+)
- Background: Solid deep charcoal or black
- Icon: Bold, centered HtmlGraph symbol in electric lime (#CDFF00)
- Symbol: HTML brackets < > with graph node in center
- Style: Clean, modern, high contrast
- Padding: Small margin around edges for iOS rounded corners

The icon should look great on both light and dark backgrounds when rounded by iOS."""
        }
    ]

    # Generate each asset
    for asset in assets:
        try:
            generate_image(
                client=client,
                model=model,
                prompt=asset["prompt"],
                file_base_name=asset["file"]
            )
        except Exception as e:
            print(f"❌ Error generating {asset['name']}: {e}")
            continue

    print("\n" + "=" * 70)
    print("✅ Asset generation complete!")
    print("=" * 70)
    print("\nGenerated files in docs/assets/:")
    print("  - logo.*              (Main logo)")
    print("  - favicon.*           (Favicon)")
    print("  - graph-hero.*        (Hero illustration)")
    print("  - apple-touch-icon.*  (iOS/Android icon)")
    print("\nNext steps:")
    print("  1. Review generated images")
    print("  2. Update mkdocs.yml with asset paths")
    print("  3. Add hero illustration to index.md")
    print("  4. Commit new assets")


if __name__ == "__main__":
    generate_all_assets()
