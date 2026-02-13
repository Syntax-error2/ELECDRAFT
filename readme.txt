===============================================================================
                ELECDRAFT PRO - PROFESSIONAL ELECTRICAL CAD
                    Load Schedule & Layout Automation
===============================================================================

Welcome to ELECDRAFT PRO, a specialized CAD tool designed for electrical
engineers and designers. This application streamlines electrical layouts,
automates Philippine Electrical Code (PEC) calculations, and generates
Single Line Diagrams (SLD) instantly.

-------------------------------------------------------------------------------
1. NAVIGATION & CONTROLS
-------------------------------------------------------------------------------

Use standard CAD-style controls to navigate your workspace:

ACTION          | CONTROL                    | DESCRIPTION
----------------|----------------------------|---------------------------------
Pan View        | Middle Mouse (Hold & Drag) | Move the canvas (AutoCAD style).
Zoom            | Mouse Wheel (Scroll)       | Zoom in/out of the floor plan.
Select          | Left Click                 | Select items to view properties.
Context Menu    | Right Click                | Copy, Paste, Delete, or Edit.
Multi-Select    | Ctrl + Click               | Select multiple items at once.
Delete          | Delete Key                 | Remove selected items.

-------------------------------------------------------------------------------
2. GETTING STARTED
-------------------------------------------------------------------------------

A. IMPORTING A FLOOR PLAN (Ctrl + I)
   - Supports .dxf, .dwg (via LibreCAD) and images (.png, .jpg, .tiff).
   - Dark lines (walls) are detected as obstacles for auto-wire routing.

B. PLACING COMPONENTS
   - Use the 'Component Toolbox' on the left.
   - Click a category (e.g., LIGHTING) and select a component.
   - Drag and drop components directly onto the floor plan.

C. WIRING & CIRCUITS
   - Click [DRAW CIRCUIT] at the bottom.
   - Click the Source (Switch/Panel) then the Destination (Light/Outlet).
   - Wires route automatically around walls.
   - PRO TIP: Connect a circuit to a Panelboard to create a "Homerun."

-------------------------------------------------------------------------------
3. CORE FEATURES
-------------------------------------------------------------------------------

PROJECT NAVIGATION (Left Sidebar)
   - Dynamic tree view that groups components by circuit/feeder.
   - Automatically creates sub-folders for "Homeruns" for easy management.

CUSTOM LIBRARY
   - Import custom .svg or .png files via File > Import Custom Symbol.
   - Custom items are added to the "CUSTOM" category in your toolbox.

PEC CALCULATIONS (Right Sidebar)
   - Select a component to edit its Power (VA).
   - System automatically calculates: Amps, Wire Size (e.g. 3.5mm),
     Breaker Rating, and Voltage Drop.

-------------------------------------------------------------------------------
4. ANALYSIS & EXPORTS
-------------------------------------------------------------------------------



[Image of an electrical single line diagram]


> REAL-TIME LOAD SCHEDULE: Table at the bottom updates live.
> EXPORT TO EXCEL: Save formatted .xlsx files for professional submission.
> GEN SLD: Instantly generate a Single Line Diagram schematic.
> 3D VIEW: View layouts in isometric 3D; component height varies by load.

-------------------------------------------------------------------------------
5. KEYBOARD SHORTCUTS
-------------------------------------------------------------------------------

SHORTCUT      | ACTION
--------------|----------------------------------------------------------------
Ctrl + S      | Save Project
Ctrl + Z      | Undo
Ctrl + Y      | Redo
Ctrl + C      | Copy
Ctrl + V      | Paste
Ctrl + D      | Duplicate
Ctrl + P      | Plot to PDF
===============================================================================