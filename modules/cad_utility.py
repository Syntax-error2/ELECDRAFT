import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt


def convert_dxf_to_png(dxf_path, output_png_path):
    try:
        # 1. Load the DXF document
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()

        # 2. Set up the rendering context (handles colors/layers)
        ctx = RenderContext(doc)

        # 3. Create a Matplotlib figure
        fig = plt.figure(figsize=(20, 20))
        ax = fig.add_axes([0, 0, 1, 1])

        # 4. Use ezdxf's Frontend to draw onto Matplotlib
        out = MatplotlibBackend(ax)
        Frontend(ctx, out).draw_layout(msp, finalize=True)

        # 5. Save as PNG with high resolution for the canvas
        fig.savefig(output_png_path, dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        return True
    except Exception as e:
        print(f"CAD Conversion Error: {e}")
        return False