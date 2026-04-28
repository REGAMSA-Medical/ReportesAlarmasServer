from app.decorators.common import handle_exceptions

@handle_exceptions
async def upload_media_file(file: UploadFile) -> str:
    """
    Save uploaded file to the media directory organized by file type.
    This function accepts an uploaded file, determines its type based on MIME type,
    saves it to the appropriate subdirectory (images, audios, documents, videos, other),
    and returns the relative file path.
    """
    # Define media directory path (project root level)
    media_dir = Path("media")
    
    # Create media directory if it doesn't exist
    media_dir.mkdir(exist_ok=True)
    
    # Determine file type based on MIME type
    mime_type = file.content_type or ""
    
    if mime_type.startswith("image/"):
        subdir = "images"
    elif mime_type.startswith("audio/"):
        subdir = "audios"
    elif mime_type.startswith("video/"):
        subdir = "videos"
    elif mime_type in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                       "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                       "text/plain", "application/json"]:
        subdir = "documents"
    else:
        subdir = "other"
    
    # Create subdirectory if it doesn't exist
    subdir_path = media_dir / subdir
    subdir_path.mkdir(exist_ok=True)
    
    # Generate unique filename to avoid collisions
    import uuid
    from datetime import datetime
    
    # Get file extension
    file_extension = Path(file.filename).suffix if file.filename else ""
    
    # Create unique filename: timestamp_uuid.extension
    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
    
    # Define full file path
    file_path = subdir_path / unique_filename
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return relative path from project root
    return str(file_path)
        
    