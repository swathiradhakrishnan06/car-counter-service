from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from app.services import car_counter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TrafficData

router = APIRouter(prefix="/cars", tags=["Cars Report"])

dataframe_store = {"df": None}  # In-memory storage for the uploaded data

@router.post("/upload")
def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload traffic car counter data with timestamp and car_count to store in-memory."""
    try:
        df = car_counter.read_data(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    if "timestamp" not in df.columns or "car_count" not in df.columns:
        raise HTTPException(status_code=400, detail="File must contain 'timestamp' and 'car_count' columns.")
    dataframe_store["df"] = df

    # Insert into DB
    try:
        for _, row in df.iterrows():
            db_row = TrafficData(timestamp=row["timestamp"], car_count=row["car_count"])
            db.add(db_row)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error inserting into DB: {str(e)}")
    
    return {"message": f"File {file.filename} uploaded successfully", "rows": len(df)}

@router.get("/total-cars")
def total_cars(use_db: bool = Query(False, description="Use DB instead of in-memory DataFrame"), db: Session = Depends(get_db)):
    """Get the total number of cars seen."""
    df = dataframe_store["df"]
    if not use_db and df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    total = car_counter.total_cars(df=df, db=db, use_db=use_db)
    return {"total_cars": int(total)}

@router.get("/cars-per-day")
def cars_per_day(use_db: bool = Query(False, description="Use DB instead of in-memory DataFrame"), db: Session = Depends(get_db)):
    """Get the total number of cars seen each day."""
    df = dataframe_store["df"]
    if not use_db and df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    daily_counts = car_counter.cars_per_day(df=df, db=db, use_db=use_db)
    return {"cars_per_day": daily_counts}

@router.get("/top-n-half-hours")
def top_n_half_hours(n: int = 3,
    use_db: bool = Query(False, description="Use DB instead of in-memory DataFrame"),
    db: Session = Depends(get_db)):
    """Get the top N half-hours with the most car counts."""
    df = dataframe_store["df"]
    if not use_db and df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    top_n = car_counter.top_n_half_hours(df=df, n=n, db=db, use_db=use_db)
    return {"top_n_half_hours": top_n}

@router.get("/least-n-contiguous-half-hours")
def least_n_contiguous_half_hours(n: int = 3,
    use_db: bool = Query(False, description="Use DB instead of in-memory DataFrame"),
    db: Session = Depends(get_db)):
    """Get the N contiguous half-hour records with the least car counts."""
    df = dataframe_store["df"]
    if not use_db and df is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    period, total = car_counter.least_n_contiguous_half_hours(df=df, n=n, db=db, use_db=use_db)
    return {"least_n_contiguous_half_hours": period, "total_cars": int(total)}
