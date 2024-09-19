# MenuTitle: d-a-m-k-replacer-wizard
# -*- coding: utf-8 -*-
__doc__ = """
Replaces all matching glyphs from Font B in Font A, scales them by a percentage, resets kerning, and transfers spacing values and kerning groups from the original glyphs of Font A. Generates a report file on the desktop with changed letters.
"""

import GlyphsApp
import objc
from AppKit import NSApp, NSAlert, NSTextField, NSPopUpButton, NSView, NSPoint
import os
from datetime import datetime

class DAMKReplacerWizard(object):
    def __init__(self):
        self.font_a = None
        self.font_b = None
        self.scale_percentage = 100.0
        self.changed_letters = []
        self.unchanged_letters = []

    def showUI(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("d-a-m-k-replacer-wizard")
        alert.setInformativeText_("Select (1) the target font and (2) the source font from the opened fonts. The source font will replace the glyphs in the target font. In the box, select the scale factor.")
        alert.addButtonWithTitle_("Run")
        alert.addButtonWithTitle_("Cancel")

        font_a_popup = NSPopUpButton.alloc().initWithFrame_(((0, 60), (200, 25)))
        font_b_popup = NSPopUpButton.alloc().initWithFrame_(((0, 30), (200, 25)))

        open_fonts = Glyphs.fonts
        for font in open_fonts:
            font_a_popup.addItemWithTitle_(font.familyName)
            font_b_popup.addItemWithTitle_(font.familyName)

        scale_input = NSTextField.alloc().initWithFrame_(((0, 0), (100, 24)))
        scale_input.setStringValue_("100.0")

        custom_view = NSView.alloc().initWithFrame_(((0, 0), (200, 90)))
        custom_view.addSubview_(font_a_popup)
        custom_view.addSubview_(font_b_popup)
        custom_view.addSubview_(scale_input)
        alert.setAccessoryView_(custom_view)

        response = alert.runModal()

        if response == 1000:  # NSAlertFirstButtonReturn
            self.font_a = open_fonts[font_a_popup.indexOfSelectedItem()]
            self.font_b = open_fonts[font_b_popup.indexOfSelectedItem()]
            self.scale_percentage = float(scale_input.stringValue())
            self.run()

    def matchGlyphs(self, font_a, font_b):
        glyphs_in_a = [glyph.name for glyph in font_a.glyphs]
        glyphs_in_b = [glyph.name for glyph in font_b.glyphs]
        return [glyph_name for glyph_name in glyphs_in_a if glyph_name in glyphs_in_b]

    def replaceAndScaleGlyph(self, glyph_a, glyph_b, scale_factor):
        layer_a = glyph_a.layers[0]  # Assuming default layer
        layer_b = glyph_b.layers[0]  # Assuming default layer

        # Save spacing and kerning groups from the new glyph (font_b)
        new_spacing = (layer_b.LSB * scale_factor, layer_b.RSB * scale_factor)
        new_left_group = glyph_b.leftKerningGroup
        new_right_group = glyph_b.rightKerningGroup

        # Clear existing content in the target layer
        layer_a.paths = []
        layer_a.components = []
        
        # Define the scaling function
        def scalePath(path, scale_factor, origin):
            for node in path.nodes:
                node.position = NSPoint(
                    origin.x + (node.position.x - origin.x) * scale_factor,
                    origin.y + (node.position.y - origin.y) * scale_factor
                )
        
        # Compute the baseline to top scaling origin
        origin = NSPoint(0, 0)
        
        # Scale paths
        for path in layer_b.paths:
            new_path = path.copy()
            scalePath(new_path, scale_factor, origin)
            layer_a.paths.append(new_path)

        # Scale components
        for component in layer_b.components:
            new_component = component.copy()
            # Scale component position
            new_component.position = NSPoint(
                origin.x + (component.position.x - origin.x) * scale_factor,
                origin.y + (component.position.y - origin.y) * scale_factor
            )
            new_component.scale = component.scale * scale_factor  # Adjust scale
            layer_a.components.append(new_component)

        # Scale anchors
        layer_a.anchors = []
        for anchor in layer_b.anchors:
            new_anchor = GSAnchor(anchor.name, NSPoint(
                origin.x + (anchor.position.x - origin.x) * scale_factor,
                origin.y + (anchor.position.y - origin.y) * scale_factor
            ))
            layer_a.anchors.append(new_anchor)

        # Apply scaled spacing from the new glyph (font_b)
        layer_a.LSB, layer_a.RSB = new_spacing

        # Apply kerning groups from the new glyph (font_b)
        glyph_a.leftKerningGroup = new_left_group
        glyph_a.rightKerningGroup = new_right_group

        # Add the changed glyph to the list
        self.changed_letters.append(glyph_a.name)

    def generateReport(self):
        desktop_path = os.path.expanduser("~/Desktop")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = "d-a-m-k-replacer-report_{}.txt".format(timestamp)
        report_path = os.path.join(desktop_path, report_filename)

        with open(report_path, 'w') as report_file:
            report_file.write("d-a-m-k-replacer-wizard Report\n")
            report_file.write("Generated on: {}\n\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            report_file.write("Target Font: {}\n".format(self.font_a.familyName))
            report_file.write("Source Font: {}\n".format(self.font_b.familyName))
            report_file.write("Scale Percentage: {}%\n\n".format(self.scale_percentage))
            report_file.write("Total Glyphs in Source Font: {}\n\n".format(len(self.font_b.glyphs)))
            
            report_file.write("Changed Letters ({}):\n".format(len(self.changed_letters)))
            for letter in sorted(self.changed_letters):
                report_file.write("- {}\n".format(letter))

            report_file.write("\nUnchanged Letters ({}):\n".format(len(self.unchanged_letters)))
            for letter in sorted(self.unchanged_letters):
                report_file.write("- {}\n".format(letter))

        return report_path


    def run(self):
        if not self.font_a or not self.font_b:
            NSApp.displayDialog_withTitle_("Please select both fonts.", "Error")
            return

        matching_glyphs = self.matchGlyphs(self.font_a, self.font_b)

        if not matching_glyphs:
            NSApp.displayDialog_withTitle_("No matching glyphs found.", "Error")
            return

        self.font_a.disableUpdateInterface()

        try:
            scale_factor = self.scale_percentage / 100.0

            # Reset kerning for font_a
            self.font_a.kerning.clear()

            # Iterate over glyphs in Font B
            for glyph_b in self.font_b.glyphs:
                glyph_name = glyph_b.name
                if glyph_name in matching_glyphs:
                    glyph_a = self.font_a.glyphs[glyph_name]
                    self.replaceAndScaleGlyph(glyph_a, glyph_b, scale_factor)
                else:
                    self.unchanged_letters.append(glyph_name)

            report_path = self.generateReport()
            NSApp.displayDialog_withTitle_("Replacement completed, Spacing added, Kerning groups added, Kerning not added. Report saved at: {}".format(report_path), "Success")
        except Exception as e:
            NSApp.displayDialog_withTitle_(str(e), "Error during execution")
        finally:
            self.font_a.enableUpdateInterface()

# Create and run the wizard
wizard = DAMKReplacerWizard()
wizard.showUI()
