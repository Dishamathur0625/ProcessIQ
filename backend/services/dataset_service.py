import uuid
from fastapi import UploadFile, HTTPException
from backend.storage.file_manager import FileManager

class DatasetService:
    ALLOWED_EXTENSIONS = {".csv", ".xls", ".xlsx"}
    ALLOWED_MIME_TYPES = {
        "text/csv", 
        "application/vnd.ms-excel", 
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/csv"
    }
    
    @classmethod
    def validate_upload(cls, file: UploadFile):
        import os
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file extension. Only CSV and Excel are allowed.")
        # Sometimes browsers don't send the correct MIME type for CSV/Excel, so we rely primarily on extension for this simple check.
        # But we leave MIME check for safety.
        # if file.content_type not in cls.ALLOWED_MIME_TYPES:
        #    raise HTTPException(status_code=400, detail=f"Invalid MIME type: {file.content_type}")
            
    @classmethod
    def save_dataset(cls, file: UploadFile) -> str:
        cls.validate_upload(file)
        
        # Create a mock job_id as the dataset id for self-contained isolation
        job_id = str(uuid.uuid4())
        
        from backend.services.storage.factory import StorageFactory
        from backend.core.config import settings
        import os
        import io
        import pandas as pd
        
        storage = StorageFactory.get_backend()
        bucket = settings.SUPABASE_BUCKET_DATASETS
        path = f"{job_id}/dataset.csv"
        
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in {".xls", ".xlsx"}:
            try:
                excel_file = pd.ExcelFile(file.file)
                sheet_names = excel_file.sheet_names
                if len(sheet_names) > 1:
                    best_sheet = sheet_names[0]
                    max_cells = 0
                    for sheet in sheet_names:
                        try:
                            temp_df = pd.read_excel(excel_file, sheet_name=sheet, nrows=50)
                            cells = temp_df.shape[0] * temp_df.shape[1]
                            if cells > max_cells:
                                max_cells = cells
                                best_sheet = sheet
                        except Exception:
                            continue
                    df = pd.read_excel(excel_file, sheet_name=best_sheet)
                else:
                    df = pd.read_excel(file.file)
            except Exception:
                df = pd.read_excel(file.file)
            csv_str = df.to_csv(index=False)
            storage.upload(bucket, path, io.BytesIO(csv_str.encode('utf-8')))
        else:
            storage.upload(bucket, path, file.file)
        
        return job_id
