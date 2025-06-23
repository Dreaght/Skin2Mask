# === mask_generator.py ===
import os
from PIL import Image, ImageDraw

# === CONFIG DEFAULTS ===
DPI = 300
A4_WIDTH_MM = 210
A4_HEIGHT_MM = 297
OVERLAP_MM = 15
MARKER_SIZE_PX = 15
FACE_WIDTH_MM = 185
FACE_HEIGHT_MM = 215
EDGE_THICKNESS_MM = 35
OUTER_SCALE_FACTOR = 1.125  # Approximate Minecraft outer layer scale


def mm_to_px(mm, dpi):
    return int(mm / 25.4 * dpi)

def extract_face_and_edges(skin_path, outer=False):
    skin = Image.open(skin_path).convert("RGBA")
    offset = 32 if outer else 0

    face = skin.crop((8 + offset, 8, 16 + offset, 16))
    top_edge = skin.crop((8 + offset, 7, 16 + offset, 8))
    bottom_edge = skin.crop((16 + offset, 7, 24 + offset, 8))
    left_edge = skin.crop((7 + offset, 8, 8 + offset, 16))
    right_edge = skin.crop((16 + offset, 8, 17 + offset, 16))
    return face, top_edge, bottom_edge, left_edge, right_edge

def build_scaled_mask(face, top, bottom, left, right, cfg, scale_factor=1.0):
    dpi = cfg['dpi']
    face_w = int(mm_to_px(cfg['face_width_mm'], dpi) * scale_factor)
    face_h = int(mm_to_px(cfg['face_height_mm'], dpi) * scale_factor)
    edge = int(mm_to_px(cfg['edge_thickness_mm'], dpi) * scale_factor)

    face = face.resize((face_w, face_h), Image.NEAREST)
    top = top.resize((face_w, edge), Image.NEAREST)
    bottom = bottom.resize((face_w, edge), Image.NEAREST)
    left = left.resize((edge, face_h), Image.NEAREST)
    right = right.resize((edge, face_h), Image.NEAREST)

    total_w = face_w + 2 * edge
    total_h = face_h + 2 * edge

    full_img = Image.new("RGBA", (total_w, total_h), (255, 255, 255, 0))
    full_img.paste(top, (edge, 0), top)
    full_img.paste(bottom, (edge, edge + face_h), bottom)
    full_img.paste(left, (0, edge), left)
    full_img.paste(right, (edge + face_w, edge), right)
    full_img.paste(face, (edge, edge), face)
    return full_img

def add_alignment_markers(draw, x, y, marker_size):
    draw.rectangle([x, y, x + marker_size, y + marker_size], fill="black")
    draw.rectangle([x + marker_size, y, x + 2 * marker_size, y + marker_size], fill="black")
    draw.rectangle([x, y + marker_size, x + marker_size, y + 2 * marker_size], fill="black")

def split_image_to_pages(mask_img, cfg):
    overlap_px = mm_to_px(cfg['overlap_mm'], cfg['dpi'])
    page_width = mm_to_px(cfg['a4_width_mm'], cfg['dpi'])
    page_height = mm_to_px(cfg['a4_height_mm'], cfg['dpi'])

    total_width, total_height = mask_img.size
    pages = []
    x = 0

    while x < total_width:
        crop_left = max(0, x - overlap_px)
        crop_right = min(total_width, x + page_width)

        region = mask_img.crop((crop_left, 0, crop_right, total_height))
        page = Image.new("RGB", (page_width, page_height), "white")
        offset_x = 0 if x == 0 else overlap_px
        offset_y = (page_height - total_height) // 2
        page.paste(region, (offset_x, offset_y))

        draw = ImageDraw.Draw(page)
        if x > 0:
            add_alignment_markers(draw, 10, 10, cfg['marker_size'])

        pages.append(page)
        x += page_width - overlap_px

    return pages

def save_pages_to_pdf(pages, output_path, dpi):
    pages[0].save(output_path, save_all=True, append_images=pages[1:], resolution=dpi)


def generate_mask_pdf(skin_path, output_pdf_path, cfg):
    # === Inner Layer ===
    face, top, bottom, left, right = extract_face_and_edges(skin_path, outer=False)
    inner_mask = build_scaled_mask(face, top, bottom, left, right, cfg)
    inner_pages = split_image_to_pages(inner_mask, cfg)

    # === Outer Layer ===
    oface, otop, obottom, oleft, oright = extract_face_and_edges(skin_path, outer=True)
    outer_mask = build_scaled_mask(oface, otop, obottom, oleft, oright, cfg, cfg['outer_scale_factor'])
    outer_pages = split_image_to_pages(outer_mask, cfg)

    all_pages = inner_pages + outer_pages
    save_pages_to_pdf(all_pages, output_pdf_path, cfg['dpi'])

    return output_pdf_path