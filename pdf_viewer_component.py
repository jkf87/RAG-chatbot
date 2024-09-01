import streamlit.components.v1 as components
import os

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "pdf_viewer",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("pdf_viewer", path=build_dir)

def pdf_viewer(pdf_base64, initial_page=1, key=None):
    component_value = _component_func(pdfBase64=pdf_base64, initialPage=initial_page, key=key, default=initial_page)
    return component_value