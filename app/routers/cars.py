from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services import car_counter

router = APIRouter(prefix="/cars", tags=["Cars Report"])

dataframe_store = {"df": None}  # In-memory storage for the uploaded data

@router.post("/upload")
def upload(file: UploadFile = File(...)):
    """Upload traffic car counter data with timestamp and car_count to store in-memory."""
    try:
        df = car_counter.read_data(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    if "timestamp" not in df.columns or "car_count" not in df.columns:
        raise HTTPException(status_code=400, detail="File must contain 'timestamp' and 'car_count' columns.")
    dataframe_store["df"] = df
    return {"message": f"File {file.filename} uploaded successfully", "rows": len(df)}

@router.get("/total-cars")
def total_cars():
    """Get the total number of cars seen."""
    df = dataframe_store["df"]
    if df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    total = car_counter.total_cars(df)
    return {"total_cars": int(total)}

@router.get("/cars-per-day")
def cars_per_day():
    """Get the total number of cars seen each day."""
    df = dataframe_store["df"]
    if df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    daily_counts = car_counter.cars_per_day(df)
    return {"cars_per_day": daily_counts}

@router.get("/top-n-half-hours")
def top_n_half_hours(n: int = 3):
    """Get the top N half-hours with the most car counts."""
    df = dataframe_store["df"]
    if df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    top_n = car_counter.top_n_half_hours(df, n)
    return {"top_n_half_hours": top_n}

@router.get("/least-n-contiguous-half-hours")
def least_n_contiguous_half_hours(n: int = 3):
    """Get the N contiguous half-hour records with the least car counts."""
    df = dataframe_store["df"]
    if df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    period, total = car_counter.least_n_contiguous_half_hours(df, n)
    return {"least_n_contiguous_half_hours": period, "total_cars": int(total)}
