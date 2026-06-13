import streamlit as st
from PIL import Image
import io
import os

# --- Page Configuration ---
st.set_page_config(page_title="Universal File Converter", page_icon="🔄", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- Header ---
st.title("🔄 Universal File Converter")
st.write("Convert images between multiple formats instantly!")

# --- Sidebar ---
st.sidebar.header("📁 Supported Formats")

st.sidebar.subheader("Input Formats")
st.sidebar.write("""
- JPG / JPEG
- PNG
- BMP
- WEBP
- TIFF
- GIF
- ICO
- HEIC (Apple)
""")

st.sidebar.subheader("Output Formats")
st.sidebar.write("""
- JPG / JPEG
- PNG
- BMP
- WEBP
- TIFF
- GIF
- ICO
- PDF
- HEIC
""")

# --- Main App Logic ---
def convert_image(image_file, target_format):
    """
    Converts the uploaded image to the target format.
    """
    try:
        # Open the uploaded image
        img = Image.open(image_file)
        
        # Determine original format
        original_format = img.format if img.format else "UNKNOWN"
        
        # Handle different image modes based on target format
        if target_format.upper() in ["JPG", "JPEG"]:
            # Convert RGBA, LA, P to RGB for JPG
            if img.mode in ("RGBA", "LA", "P"):
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode == "RGBA":
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert("RGB")
            elif img.mode == "L":
                img = img.convert("RGB")
                
        elif target_format.upper() in ["TIFF", "TIF"]:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
                
        elif target_format.upper() == "GIF":
            if img.mode not in ("L", "P", "RGB"):
                img = img.convert("RGB")
                
        elif target_format.upper() == "BMP":
            if img.mode not in ("L", "P", "RGB"):
                img = img.convert("RGB")
                
        elif target_format.upper() == "ICO":
            if img.size[0] > 256 or img.size[1] > 256:
                img.thumbnail((256, 256), Image.Resampling.LANCZOS)
            if img.mode not in ("L", "P", "RGB"):
                img = img.convert("RGB")
        
        elif target_format.upper() == "WEBP":
            if img.mode not in ("RGB", "RGBA", "L"):
                img = img.convert("RGB")
        
        elif target_format.upper() == "HEIC":
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
        
        # Save kwargs based on format
        save_kwargs = {}
        if target_format.upper() in ["JPG", "JPEG"]:
            save_kwargs['quality'] = 95
            save_kwargs['optimize'] = True
        elif target_format.upper() == "WEBP":
            save_kwargs['quality'] = 95
            save_kwargs['method'] = 6
        elif target_format.upper() == "TIFF":
            save_kwargs['compression'] = 'tiff_deflate'
        
        # Handle PDF conversion
        if target_format.upper() == "PDF":
            try:
                import img2pdf
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                pdf_bytes = img2pdf.convert(img_byte_arr.read())
                return io.BytesIO(pdf_bytes), img.size
            except ImportError:
                st.error("PDF conversion not available. Please install img2pdf.")
                return None, None
        
        # Save to a bytes buffer
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=target_format.upper(), **save_kwargs)
        img_byte_arr.seek(0)
        
        return img_byte_arr, img.size
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None, None

# --- Supported formats list ---
supported_formats = ["PNG", "JPG", "BMP", "WEBP", "TIFF", "GIF", "ICO", "PDF", "HEIC"]

# --- File Uploader ---
uploaded_file = st.file_uploader("📤 Upload an image...", 
    type=["png", "jpg", "jpeg", "bmp", "webp", "tiff", "tif", "gif", "ico", "heic"])

if uploaded_file is not None:
    # 1. Show file details
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**📄 Filename:** {uploaded_file.name}")
    with col2:
        st.info(f"**📊 Size:** {uploaded_file.size / 1024:.2f} KB")

    # 2. Show preview
    st.image(uploaded_file, caption="👁️ Preview", use_column_width=True)

    # 3. Select Target Format
    st.subheader("⚙️ Conversion Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        target_format = st.selectbox(
            "Select target format:",
            supported_formats
        )
    
    # 4. Convert Button
    if st.button("🔄 Convert File", type="primary"):
        # Check if same format
        original_ext = uploaded_file.name.split('.')[-1].lower()
        target_ext = target_format.lower()
        
        if target_format == "PDF":
            target_ext = "pdf"
        
        if original_ext == target_ext:
            st.warning("⚠️ Target format is the same as original!")
        else:
            with st.spinner("⏳ Converting..."):
                result = convert_image(uploaded_file, target_format)
                
                if result[0] is not None:
                    converted_data = result[0]
                    
                    st.success("✅ Conversion Successful!")
                    
                    # Generate new filename
                    new_filename = uploaded_file.name.rsplit('.', 1)[0] + f".{target_ext}"
                    
                    # Determine MIME type
                    mime_types = {
                        "png": "image/png",
                        "jpg": "image/jpeg",
                        "jpeg": "image/jpeg",
                        "bmp": "image/bmp",
                        "webp": "image/webp",
                        "tiff": "image/tiff",
                        "tif": "image/tiff",
                        "gif": "image/gif",
                        "ico": "image/x-icon",
                        "heic": "image/heic",
                        "pdf": "application/pdf"
                    }
                    mime = mime_types.get(target_ext, "application/octet-stream")
                    
                    # Download Button
                    st.download_button(
                        label="⬇️ Download Converted File",
                        data=converted_data,
                        file_name=new_filename,
                        mime=mime,
                        type="primary"
                    )
                    
                    st.balloons()