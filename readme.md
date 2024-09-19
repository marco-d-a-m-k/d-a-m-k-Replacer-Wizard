# d-a-m-k-replacer-wizard

The `d-a-m-k-replacer-wizard` is a GlyphsApp script designed to streamline the process of replacing glyphs in one font with those from another font. This script is particularly useful for type designers who need to transfer glyph designs between fonts while maintaining consistency in spacing and kerning groups.

## Features

-   **Glyph Replacement:** Replaces glyphs in the target font (Font A) with matching glyphs from the source font (Font B).
-   **Scaling:** Allows scaling of the transferred glyphs and their spacing according to a user-defined percentage.
-   **Spacing and Kerning:** Transfers and scales spacing values and transfers kerning groups from the source font to the target font, ensuring that the visual metrics are retained.
-   **Report Generation:** Generates a comprehensive report detailing:
    -   The total number of glyphs in the source font.
    -   Glyphs that were successfully transferred to the target font.
    -   Glyphs from the source font that were not replaced in the target font.

## Usage

1. Run the script in GlyphsApp.
2. Select the target font (Font A) and the source font (Font B).
3. Define the scaling percentage.
4. The script replaces matching glyphs, scales them, scales the spacing, and transfers spacing and kerning groups.
5. A report is generated on the desktop listing all changes made.

## Requirements

-   GlyphsApp
-   Two open fonts (one as the source and one as the target)

This script simplifies the process of transferring glyphs between fonts, saving time and ensuring accuracy in type design workflows, while also preserving the intended spacing through scalable adjustments.
