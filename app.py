from judici.application.settings import secrets
from chalicelib.judici.fileLoaders.pdf import ReaderPdf
from chalice import Chalice
import json

app = Chalice(
    app_name="judicial-service-events",
    configure_logs=True
)

app.debug = True
S3_BUCKET = secrets.app_bucket_name

@app.on_s3_event(
    bucket=S3_BUCKET,
    events=['s3:ObjectCreated:*']
)
def s3_handler(event): 
    try:
        file = ReaderPdf(keyFile=event.key)
        file.extract_images_to_bucket()
        
        return {
            "status": "success",
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        app.log.error(e)
        return {
            "status": "error",
            "message": "An error occurred"
        }
    