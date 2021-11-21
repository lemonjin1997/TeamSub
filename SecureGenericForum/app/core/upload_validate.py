import imghdr
from flask import abort
from werkzeug.utils import secure_filename
from os import path
from ..app import app

def image_validation(image_file) -> bool:
    
    # Check if field is empty
    if image_file.filename != '':
        
        # Check if extension is correct
        image_filename = secure_filename(image_file.filename)
        file_ext = path.splitext(image_filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            
            return False

        # Check for malious content in the image
        header = image_file.stream.read(512)
        image_file.stream.seek(0) 
        format = imghdr.what(None, header)
        if '.' + str(format) not in app.config['UPLOAD_EXTENSIONS']:
            return False

        if image_file.tell() > app.config['MAX_UPLOAD_SIZE']:
            return False

        # Save image if all checks pass
        #image_file.save(path.join(app.config['UPLOAD_PATH'], image_filename))
        
        return True

    return False

    
    